# modules/url_analyzer.py
"""
Analyze YouTube / TikTok videos by URL.
Downloads audio with yt-dlp, transcribes with Groq Whisper,
then runs the full script + visual analysis pipeline.
"""

import os
import re
import json
import tempfile
import subprocess

# ── yt-dlp helpers ────────────────────────────────────────────────────────────

def _ytdlp_available() -> bool:
    try:
        result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False


def get_video_metadata(url: str) -> dict:
    """Fetch video title, description, duration, view count without downloading."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-playlist", url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return {"error": result.stderr[:300]}
        data = json.loads(result.stdout)
        return {
            "title": data.get("title", "Unknown"),
            "uploader": data.get("uploader", "Unknown"),
            "duration": data.get("duration", 0),
            "view_count": data.get("view_count", 0),
            "like_count": data.get("like_count", 0),
            "description": (data.get("description") or "")[:1000],
            "upload_date": data.get("upload_date", ""),
            "platform": data.get("extractor_key", "Unknown"),
            "thumbnail": data.get("thumbnail", ""),
            "tags": data.get("tags", [])[:10],
            "categories": data.get("categories", []),
        }
    except Exception as e:
        return {"error": str(e)}


def download_audio(url: str, output_dir: str) -> str:
    """Download best audio from URL as mp3. Returns file path."""
    output_template = os.path.join(output_dir, "audio.%(ext)s")
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--extract-audio",
                "--audio-format", "mp3",
                "--audio-quality", "128K",
                "--no-playlist",
                "--max-filesize", "50m",
                "-o", output_template,
                url
            ],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            return None
        # Find the output file
        for f in os.listdir(output_dir):
            if f.startswith("audio") and f.endswith(".mp3"):
                return os.path.join(output_dir, f)
        return None
    except Exception:
        return None


def transcribe_audio(groq_client, audio_path: str) -> str:
    """Transcribe audio file using Groq Whisper."""
    try:
        with open(audio_path, "rb") as f:
            transcription = groq_client.audio.transcriptions.create(
                file=(os.path.basename(audio_path), f.read()),
                model="whisper-large-v3",
                response_format="text"
            )
        return transcription
    except Exception as e:
        return f"[Transcription failed: {e}]"


def analyze_url(groq_client, url: str) -> dict:
    """
    Full pipeline for URL analysis:
    1. Fetch metadata
    2. Download audio
    3. Transcribe
    4. Return all data for script analysis
    """
    results = {
        "url": url,
        "metadata": {},
        "transcription": "",
        "error": None
    }

    if not _ytdlp_available():
        results["error"] = "yt-dlp is not installed. Run: pip install yt-dlp"
        return results

    # Step 1: Metadata
    meta = get_video_metadata(url)
    if "error" in meta:
        results["error"] = f"Could not fetch video: {meta['error']}"
        return results
    results["metadata"] = meta

    # Step 2 & 3: Audio download + transcribe
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = download_audio(url, tmpdir)
        if audio_path and os.path.exists(audio_path):
            results["transcription"] = transcribe_audio(groq_client, audio_path)
        else:
            results["transcription"] = "[Audio download failed — analysis based on description only]"
            # Fall back to description as script
            if meta.get("description"):
                results["transcription"] = meta["description"]

    return results


def build_analysis_graph(analysis: dict, metadata: dict) -> dict:
    """
    Build node/edge data for the visual connection map.
    Returns nodes and edges for Plotly network visualization.
    """
    import math, random

    nodes = []
    edges = []

    overview = analysis.get("overview", {})
    hook = analysis.get("hook", {})
    emotion = analysis.get("emotional_arc", {})
    structure = analysis.get("structure", {})
    tone = analysis.get("tone_voice", {})
    retention = analysis.get("retention_prediction", {})
    pf = overview.get("platform_fit", {})

    # ── Central node ──────────────────────────────────────────────────────────
    title = metadata.get("title", "Video")[:40]
    nodes.append({
        "id": "center",
        "label": title,
        "x": 0, "y": 0,
        "size": 36,
        "color": "#7c3aed",
        "text_color": "#ffffff",
        "group": "center",
        "detail": f"Overall Score: {overview.get('overall_score','—')}/100"
    })

    # ── Score ring nodes ──────────────────────────────────────────────────────
    ring1 = [
        ("hook_node", f"🎣 Hook\n{hook.get('score','—')}/100", hook.get('score', 50), "#06b6d4", "hook",
         f"Type: {hook.get('type','—')}\nTrigger: {hook.get('psychological_trigger','—')}"),
        ("emotion_node", f"💭 Emotion\n{emotion.get('score','—')}/100", emotion.get('score', 50), "#10b981", "emotion",
         f"Dominant: {emotion.get('dominant_emotion','—')}\nEQ: {emotion.get('emotional_intelligence_rating','—')}"),
        ("structure_node", f"🏗️ Structure\n{structure.get('score','—')}/100", structure.get('score', 50), "#f59e0b", "structure",
         f"Opening: {structure.get('opening_type','—')}\nPacing: {structure.get('pacing','—')}"),
        ("tone_node", f"🎙️ Tone\n{tone.get('score','—')}/100", tone.get('score', 50), "#ec4899", "tone",
         f"Primary: {tone.get('primary_tone','—')}\nEnergy: {tone.get('energy_level','—')}"),
        ("retention_node", f"📊 Retention\n{retention.get('score','—')}/100", retention.get('score', 50), "#8b5cf6", "retention",
         f"Predicted: {retention.get('predicted_watch_through_rate','—')}\nVirality: {retention.get('virality_potential','—')}"),
    ]

    r1 = 2.2
    for i, (nid, label, score, color, group, detail) in enumerate(ring1):
        angle = (2 * math.pi * i / len(ring1)) - math.pi / 2
        x = r1 * math.cos(angle)
        y = r1 * math.sin(angle)
        size = 14 + (score or 50) * 0.14
        nodes.append({"id": nid, "label": label, "x": x, "y": y,
                       "size": size, "color": color, "text_color": "#ffffff",
                       "group": group, "detail": detail})
        edges.append({"from": "center", "to": nid, "weight": (score or 50) / 100, "color": color})

    # ── Platform fit satellite nodes ──────────────────────────────────────────
    r2 = 3.8
    platform_items = list(pf.items())[:4] if pf else []
    for i, (pname, pscore) in enumerate(platform_items):
        angle = (2 * math.pi * i / max(len(platform_items), 1)) + math.pi / 6
        x = r2 * math.cos(angle)
        y = r2 * math.sin(angle)
        pid = f"platform_{i}"
        short = pname.replace("_", " ").replace("YouTube", "YT")
        nodes.append({
            "id": pid,
            "label": f"📱 {short}\n{pscore}/100",
            "x": x, "y": y,
            "size": 10 + pscore * 0.08,
            "color": "#374151",
            "text_color": "#9ca3af",
            "group": "platform",
            "detail": f"Platform fit score: {pscore}/100"
        })
        # Connect to relevant score nodes
        edges.append({"from": "hook_node", "to": pid, "weight": pscore / 100, "color": "#374151"})

    # ── Emotion journey nodes ─────────────────────────────────────────────────
    journey = emotion.get("journey", [])
    r3 = 4.5
    for i, step in enumerate(journey[:4]):
        angle = (2 * math.pi * i / 4) + math.pi
        x = r3 * math.cos(angle)
        y = r3 * math.sin(angle)
        eid = f"emo_{i}"
        intensity = step.get("intensity", 50)
        nodes.append({
            "id": eid,
            "label": f"{step.get('timestamp','')}\n{step.get('emotion','')}\n{intensity}%",
            "x": x, "y": y,
            "size": 8 + intensity * 0.1,
            "color": "#1e3a5f",
            "text_color": "#67e8f9",
            "group": "journey",
            "detail": f"Purpose: {step.get('purpose','—')}"
        })
        edges.append({"from": "emotion_node", "to": eid, "weight": intensity / 100, "color": "#06b6d422"})

    # ── Strengths nodes ───────────────────────────────────────────────────────
    strengths = analysis.get("strengths", [])[:3]
    for i, s in enumerate(strengths):
        angle = -math.pi / 4 + i * 0.5
        x = 5.2 * math.cos(angle)
        y = 5.2 * math.sin(angle)
        nodes.append({
            "id": f"str_{i}",
            "label": f"✅ {s[:25]}",
            "x": x, "y": y,
            "size": 8,
            "color": "#064e3b",
            "text_color": "#6ee7b7",
            "group": "strength",
            "detail": s
        })
        edges.append({"from": "center", "to": f"str_{i}", "weight": 0.3, "color": "#10b98122"})

    # ── Weakness nodes ────────────────────────────────────────────────────────
    weaknesses = analysis.get("weaknesses", [])[:3]
    for i, w in enumerate(weaknesses):
        angle = math.pi + math.pi / 4 + i * 0.5
        x = 5.2 * math.cos(angle)
        y = 5.2 * math.sin(angle)
        nodes.append({
            "id": f"weak_{i}",
            "label": f"⚠ {w[:25]}",
            "x": x, "y": y,
            "size": 8,
            "color": "#4c0519",
            "text_color": "#fca5a5",
            "group": "weakness",
            "detail": w
        })
        edges.append({"from": "center", "to": f"weak_{i}", "weight": 0.3, "color": "#ef444422"})

    return {"nodes": nodes, "edges": edges}

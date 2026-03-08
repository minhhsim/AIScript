# modules/url_analyzer.py
import os
import re
import sys
import json
import shutil
import tempfile
import subprocess
import math


# ── yt-dlp helpers ────────────────────────────────────────────────────────────

def _ytdlp_cmd() -> list:
    """Return working yt-dlp command — handles Windows PATH issues."""
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    # pip installed but not on PATH (common on Windows/Python 3.14)
    return [sys.executable, "-m", "yt_dlp"]


def _ytdlp_available() -> bool:
    if shutil.which("yt-dlp"):
        return True
    try:
        r = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--version"],
            capture_output=True, text=True, timeout=10
        )
        return r.returncode == 0
    except Exception:
        return False


def get_video_metadata(url: str) -> dict:
    try:
        result = subprocess.run(
            _ytdlp_cmd() + ["--dump-json", "--no-playlist", url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return {"error": result.stderr[:300]}
        data = json.loads(result.stdout)
        return {
            "title":       data.get("title", "Unknown"),
            "uploader":    data.get("uploader", "Unknown"),
            "duration":    data.get("duration", 0),
            "view_count":  data.get("view_count", 0),
            "like_count":  data.get("like_count", 0),
            "description": (data.get("description") or "")[:1000],
            "upload_date": data.get("upload_date", ""),
            "platform":    data.get("extractor_key", "Unknown"),
            "thumbnail":   data.get("thumbnail", ""),
            "tags":        data.get("tags", [])[:10],
            "categories":  data.get("categories", []),
        }
    except Exception as e:
        return {"error": str(e)}


def download_audio(url: str, output_dir: str) -> str:
    output_template = os.path.join(output_dir, "audio.%(ext)s")
    try:
        result = subprocess.run(
            _ytdlp_cmd() + [
                "--extract-audio", "--audio-format", "mp3",
                "--audio-quality", "128K", "--no-playlist",
                "--max-filesize", "50m", "-o", output_template, url
            ],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            print(f"[yt-dlp] {result.stderr[:200]}")
            return None
        for f in os.listdir(output_dir):
            if f.startswith("audio") and f.endswith(".mp3"):
                return os.path.join(output_dir, f)
        return None
    except Exception as e:
        print(f"[yt-dlp download error] {e}")
        return None


def transcribe_audio(groq_client, audio_path: str) -> str:
    try:
        with open(audio_path, "rb") as f:
            transcription = groq_client.audio.transcriptions.create(
                file=(os.path.basename(audio_path), f.read()),
                model="whisper-large-v3",
                response_format="text"
            )
        return transcription if isinstance(transcription, str) else str(transcription)
    except Exception as e:
        return f"[Transcription failed: {e}]"


def analyze_url(groq_client, url: str) -> dict:
    results = {"url": url, "metadata": {}, "transcription": "", "error": None}

    if not _ytdlp_available():
        results["error"] = "yt-dlp not found. Run: pip install yt-dlp"
        return results

    meta = get_video_metadata(url)
    if "error" in meta:
        results["error"] = f"Could not fetch video: {meta['error']}"
        return results
    results["metadata"] = meta

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = download_audio(url, tmpdir)
        if audio_path and os.path.exists(audio_path):
            results["transcription"] = transcribe_audio(groq_client, audio_path)
        else:
            results["transcription"] = meta.get("description") or "[Audio download failed]"

    return results


# ── Visual Direction Generator ────────────────────────────────────────────────

def generate_visual_direction(groq_client, script_text: str, platform: str = "TikTok") -> list:
    prompt = f"""You are a professional video director specializing in {platform} content.

Analyze this script and break it into cinematic shots.

SCRIPT:
\"\"\"{script_text[:3000]}\"\"\"

Return ONLY a JSON array with 6-10 shot objects, no markdown fences:
[
  {{
    "shot_number": 1,
    "timestamp": "0-3s",
    "shot_type": "ECU / CU / MCU / MS / WS / OTS / POV / B-Roll",
    "camera_angle": "Eye Level / Low Angle / High Angle / Dutch / Bird's Eye",
    "camera_movement": "Static / Pan / Tilt / Dolly / Zoom / Handheld",
    "subject": "what/who is in frame",
    "action": "what is happening visually",
    "script_line": "the spoken words during this shot",
    "lighting": "Natural / Softbox / Rim / Backlit / Golden Hour / Studio",
    "color_mood": "#FF6B35",
    "emotion_target": "emotion this triggers in viewer",
    "director_note": "one specific tip to make this shot work",
    "icon": "single emoji representing this shot"
  }}
]"""

    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a cinematographer. Return only valid JSON arrays. No markdown."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,
            temperature=0.4
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"^```\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        shots = json.loads(raw)
        return shots if isinstance(shots, list) else []
    except Exception as e:
        print(f"[VisualDirection] {e}")
        return []


# ── Network Graph Builder ─────────────────────────────────────────────────────

def build_analysis_graph(analysis: dict, metadata: dict) -> dict:
    nodes = []
    edges = []

    overview  = analysis.get("overview", {})
    hook      = analysis.get("hook", {})
    emotion   = analysis.get("emotional_arc", {})
    structure = analysis.get("structure", {})
    tone      = analysis.get("tone_voice", {})
    retention = analysis.get("retention_prediction", {})
    pf        = overview.get("platform_fit", {})

    title = metadata.get("title", "Video")[:40]
    nodes.append({
        "id": "center", "label": title, "x": 0, "y": 0,
        "size": 36, "color": "#7c3aed", "text_color": "#ffffff",
        "group": "center",
        "detail": f"Overall Score: {overview.get('overall_score','—')}/100"
    })

    ring1 = [
        ("hook_node",      f"🎣 Hook\n{hook.get('score','—')}/100",          hook.get('score', 50),      "#06b6d4", "hook",
         f"Type: {hook.get('type','—')}\nTrigger: {hook.get('psychological_trigger','—')}"),
        ("emotion_node",   f"💭 Emotion\n{emotion.get('score','—')}/100",     emotion.get('score', 50),   "#10b981", "emotion",
         f"Dominant: {emotion.get('dominant_emotion','—')}"),
        ("structure_node", f"🏗️ Structure\n{structure.get('score','—')}/100", structure.get('score', 50), "#f59e0b", "structure",
         f"Opening: {structure.get('opening_type','—')}"),
        ("tone_node",      f"🎙️ Tone\n{tone.get('score','—')}/100",          tone.get('score', 50),      "#ec4899", "tone",
         f"Primary: {tone.get('primary_tone','—')}"),
        ("retention_node", f"📊 Retention\n{retention.get('score','—')}/100", retention.get('score', 50), "#8b5cf6", "retention",
         f"Virality: {retention.get('virality_potential','—')}"),
    ]

    r1 = 2.2
    for i, (nid, label, score, color, group, detail) in enumerate(ring1):
        angle = (2 * math.pi * i / len(ring1)) - math.pi / 2
        x, y = r1 * math.cos(angle), r1 * math.sin(angle)
        nodes.append({"id": nid, "label": label, "x": x, "y": y,
                       "size": 14 + (score or 50) * 0.14, "color": color,
                       "text_color": "#ffffff", "group": group, "detail": detail})
        edges.append({"from": "center", "to": nid, "weight": (score or 50) / 100, "color": color})

    r2 = 3.8
    for i, (pname, pscore) in enumerate(list(pf.items())[:4]):
        angle = (2 * math.pi * i / 4) + math.pi / 6
        x, y = r2 * math.cos(angle), r2 * math.sin(angle)
        short = pname.replace("_", " ").replace("YouTube", "YT")
        nodes.append({"id": f"platform_{i}", "label": f"📱 {short}\n{pscore}/100",
                       "x": x, "y": y, "size": 10 + pscore * 0.08,
                       "color": "#374151", "text_color": "#9ca3af",
                       "group": "platform", "detail": f"Fit: {pscore}/100"})
        edges.append({"from": "hook_node", "to": f"platform_{i}", "weight": pscore / 100, "color": "#374151"})

    r3 = 4.5
    for i, step in enumerate(emotion.get("journey", [])[:4]):
        angle = (2 * math.pi * i / 4) + math.pi
        x, y = r3 * math.cos(angle), r3 * math.sin(angle)
        intensity = step.get("intensity", 50)
        nodes.append({"id": f"emo_{i}",
                       "label": f"{step.get('timestamp','')}\n{step.get('emotion','')}\n{intensity}%",
                       "x": x, "y": y, "size": 8 + intensity * 0.1,
                       "color": "#1e3a5f", "text_color": "#67e8f9",
                       "group": "journey", "detail": f"Purpose: {step.get('purpose','—')}"})
        edges.append({"from": "emotion_node", "to": f"emo_{i}", "weight": intensity / 100, "color": "rgba(6,182,212,0.13)"})

    for i, s in enumerate(analysis.get("strengths", [])[:3]):
        angle = -math.pi / 4 + i * 0.5
        x, y = 5.2 * math.cos(angle), 5.2 * math.sin(angle)
        nodes.append({"id": f"str_{i}", "label": f"✅ {s[:25]}",
                       "x": x, "y": y, "size": 8, "color": "#064e3b",
                       "text_color": "#6ee7b7", "group": "strength", "detail": s})
        edges.append({"from": "center", "to": f"str_{i}", "weight": 0.3, "color": "rgba(16,185,129,0.13)"})

    for i, w in enumerate(analysis.get("weaknesses", [])[:3]):
        angle = math.pi + math.pi / 4 + i * 0.5
        x, y = 5.2 * math.cos(angle), 5.2 * math.sin(angle)
        nodes.append({"id": f"weak_{i}", "label": f"⚠ {w[:25]}",
                       "x": x, "y": y, "size": 8, "color": "#4c0519",
                       "text_color": "#fca5a5", "group": "weakness", "detail": w})
        edges.append({"from": "center", "to": f"weak_{i}", "weight": 0.3, "color": "rgba(239,68,68,0.13)"})

    return {"nodes": nodes, "edges": edges}

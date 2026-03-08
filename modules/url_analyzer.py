# modules/url_analyzer.py
import os, re, sys, json, shutil, tempfile, subprocess, math


# ── yt-dlp helpers ────────────────────────────────────────────────────────────

def _ytdlp_cmd() -> list:
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    return [sys.executable, "-m", "yt_dlp"]


def _ytdlp_available() -> bool:
    if shutil.which("yt-dlp"):
        return True
    try:
        r = subprocess.run([sys.executable, "-m", "yt_dlp", "--version"],
                           capture_output=True, text=True, timeout=10)
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
            "tags":        data.get("tags", [])[:15],
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
        print(f"[yt-dlp download] {e}")
        return None


def transcribe_audio(groq_client, audio_path: str) -> str:
    try:
        with open(audio_path, "rb") as f:
            result = groq_client.audio.transcriptions.create(
                file=(os.path.basename(audio_path), f.read()),
                model="whisper-large-v3",
                response_format="text"
            )
        return result if isinstance(result, str) else str(result)
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


# ── Video Type Detection ──────────────────────────────────────────────────────

VIDEO_TYPES = {
    "dance":        {"label": "💃 Dance / Performance",    "color": "#ec4899", "icon": "💃"},
    "voiceover":    {"label": "🎙️ Voiceover / Narration",  "color": "#8b5cf6", "icon": "🎙️"},
    "talking_head": {"label": "🗣️ Talking Head / Vlog",    "color": "#06b6d4", "icon": "🗣️"},
    "tutorial":     {"label": "📚 Tutorial / How-To",       "color": "#10b981", "icon": "📚"},
    "comedy":       {"label": "😂 Comedy / Skit",           "color": "#f59e0b", "icon": "😂"},
    "reaction":     {"label": "😱 Reaction",                "color": "#ef4444", "icon": "😱"},
    "aesthetic":    {"label": "✨ Aesthetic / Montage",     "color": "#a78bfa", "icon": "✨"},
    "product":      {"label": "🛍️ Product / Review",        "color": "#14b8a6", "icon": "🛍️"},
    "news":         {"label": "📰 News / Commentary",       "color": "#64748b", "icon": "📰"},
    "motivational": {"label": "🔥 Motivational / Story",   "color": "#f97316", "icon": "🔥"},
    "unknown":      {"label": "🎬 General Video",           "color": "#7c3aed", "icon": "🎬"},
}


def detect_video_type(groq_client, transcription: str, metadata: dict) -> dict:
    """
    Detect video type using AI analysis of transcript + metadata signals.
    Returns type dict with label, color, icon, confidence, reasoning, subtype.
    """
    title       = metadata.get("title", "")
    tags        = metadata.get("tags", [])
    description = metadata.get("description", "")
    duration    = metadata.get("duration", 0)

    # Quick signal-based pre-detection for obvious cases
    all_signals = f"{title} {' '.join(tags)} {description}".lower()
    transcript_lower = transcription.lower()

    # These are high-confidence keyword signals
    quick_signals = {
        "dance":     ["dance", "dancing", "choreography", "choreo", "moves", "freestyle", "twerk"],
        "tutorial":  ["tutorial", "how to", "step by step", "diy", "learn", "tips", "guide", "hack"],
        "comedy":    ["pov:", "skit", "comedy", "funny", "lol", "🤣", "hilarious", "joke"],
        "reaction":  ["reaction", "reacting", "watch me react", "first time watching"],
        "product":   ["review", "unboxing", "this product", "bought this", "amazon", "trying out"],
        "news":      ["breaking", "news", "just in", "update", "happening now", "latest"],
        "motivational": ["motivation", "mindset", "success", "grind", "hustle", "believe", "you can"],
    }

    for vtype, keywords in quick_signals.items():
        if any(kw in all_signals or kw in transcript_lower for kw in keywords):
            # Confirm with short AI call for borderline cases
            pass  # Still run AI for confidence + subtype

    # AI detection for nuanced classification
    prompt = f"""You are a social media content analyst. Classify this video into exactly ONE type.

VIDEO METADATA:
Title: {title}
Duration: {duration}s
Tags: {', '.join(tags[:8])}
Description: {description[:300]}

TRANSCRIPT:
\"\"\"{transcription[:1500]}\"\"\"

Choose ONE primary type from:
- dance: dancing, choreography, performance, movement-based
- voiceover: narration over footage, no face shown, storytelling with visuals
- talking_head: person speaking directly to camera, vlog, interview, face-cam
- tutorial: how-to, step-by-step instructions, educational demos
- comedy: skits, POV videos, parody, funny scenarios
- reaction: reacting to content, duets, watching something
- aesthetic: montage, cinematic, minimal speech, vibe-based, ASMR
- product: unboxing, review, haul, try-on
- news: news commentary, current events, updates
- motivational: inspiration, mindset, personal story, transformation
- unknown: none of the above

Return ONLY valid JSON, no markdown:
{{
  "type": "one of the types above",
  "confidence": 0-100,
  "subtype": "more specific description e.g. 'K-pop dance cover' or 'makeup tutorial' or 'gym motivation'",
  "reasoning": "1-2 sentences explaining why",
  "has_speech": true/false,
  "has_music": true/false,
  "has_face": true/false,
  "content_density": "low/medium/high",
  "pacing": "slow/medium/fast/very_fast",
  "primary_audience": "who this is for"
}}"""

    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a video classification expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.1
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"^```\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        data = json.loads(raw)

        vtype    = data.get("type", "unknown")
        type_meta = VIDEO_TYPES.get(vtype, VIDEO_TYPES["unknown"])

        return {
            "type":             vtype,
            "label":            type_meta["label"],
            "color":            type_meta["color"],
            "icon":             type_meta["icon"],
            "confidence":       data.get("confidence", 70),
            "subtype":          data.get("subtype", ""),
            "reasoning":        data.get("reasoning", ""),
            "has_speech":       data.get("has_speech", True),
            "has_music":        data.get("has_music", False),
            "has_face":         data.get("has_face", True),
            "content_density":  data.get("content_density", "medium"),
            "pacing":           data.get("pacing", "medium"),
            "primary_audience": data.get("primary_audience", "General"),
        }
    except Exception as e:
        print(f"[VideoTypeDetection] {e}")
        return {**VIDEO_TYPES["unknown"], "type": "unknown",
                "confidence": 0, "subtype": "", "reasoning": "",
                "has_speech": True, "has_music": False, "has_face": True,
                "content_density": "medium", "pacing": "medium", "primary_audience": "General"}


# ── Type-Specific Analysis Prompts ────────────────────────────────────────────

TYPE_ANALYSIS_CONTEXT = {
    "dance": """Focus on:
- Transition timing: are cuts synced to beat drops?
- Hook moment: what visual gesture happens in first 2s to stop the scroll?
- Trend alignment: is this using a trending sound/choreo or original?
- Energy arc: does the energy build, peak, and close well?
- Loop-ability: does it end in a way that encourages replay?""",

    "voiceover": """Focus on:
- Script pacing: words per second, is it too fast or slow for the visuals?
- Emotional hook: does the opening line create curiosity or emotion instantly?
- Visual-audio sync: do the visuals reinforce or contradict what's being said?
- Retention risk: where does narration lose momentum?
- Story arc: is there a clear beginning tension → build → resolution?""",

    "talking_head": """Focus on:
- Eye contact & camera confidence: is the presenter engaging directly?
- Hook delivery: is the first sentence spoken with energy and purpose?
- Filler words: excessive 'um', 'like', 'you know' that reduce authority
- Gesture & body language: does physical presence support or distract?
- CTA clarity: is there a clear ask and does it land naturally?""",

    "tutorial": """Focus on:
- Clarity of steps: are instructions numbered, clear, easy to follow?
- Demonstration quality: are key steps shown visually, not just narrated?
- Pacing: does it rush through hard parts or overexplain simple ones?
- Hook promise: does the opening clearly state what viewer will learn?
- Save-worthiness: is this the type of video people screenshot or save?""",

    "comedy": """Focus on:
- Setup efficiency: does the premise land within the first 3 seconds?
- Punchline timing: is the joke delivered at the right moment?
- Relatability factor: does the audience immediately recognize themselves?
- Pattern subversion: does it set up an expectation and break it?
- Shareability: is there a 'send this to your friend' moment?""",

    "reaction": """Focus on:
- Authentic reaction: does the reactor's emotion feel genuine or performed?
- Commentary value: does the reactor add insight beyond just watching?
- Duet/Split use: if split-screen, is both content visible and readable?
- Engagement trigger: does it make viewers want to watch the original?
- Timestamp hooks: are the best reaction moments in the first 5 seconds?""",

    "aesthetic": """Focus on:
- Visual cohesion: do all clips share a consistent color palette and mood?
- Sound-visual sync: do cuts happen on beat or at emotional audio peaks?
- Pacing rhythm: is the edit fast enough to hold attention, slow enough to feel?
- Mood delivery: does the overall video evoke a specific single emotion?
- Text overlay: if any, is it minimal and enhancing vs cluttering?""",

    "product": """Focus on:
- First impression hook: is the product shown compellingly in frame 1?
- Social proof signals: reviews, unboxing excitement, genuine reaction
- Feature demonstration: are key benefits shown visually, not just listed?
- Purchase trigger: is there urgency, scarcity, or a clear 'get this' moment?
- Trust signals: does creator seem genuine or overly scripted/paid?""",

    "news": """Focus on:
- Credibility signals: does the presenter establish authority quickly?
- Information clarity: is the key point stated in the first 5 seconds?
- Source transparency: are claims backed by visible evidence?
- Bias awareness: is the framing neutral or one-sided?
- Engagement hook: is there a question, controversy, or tension that keeps viewers?""",

    "motivational": """Focus on:
- Personal story authenticity: does the struggle feel real and specific?
- Emotional journey: does it move from pain → turning point → transformation?
- Relatability: can the audience see themselves in this story?
- Message clarity: is the core lesson stated powerfully?
- Action trigger: does it make the viewer want to do something immediately?""",

    "unknown": """Focus on:
- Overall content clarity and purpose
- Hook strength in first 3 seconds
- Pacing and retention risk points
- Audience fit and platform optimization
- Key improvements for engagement""",
}


def analyze_script_typed(groq_client, transcription: str, platform: str, video_type: dict) -> dict:
    """Run script analysis with type-specific context for more relevant feedback."""
    from modules.script_analyzer import analyze_script

    vtype   = video_type.get("type", "unknown")
    subtype = video_type.get("subtype", "")
    context = TYPE_ANALYSIS_CONTEXT.get(vtype, TYPE_ANALYSIS_CONTEXT["unknown"])

    # Inject type-specific context into the standard analyzer
    typed_transcription = f"""[VIDEO TYPE: {video_type.get('label','')} — {subtype}]
[PACING: {video_type.get('pacing','')} | HAS SPEECH: {video_type.get('has_speech',True)} | HAS MUSIC: {video_type.get('has_music',False)}]
[TARGET AUDIENCE: {video_type.get('primary_audience','')}]

TYPE-SPECIFIC ANALYSIS FOCUS:
{context}

TRANSCRIPT / AUDIO:
{transcription}"""

    return analyze_script(groq_client, typed_transcription, platform)


# ── Visual Direction Generator ────────────────────────────────────────────────

def generate_visual_direction(groq_client, script_text: str, platform: str, video_type: dict) -> list:
    """Generate shot-by-shot visual direction cards tailored to video type."""

    vtype   = video_type.get("type", "unknown")
    subtype = video_type.get("subtype", "")
    label   = video_type.get("label", "General Video")

    # Type-specific direction style
    direction_styles = {
        "dance": "Focus on: beat-sync cut timing, energy framing, performance angles (low angle hero shots, overhead, close on footwork/hands), crowd/reaction inserts.",
        "voiceover": "Focus on: B-roll shots that match narration, text overlays, cutaway timing, visual metaphors for spoken concepts.",
        "talking_head": "Focus on: camera framing (MCU/CU), depth of field, background setup, lighting for face, eye-line adjustments.",
        "tutorial": "Focus on: POV shots of hands/subject, clear demonstration angles, text callouts, before/after framing.",
        "comedy": "Focus on: comedic timing of cuts, reaction shots, deadpan framing, unexpected angle changes for punchlines.",
        "reaction": "Focus on: split-screen layout, reactor close-ups during peak moments, caption overlays, zoom-ins.",
        "aesthetic": "Focus on: color grading notes, smooth transitions, golden hour/mood lighting, minimal text, visual rhythm.",
        "product": "Focus on: macro product shots, unboxing reveal angles, before/after, lifestyle context shots.",
        "news": "Focus on: clean authoritative framing, text lower-thirds, source footage cutaways, stable camera.",
        "motivational": "Focus on: emotional close-ups, transformation visual cues, high-energy B-roll, powerful statement overlays.",
        "unknown": "Focus on: best practices for the platform, clear subject framing, good lighting.",
    }

    direction_focus = direction_styles.get(vtype, direction_styles["unknown"])

    prompt = f"""You are a professional {label} video director for {platform}.

VIDEO TYPE: {label} ({subtype})
DIRECTION STYLE: {direction_focus}

TRANSCRIPT / AUDIO CONTENT:
\"\"\"{script_text[:2500]}\"\"\"

Create a realistic shot-by-shot storyboard for this EXACT type of video.
Be specific to {label} content — don't give generic advice.

Return ONLY a JSON array of 6-10 shots, no markdown:
[
  {{
    "shot_number": 1,
    "timestamp": "0-3s",
    "shot_type": "ECU/CU/MCU/MS/WS/OTS/POV/B-Roll/Split-Screen/Overhead",
    "camera_angle": "Eye Level/Low Angle/High Angle/Dutch/Bird's Eye/Selfie",
    "camera_movement": "Static/Pan/Tilt/Dolly/Zoom/Handheld/Stabilized/Whip Pan",
    "subject": "what/who is in frame — be specific to this video type",
    "action": "what is happening visually — specific to {vtype}",
    "script_line": "audio/spoken words during this shot (or 'music only' for dance/aesthetic)",
    "lighting": "Natural/Softbox/Ring Light/Rim/Backlit/Golden Hour/Neon/Studio",
    "color_mood": "#hexcolor representing the mood",
    "emotion_target": "specific emotion this shot triggers",
    "director_note": "ONE highly specific tip for this exact video type and shot",
    "icon": "single emoji"
  }}
]"""

    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"You are a {label} video director. Give type-specific cinematic direction. Return only valid JSON."},
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

def build_analysis_graph(analysis: dict, metadata: dict, video_type: dict = None) -> dict:
    nodes = []
    edges = []

    overview  = analysis.get("overview", {})
    hook      = analysis.get("hook", {})
    emotion   = analysis.get("emotional_arc", {})
    structure = analysis.get("structure", {})
    tone      = analysis.get("tone_voice", {})
    retention = analysis.get("retention_prediction", {})
    pf        = overview.get("platform_fit", {})

    center_color = (video_type or {}).get("color", "#7c3aed")

    title = metadata.get("title", "Video")[:40]
    nodes.append({
        "id": "center", "label": title, "x": 0, "y": 0,
        "size": 36, "color": center_color, "text_color": "#ffffff",
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
        x, y  = r1 * math.cos(angle), r1 * math.sin(angle)
        nodes.append({"id": nid, "label": label, "x": x, "y": y,
                       "size": 14 + (score or 50) * 0.14, "color": color,
                       "text_color": "#ffffff", "group": group, "detail": detail})
        edges.append({"from": "center", "to": nid, "weight": (score or 50) / 100, "color": color})

    r2 = 3.8
    for i, (pname, pscore) in enumerate(list(pf.items())[:4]):
        angle = (2 * math.pi * i / 4) + math.pi / 6
        x, y  = r2 * math.cos(angle), r2 * math.sin(angle)
        short = pname.replace("_", " ").replace("YouTube", "YT")
        nodes.append({"id": f"platform_{i}", "label": f"📱 {short}\n{pscore}/100",
                       "x": x, "y": y, "size": 10 + pscore * 0.08,
                       "color": "#374151", "text_color": "#9ca3af",
                       "group": "platform", "detail": f"Fit: {pscore}/100"})
        edges.append({"from": "hook_node", "to": f"platform_{i}",
                      "weight": pscore / 100, "color": "#374151"})

    r3 = 4.5
    for i, step in enumerate(emotion.get("journey", [])[:4]):
        angle     = (2 * math.pi * i / 4) + math.pi
        x, y      = r3 * math.cos(angle), r3 * math.sin(angle)
        intensity = step.get("intensity", 50)
        nodes.append({"id": f"emo_{i}",
                       "label": f"{step.get('timestamp','')}\n{step.get('emotion','')}\n{intensity}%",
                       "x": x, "y": y, "size": 8 + intensity * 0.1,
                       "color": "#1e3a5f", "text_color": "#67e8f9",
                       "group": "journey", "detail": f"Purpose: {step.get('purpose','—')}"})
        edges.append({"from": "emotion_node", "to": f"emo_{i}",
                      "weight": intensity / 100, "color": "rgba(6,182,212,0.13)"})

    for i, s in enumerate(analysis.get("strengths", [])[:3]):
        angle = -math.pi / 4 + i * 0.5
        x, y  = 5.2 * math.cos(angle), 5.2 * math.sin(angle)
        nodes.append({"id": f"str_{i}", "label": f"✅ {s[:25]}",
                       "x": x, "y": y, "size": 8, "color": "#064e3b",
                       "text_color": "#6ee7b7", "group": "strength", "detail": s})
        edges.append({"from": "center", "to": f"str_{i}",
                      "weight": 0.3, "color": "rgba(16,185,129,0.13)"})

    for i, w in enumerate(analysis.get("weaknesses", [])[:3]):
        angle = math.pi + math.pi / 4 + i * 0.5
        x, y  = 5.2 * math.cos(angle), 5.2 * math.sin(angle)
        nodes.append({"id": f"weak_{i}", "label": f"⚠ {w[:25]}",
                       "x": x, "y": y, "size": 8, "color": "#4c0519",
                       "text_color": "#fca5a5", "group": "weakness", "detail": w})
        edges.append({"from": "center", "to": f"weak_{i}",
                      "weight": 0.3, "color": "rgba(239,68,68,0.13)"})

    return {"nodes": nodes, "edges": edges}

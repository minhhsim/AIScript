# modules/video_analyzer.py
"""
Video analysis pipeline:
1. Extract audio → transcribe with Groq Whisper
2. Extract key frames with OpenCV
3. Analyze frames with Groq Vision
4. Combine into comprehensive feedback report
"""

import cv2
import base64
import tempfile
import os
import json
import re
import numpy as np
from PIL import Image
import io


def extract_audio_from_video(video_path: str) -> str:
    """Extract audio from video and save as mp3. Returns audio path."""
    try:
        from moviepy.editor import VideoFileClip
        audio_path = video_path.replace(".mp4", "_audio.mp3").replace(".mov", "_audio.mp3").replace(".avi", "_audio.mp3")
        clip = VideoFileClip(video_path)
        if clip.audio:
            clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
            clip.close()
            return audio_path
        clip.close()
        return None
    except Exception as e:
        print(f"Audio extraction error: {e}")
        return None


def transcribe_audio(groq_client, audio_path: str) -> str:
    """Transcribe audio using Groq Whisper."""
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


def extract_key_frames(video_path: str, num_frames: int = 6) -> list:
    """Extract evenly-spaced key frames from video. Returns list of base64 strings."""
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0

    if total_frames == 0:
        cap.release()
        return []

    indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
    frames_b64 = []

    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(frame_rgb)
        # Resize for API efficiency
        pil_img.thumbnail((768, 768), Image.LANCZOS)
        buf = io.BytesIO()
        pil_img.save(buf, format="JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        timestamp = idx / fps if fps > 0 else 0
        frames_b64.append({"b64": b64, "timestamp": round(timestamp, 1)})

    cap.release()
    return frames_b64, round(duration, 1)


def analyze_frames_with_vision(groq_client, frames: list, transcription: str) -> str:
    """Send frames to Groq vision model for visual analysis."""
    if not frames:
        return "No frames could be extracted."

    # Build content list with all frames
    content = []

    # Add frames
    for frame_data in frames:
        content.append({
            "type": "text",
            "text": f"[Frame at {frame_data['timestamp']}s]"
        })
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{frame_data['b64']}"
            }
        })

    content.append({
        "type": "text",
        "text": f"""Analyze these video frames as a professional content strategist.

VIDEO TRANSCRIPT:
\"\"\"{transcription}\"\"\"

Provide detailed analysis of:
1. VISUAL QUALITY: Lighting, framing, composition, background, production value (score /100)
2. PRESENTER/SUBJECT: Energy, body language, eye contact, authenticity, charisma (score /100)
3. VISUAL HOOK: Does the opening frame stop a scroll? What's compelling or weak?
4. PACING & EDITING: Is the visual pacing appropriate for the platform?
5. BRAND CONSISTENCY: Colors, style, professionalism consistency
6. EMOTIONAL VISUAL IMPACT: Do the visuals amplify or undermine the script?
7. SPECIFIC IMPROVEMENTS: Frame-by-frame recommendations
8. THUMBNAIL POTENTIAL: Which frame would make the best thumbnail and why?

Be extremely specific and actionable."""
    })

    try:
        resp = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "system",
                    "content": "You are an elite video content analyst and production director. Provide brutally honest, highly specific feedback."
                },
                {
                    "role": "user",
                    "content": content
                }
            ],
            max_tokens=2000,
            temperature=0.3
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Visual analysis unavailable: {e}"


def generate_video_report(groq_client, transcription: str, visual_analysis: str, platform: str) -> dict:
    """Generate comprehensive video feedback report combining script + visual analysis."""

    prompt = f"""You are an elite content coach. Generate a comprehensive, actionable video analysis report.

PLATFORM: {platform}

TRANSCRIBED SCRIPT:
\"\"\"{transcription}\"\"\"

VISUAL ANALYSIS:
\"\"\"{visual_analysis}\"\"\"

Return a JSON object with this structure:
{{
  "overall_score": 0-100,
  "grade": "A/B/C/D/F",
  "viral_potential": "Low/Medium/High/Viral",
  "executive_summary": "string (3 sentences max - what this video does well and what kills it)",
  "script_analysis": {{
    "score": 0-100,
    "hook_strength": 0-100,
    "hook_feedback": "string",
    "clarity": 0-100,
    "emotional_resonance": 0-100,
    "cta_effectiveness": 0-100,
    "top_issues": ["string", "string"],
    "top_strengths": ["string", "string"]
  }},
  "visual_analysis": {{
    "score": 0-100,
    "production_quality": 0-100,
    "presenter_energy": 0-100,
    "lighting_score": 0-100,
    "framing_score": 0-100,
    "top_issues": ["string", "string"],
    "top_strengths": ["string", "string"]
  }},
  "retention_analysis": {{
    "predicted_retention": "string (e.g. 45%)",
    "drop_off_moments": ["string", "string"],
    "high_engagement_moments": ["string", "string"],
    "pacing_verdict": "string"
  }},
  "platform_optimization": {{
    "platform": "{platform}",
    "score": 0-100,
    "issues": ["string"],
    "optimizations": ["string", "string", "string"]
  }},
  "improvement_roadmap": [
    {{"priority": 1, "impact": "High", "effort": "Low", "action": "string", "expected_result": "string"}},
    {{"priority": 2, "impact": "High", "effort": "Medium", "action": "string", "expected_result": "string"}},
    {{"priority": 3, "impact": "Medium", "effort": "Low", "action": "string", "expected_result": "string"}},
    {{"priority": 4, "impact": "Medium", "effort": "Medium", "action": "string", "expected_result": "string"}},
    {{"priority": 5, "impact": "Low", "effort": "Low", "action": "string", "expected_result": "string"}}
  ],
  "rewritten_hook": "string (dramatically improved version of the opening 20 words)",
  "thumbnail_recommendation": "string (specific description of the ideal thumbnail frame)"
}}"""

    resp = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an elite video content analyst. Return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2500,
        temperature=0.2
    )

    raw = resp.choices[0].message.content.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except Exception:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {"error": "Could not parse report", "raw": raw}


def analyze_video_file(groq_client, video_path: str, platform: str = "TikTok") -> dict:
    """Full pipeline: extract frames + audio → transcribe → analyze → report."""
    results = {
        "transcription": "",
        "visual_analysis": "",
        "report": {},
        "frames": [],
        "duration": 0
    }

    # Step 1: Extract frames
    try:
        frames, duration = extract_key_frames(video_path, num_frames=6)
        results["frames"] = frames
        results["duration"] = duration
    except Exception as e:
        results["frames"] = []
        results["duration"] = 0

    # Step 2: Extract & transcribe audio
    audio_path = extract_audio_from_video(video_path)
    if audio_path and os.path.exists(audio_path):
        results["transcription"] = transcribe_audio(groq_client, audio_path)
        try:
            os.remove(audio_path)
        except Exception:
            pass
    else:
        results["transcription"] = "[No audio track found or extraction failed]"

    # Step 3: Visual analysis
    if results["frames"]:
        results["visual_analysis"] = analyze_frames_with_vision(
            groq_client, results["frames"], results["transcription"]
        )
    else:
        results["visual_analysis"] = "No frames extracted for visual analysis."

    # Step 4: Combined report
    results["report"] = generate_video_report(
        groq_client,
        results["transcription"],
        results["visual_analysis"],
        platform
    )

    return results

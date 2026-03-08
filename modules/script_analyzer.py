# modules/script_analyzer.py
"""
Analyzes scripts/transcripts for:
- Hook strength
- Emotional arc
- Tone & voice
- Content category
- Opening structure
- Retention prediction
- Platform suitability
"""

import json
import re


ANALYSIS_SYSTEM_PROMPT = """You are an elite content strategist and script analyst with expertise in 
viral social media content, consumer psychology, and emotional intelligence. 

You analyze scripts with surgical precision, evaluating:
- Psychological hooks and attention mechanisms
- Emotional journey and arc mapping
- Narrative structure and pacing
- Platform-specific optimization signals
- Viewer retention patterns
- Brand voice and authenticity markers

Always respond in valid JSON only. No markdown, no explanation outside the JSON."""


def analyze_script(groq_client, script_text: str, platform: str = "TikTok") -> dict:
    """Full deep analysis of a script. Returns structured dict."""

    prompt = f"""Analyze this {platform} script with extreme depth and precision.

SCRIPT:
\"\"\"
{script_text}
\"\"\"

Return a JSON object with EXACTLY this structure:
{{
  "overview": {{
    "category": "string (e.g. Education, Entertainment, Lifestyle, Finance, Fitness)",
    "sub_category": "string (more specific niche)",
    "platform_fit": {{
      "TikTok": 0-100,
      "YouTube_Shorts": 0-100,
      "Instagram_Reels": 0-100,
      "YouTube_Long": 0-100
    }},
    "estimated_duration_seconds": number,
    "word_count": number,
    "overall_score": 0-100
  }},
  "hook": {{
    "score": 0-100,
    "type": "string (e.g. Question Hook, Shock Hook, Story Hook, Controversy Hook, Value Hook)",
    "text": "string (the actual hook line from the script)",
    "first_3_seconds": "string (what happens in the critical first 3 seconds)",
    "psychological_trigger": "string (e.g. Curiosity Gap, FOMO, Social Proof, Fear, Desire)",
    "feedback": "string (specific actionable feedback on the hook)",
    "improved_version": "string (a better version of the hook)"
  }},
  "emotional_arc": {{
    "score": 0-100,
    "journey": [
      {{"timestamp": "0-10s", "emotion": "string", "intensity": 0-100, "purpose": "string"}},
      {{"timestamp": "10-20s", "emotion": "string", "intensity": 0-100, "purpose": "string"}},
      {{"timestamp": "20-30s", "emotion": "string", "intensity": 0-100, "purpose": "string"}},
      {{"timestamp": "30s+", "emotion": "string", "intensity": 0-100, "purpose": "string"}}
    ],
    "dominant_emotion": "string",
    "emotional_intelligence_rating": "string (Low/Medium/High/Exceptional)",
    "feedback": "string"
  }},
  "structure": {{
    "score": 0-100,
    "opening_type": "string (e.g. Bold Statement, Question, Story, Statistic, Demonstration)",
    "has_pattern_interrupt": true/false,
    "has_clear_cta": true/false,
    "cta_text": "string or null",
    "pacing": "string (Too Slow/Slow/Perfect/Fast/Too Fast)",
    "segments": [
      {{"name": "Hook", "duration": "string", "effectiveness": 0-100}},
      {{"name": "Body", "duration": "string", "effectiveness": 0-100}},
      {{"name": "CTA", "duration": "string", "effectiveness": 0-100}}
    ]
  }},
  "tone_voice": {{
    "score": 0-100,
    "primary_tone": "string (e.g. Authoritative, Conversational, Inspirational, Humorous, Urgent)",
    "secondary_tone": "string",
    "authenticity_score": 0-100,
    "relatability_score": 0-100,
    "energy_level": "string (Low/Medium/High/Intense)",
    "personality_traits": ["string", "string", "string"]
  }},
  "retention_prediction": {{
    "score": 0-100,
    "drop_off_risk_points": ["string", "string"],
    "strongest_moments": ["string", "string"],
    "predicted_watch_through_rate": "string (e.g. 65%)",
    "virality_potential": "string (Low/Medium/High/Viral)"
  }},
  "strengths": ["string", "string", "string"],
  "weaknesses": ["string", "string", "string"],
  "actionable_improvements": [
    {{"priority": "High", "area": "string", "suggestion": "string"}},
    {{"priority": "Medium", "area": "string", "suggestion": "string"}},
    {{"priority": "Low", "area": "string", "suggestion": "string"}}
  ],
  "rewritten_hook": "string (a significantly better version of the opening 15 words)"
}}"""

    resp = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2500,
        temperature=0.3
    )

    raw = resp.choices[0].message.content.strip()
    # Strip markdown code fences if present
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Attempt to extract JSON from response
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"error": "Could not parse analysis", "raw": raw}


def compare_scripts(groq_client, script_a: str, script_b: str) -> dict:
    """Compare two scripts head-to-head."""
    prompt = f"""Compare these two scripts head-to-head as a content strategist.

SCRIPT A:
\"\"\"{script_a}\"\"\"

SCRIPT B:
\"\"\"{script_b}\"\"\"

Return JSON:
{{
  "winner": "A or B",
  "hook_winner": "A or B",
  "retention_winner": "A or B", 
  "emotion_winner": "A or B",
  "score_a": 0-100,
  "score_b": 0-100,
  "key_differences": ["string", "string", "string"],
  "recommendation": "string"
}}"""

    resp = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,
        temperature=0.2
    )
    raw = resp.choices[0].message.content.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    try:
        return json.loads(raw)
    except Exception:
        return {"error": raw}

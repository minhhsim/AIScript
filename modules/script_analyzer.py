# modules/script_analyzer.py
"""
Deep script analysis engine.

Detects:
  - Narrative frameworks (AIDA, PAS, BAB, Hero's Journey, etc.)
  - Hook classification + psychology
  - Emotional arc mapping
  - Brand alignment signals
  - Pattern recommendations for improvement
"""

import json
import re


ANALYSIS_SYSTEM_PROMPT = """You are an elite content strategist and script analyst with expertise in
viral social media content, consumer psychology, and emotional intelligence.

You analyze scripts with surgical precision, identifying:
- Narrative frameworks and story structures
- Psychological hooks and attention mechanisms
- Emotional journey and arc mapping
- Brand voice and alignment signals
- Viewer retention patterns
- Pattern recommendations backed by performance data

Always respond in valid JSON only. No markdown, no explanation outside the JSON."""


# ─────────────────────────────────────────────────────────────────────────────
# Framework definitions (used in prompts + UI)
# ─────────────────────────────────────────────────────────────────────────────

NARRATIVE_FRAMEWORKS = {
    "AIDA": {
        "full": "Attention → Interest → Desire → Action",
        "description": "Classic persuasion arc. Grabs attention, builds interest with facts/story, creates desire with benefits, closes with a clear action.",
        "best_for": ["product launches", "sales", "promotions", "service explainers"],
        "platforms": ["YouTube", "Instagram Reels", "TikTok"],
        "icon": "🎯"
    },
    "PAS": {
        "full": "Problem → Agitate → Solution",
        "description": "Identify a pain, twist the knife to make it feel urgent, then deliver the relief. Most effective for high-emotion niches.",
        "best_for": ["health", "finance", "relationships", "self-improvement"],
        "platforms": ["TikTok", "Instagram Reels", "YouTube Shorts"],
        "icon": "💊"
    },
    "BAB": {
        "full": "Before → After → Bridge",
        "description": "Show the painful before state, paint the dream after state, then reveal the bridge (your solution) that gets them there.",
        "best_for": ["transformation stories", "fitness", "business", "lifestyle"],
        "platforms": ["TikTok", "Instagram", "YouTube"],
        "icon": "🌉"
    },
    "Hero's Journey": {
        "full": "Ordinary World → Call → Trial → Transformation → Return",
        "description": "The creator or subject goes on a journey, faces adversity, and returns changed. The viewer sees themselves in the hero.",
        "best_for": ["brand storytelling", "personal brand", "long-form", "motivation"],
        "platforms": ["YouTube", "Instagram", "LinkedIn"],
        "icon": "⚔️"
    },
    "Story Loop": {
        "full": "Open Loop → Tension → Payoff",
        "description": "Start mid-story or tease an answer, create tension that keeps viewer watching, deliver the satisfying payoff at the end.",
        "best_for": ["storytelling", "mystery", "suspense", "education with twist"],
        "platforms": ["TikTok", "YouTube Shorts", "Reels"],
        "icon": "🔄"
    },
    "Curiosity Gap": {
        "full": "Tease → Withhold → Reveal",
        "description": "Plant a question the viewer desperately wants answered, withhold the answer to maintain tension, deliver the reveal with impact.",
        "best_for": ["listicles", "facts", "tutorials", "reveal videos"],
        "platforms": ["TikTok", "YouTube", "Reels"],
        "icon": "❓"
    },
    "Problem-Solution": {
        "full": "Problem → Context → Solution → Proof",
        "description": "State the problem, give context/authority, present solution clearly, back it with proof. Clean and educational.",
        "best_for": ["tutorials", "how-to", "tech", "finance", "B2B"],
        "platforms": ["YouTube", "LinkedIn", "Instagram"],
        "icon": "🔧"
    },
    "Social Proof": {
        "full": "Credibility → Evidence → Invitation",
        "description": "Establish trust with results or authority, show evidence (numbers, reviews, testimonials), invite viewer to join the tribe.",
        "best_for": ["reviews", "testimonials", "case studies", "product demos"],
        "platforms": ["Instagram", "TikTok", "YouTube"],
        "icon": "⭐"
    },
    "Contrast Arc": {
        "full": "Before (Pain) → Contrast Moment → After (Dream)",
        "description": "Juxtapose two realities — the struggle and the transformation. Creates powerful emotional resonance.",
        "best_for": ["transformation", "lifestyle", "fitness", "product demos"],
        "platforms": ["Instagram Reels", "TikTok", "YouTube Shorts"],
        "icon": "↔️"
    },
    "Listicle": {
        "full": "Promise → Item 1 → Item 2 → Item N → Summary CTA",
        "description": "Promise N items upfront, deliver each clearly, close with a synthesis CTA. Highly watchable because viewers want to see all N items.",
        "best_for": ["education", "tips", "tools", "recommendations", "myths"],
        "platforms": ["TikTok", "YouTube", "Reels"],
        "icon": "📋"
    },
}

HOOK_ARCHETYPES = {
    "Shock/Controversy": "States a hot take or unexpected claim that challenges assumptions",
    "Question": "Opens with a deeply relatable or provocative question",
    "Statistic": "Leads with a surprising, counterintuitive data point",
    "Story Drop": "Drops mid-story — no setup, straight to the moment of tension",
    "Direct Value": "Immediately promises the viewer specific, tangible value",
    "Pattern Interrupt": "Does/says something unexpected that breaks the scroll reflex",
    "Relatability Mirror": "Mirrors the exact thought or situation the viewer is experiencing",
    "POV/Scenario": "Places the viewer inside a situation using 'You' framing",
    "Cliffhanger Tease": "Reveals the ending first, then promises to explain how",
    "Challenge/Dare": "Directly challenges or dares the viewer to disprove something",
}


# ─────────────────────────────────────────────────────────────────────────────
# Core analysis
# ─────────────────────────────────────────────────────────────────────────────

def analyze_script(groq_client, script_text: str, platform: str = "TikTok",
                   brand_context: str = "") -> dict:
    """
    Full deep script analysis including framework detection and pattern recommendations.
    brand_context: optional brand intelligence injection for alignment scoring.
    """

    brand_section = ""
    if brand_context.strip():
        brand_section = f"""
BRAND CONTEXT (score alignment to this):
{brand_context[:800]}
"""

    framework_list = "\n".join([
        f"- {k}: {v['full']} — {v['description']}"
        for k, v in NARRATIVE_FRAMEWORKS.items()
    ])

    hook_list = "\n".join([f"- {k}: {v}" for k, v in HOOK_ARCHETYPES.items()])

    prompt = f"""Analyze this {platform} script with expert depth.
{brand_section}
SCRIPT:
\"\"\"{script_text}\"\"\"

AVAILABLE NARRATIVE FRAMEWORKS (identify which one this uses):
{framework_list}

AVAILABLE HOOK ARCHETYPES (identify which one this uses):
{hook_list}

Return a JSON object with EXACTLY this structure (all fields required):
{{
  "overview": {{
    "category": "string",
    "sub_category": "string",
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
    "archetype": "exact name from the hook archetypes list above",
    "type": "string (e.g. Question Hook, Shock Hook)",
    "text": "the actual hook line from the script",
    "first_3_seconds": "what happens in the critical first 3 seconds",
    "psychological_trigger": "e.g. Curiosity Gap, FOMO, Fear, Desire, Social Proof",
    "why_it_works": "1 sentence explaining the psychology behind this hook",
    "why_it_fails": "1 sentence on what weakens this hook (or null if strong)",
    "feedback": "specific actionable feedback",
    "improved_version": "a significantly better version of this hook"
  }},
  "narrative_framework": {{
    "detected": "exact framework name from the list above or 'Hybrid' or 'None'",
    "confidence": 0-100,
    "evidence": "quote the part of the script that reveals this framework",
    "execution_quality": "Poor/Fair/Good/Excellent",
    "execution_notes": "what they did well and what broke down in this framework",
    "missing_elements": ["framework element that is missing 1", "missing 2"]
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
    "emotional_intelligence_rating": "Low/Medium/High/Exceptional",
    "feedback": "string"
  }},
  "structure": {{
    "score": 0-100,
    "opening_type": "string",
    "has_pattern_interrupt": true/false,
    "has_clear_cta": true/false,
    "cta_text": "string or null",
    "pacing": "Too Slow/Slow/Perfect/Fast/Too Fast",
    "segments": [
      {{"name": "Hook", "duration": "string", "effectiveness": 0-100}},
      {{"name": "Body", "duration": "string", "effectiveness": 0-100}},
      {{"name": "CTA", "duration": "string", "effectiveness": 0-100}}
    ]
  }},
  "tone_voice": {{
    "score": 0-100,
    "primary_tone": "string",
    "secondary_tone": "string",
    "authenticity_score": 0-100,
    "relatability_score": 0-100,
    "energy_level": "Low/Medium/High/Intense",
    "personality_traits": ["string", "string", "string"]
  }},
  "brand_alignment": {{
    "score": 0-100,
    "aligned_elements": ["what aligns with brand 1", "aligned 2"],
    "misaligned_elements": ["what conflicts with brand 1", "conflict 2"],
    "notes": "string (or 'No brand context provided')"
  }},
  "retention_prediction": {{
    "score": 0-100,
    "drop_off_risk_points": ["string", "string"],
    "strongest_moments": ["string", "string"],
    "predicted_watch_through_rate": "e.g. 65%",
    "virality_potential": "Low/Medium/High/Viral"
  }},
  "pattern_recommendations": [
    {{
      "rank": 1,
      "framework": "framework name",
      "hook_archetype": "hook type",
      "why_better": "specific reason why this pattern would outperform current script for this content",
      "example_opening": "write the first 2 sentences of how this script would start with this pattern",
      "expected_improvement": "e.g. +15 retention, higher shareability"
    }},
    {{
      "rank": 2,
      "framework": "framework name",
      "hook_archetype": "hook type",
      "why_better": "string",
      "example_opening": "string",
      "expected_improvement": "string"
    }},
    {{
      "rank": 3,
      "framework": "framework name",
      "hook_archetype": "hook type",
      "why_better": "string",
      "example_opening": "string",
      "expected_improvement": "string"
    }}
  ],
  "strengths": ["string", "string", "string"],
  "weaknesses": ["string", "string", "string"],
  "actionable_improvements": [
    {{"priority": "High", "area": "string", "suggestion": "string"}},
    {{"priority": "Medium", "area": "string", "suggestion": "string"}},
    {{"priority": "Low", "area": "string", "suggestion": "string"}}
  ],
  "rewritten_hook": "a significantly better version of the opening 15 words"
}}"""

    resp = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000,
        temperature=0.3
    )

    raw = resp.choices[0].message.content.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*",     "", raw)
    raw = re.sub(r"\s*```$",     "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {"error": "Could not parse analysis", "raw": raw[:500]}


def compare_scripts(groq_client, script_a: str, script_b: str) -> dict:
    """Compare two scripts head-to-head."""
    prompt = f"""Compare these two scripts as an elite content strategist.

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
  "framework_winner": "A or B",
  "score_a": 0-100,
  "score_b": 0-100,
  "framework_a": "detected framework",
  "framework_b": "detected framework",
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
    raw = re.sub(r"\s*```$",     "", raw)
    try:
        return json.loads(raw)
    except Exception:
        return {"error": raw[:200]}

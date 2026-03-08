# modules/script_generator.py
"""
EQ-powered script generator.
Uses RAG brand context + emotional intelligence framework
to generate standout, platform-optimized scripts.
"""

EMOTIONAL_FRAMEWORKS = {
    "Hero's Journey": "Take viewer from problem → struggle → transformation → triumph",
    "AIDA": "Attention → Interest → Desire → Action",
    "PAS": "Problem → Agitate → Solution (create pain then relief)",
    "Story Loop": "Open a loop (question/story) → build tension → close loop with payoff",
    "Contrast Arc": "Show the before (relatable pain) → reveal the after (desired outcome)",
    "Curiosity Gap": "Tease an answer → delay → deliver with impact",
    "Social Proof": "Establish credibility → show results → invite viewer into the tribe",
}

HOOK_TYPES = {
    "Controversy": "Start with a hot take or unpopular opinion that challenges assumptions",
    "Question": "Open with a deeply relatable or provocative question",
    "Statistic": "Lead with a shocking, counterintuitive data point",
    "Story": "Drop mid-story — skip the setup, start at the moment of tension",
    "Direct Value": "Immediately promise the viewer something they desperately want",
    "Pattern Interrupt": "Say or do something unexpected that breaks the scroll reflex",
    "Relatability": "Mirror the viewer's exact internal monologue",
}

EQ_EMOTIONS = [
    "Curiosity", "Surprise", "Urgency", "Fear", "Hope",
    "Inspiration", "Validation", "FOMO", "Excitement", "Trust",
    "Nostalgia", "Empathy", "Pride", "Humor", "Awe"
]


def generate_script(
    groq_client,
    topic: str,
    platform: str,
    duration: str,
    tone: str,
    hook_type: str,
    emotional_framework: str,
    target_emotions: list,
    conditions: str,
    brand_context: str = "",
    trend_data: str = ""
) -> str:
    """Generate a full EQ-powered script with brand alignment."""

    brand_section = ""
    if brand_context.strip():
        brand_section = f"""
BRAND CONTEXT (from uploaded brand documents — align everything to this):
{brand_context}
"""

    trend_section = ""
    if trend_data.strip():
        trend_section = f"""
CURRENT TREND DATA (incorporate naturally):
{trend_data}
"""

    emotion_str = ", ".join(target_emotions) if target_emotions else "Curiosity, Inspiration"
    framework_desc = EMOTIONAL_FRAMEWORKS.get(emotional_framework, "")
    hook_desc = HOOK_TYPES.get(hook_type, "")

    system_prompt = """You are the world's top viral content strategist and scriptwriter.
You combine deep emotional intelligence, consumer psychology, and platform mastery 
to create scripts that stop scrolls, hold attention, and drive action.

Your scripts are:
- Psychologically precise — every word serves a purpose
- Emotionally intelligent — they mirror, validate, then elevate the viewer
- Platform-native — they feel organic, not produced
- Brand-authentic — they sound human, not corporate
- Action-driving — they create undeniable momentum toward a CTA

Never write generic content. Every script must feel like it was written specifically 
for this brand, this audience, this moment."""

    prompt = f"""Create a complete, production-ready {platform} script.

TOPIC: {topic}
PLATFORM: {platform}
DURATION: {duration}
TONE: {tone}
HOOK TYPE: {hook_type} — {hook_desc}
EMOTIONAL FRAMEWORK: {emotional_framework} — {framework_desc}
TARGET EMOTIONS TO TRIGGER: {emotion_str}
SPECIAL CONDITIONS: {conditions}
{brand_section}
{trend_section}

Deliver the full script in this format:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎣 HOOK (0-3 seconds) — {hook_type}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Script line]
[Director note: what to show visually]
[Emotion triggered: X at intensity Y/10]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 BODY — {emotional_framework}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Segment 1 — Emotion: X]
[Script lines]
[Visual direction]

[Segment 2 — Emotion: X]
[Script lines]
[Visual direction]

[Segment 3 — Emotion: X]
[Script lines]
[Visual direction]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💥 PATTERN INTERRUPT (if applicable)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[The moment that re-captures attention]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 CTA (last 5 seconds)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[CTA line]
[Why this CTA works psychologically]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 CAPTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Engaging caption that extends the hook]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HASHTAGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[15 targeted hashtags mixing viral + niche]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 EMOTIONAL INTELLIGENCE BREAKDOWN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hook emotion: [emotion + why it works]
Body arc: [emotional journey explanation]
CTA emotion: [why this drives action]
Predicted retention: [X%]
Virality factors: [3 specific reasons this could go viral]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 PRODUCTION NOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pacing: [beats per segment]
Music mood: [specific vibe for background audio]
Text overlays: [key words to highlight on screen]
Thumbnail/Cover frame: [describe the perfect still frame]"""

    resp = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000,
        temperature=0.75,
        stream=True
    )

    return resp  # return stream for live display


def generate_script_variations(groq_client, original_script: str, variation_type: str) -> str:
    """Generate a variation of an existing script."""
    prompts = {
        "More Emotional": "Rewrite this script to be 3x more emotionally resonant. Add vulnerability, stakes, and deeper psychological triggers.",
        "Shorter (30s)": "Condense this to a punchy 30-second version. Keep only what's essential. Every word must earn its place.",
        "Different Hook": "Keep the same content but completely rewrite the hook. Use a radically different psychological trigger.",
        "More Conversational": "Rewrite this to sound like you're talking to your best friend. Remove any corporate or stiff language.",
        "Higher Energy": "Rewrite with significantly more energy, urgency, and momentum. This should feel like an adrenaline shot.",
    }

    instruction = prompts.get(variation_type, "Improve this script significantly.")

    resp = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a viral content strategist. Rewrite scripts with precision and psychological insight."},
            {"role": "user", "content": f"{instruction}\n\nORIGINAL SCRIPT:\n{original_script}"}
        ],
        max_tokens=2000,
        temperature=0.8,
        stream=True
    )
    return resp

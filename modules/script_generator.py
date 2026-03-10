# modules/script_generator.py
"""
EQ-powered script generator.
Integrates:
  - RAG brand documents (uploaded)
  - Live brand intelligence (web-scraped)
  - Topic research data
  - Narrative framework injection
  - Creator style injection
"""

EMOTIONAL_FRAMEWORKS = {
    "Hero's Journey":   "Take viewer from problem → struggle → transformation → triumph. The viewer is the hero.",
    "AIDA":             "Attention → Interest → Desire → Action. Classic persuasion arc.",
    "PAS":              "Problem → Agitate → Solution. Create pain, make it urgent, deliver relief.",
    "BAB":              "Before → After → Bridge. Show painful before, dream after, reveal the bridge.",
    "Story Loop":       "Open a story loop → build tension → close with a satisfying payoff.",
    "Contrast Arc":     "Juxtapose before/after states. Relatable struggle vs. transformed outcome.",
    "Curiosity Gap":    "Tease the answer → withhold → deliver reveal with impact.",
    "Social Proof":     "Credibility → Evidence (results/numbers) → Invitation to join.",
    "Listicle":         "Promise N items → deliver each crisply → summarize with CTA.",
    "Problem-Solution": "State problem → context → solution → proof. Clean and educational.",
}

HOOK_TYPES = {
    "Shock/Controversy":   "Hot take or unpopular opinion that challenges assumptions",
    "Question":            "Deeply relatable or provocative question",
    "Statistic":           "Shocking, counterintuitive data point",
    "Story Drop":          "Drop mid-story — no setup, straight to the tension",
    "Direct Value":        "Immediately promise specific, tangible value",
    "Pattern Interrupt":   "Unexpected statement that breaks the scroll reflex",
    "Relatability Mirror": "Mirror the viewer's exact internal monologue",
    "POV/Scenario":        "Put viewer inside a situation using 'You' framing",
    "Cliffhanger Tease":   "Reveal the ending first, then promise to explain how",
    "Challenge/Dare":      "Directly challenge viewer to disprove something",
}

EQ_EMOTIONS = [
    "Curiosity", "Surprise", "Urgency", "Fear", "Hope",
    "Inspiration", "Validation", "FOMO", "Excitement", "Trust",
    "Nostalgia", "Empathy", "Pride", "Humor", "Awe",
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
    brand_intelligence: str = "",
    topic_research: str = "",
    creator_style: str = "",
    trend_data: str = "",
) -> str:
    """
    Generate a full EQ-powered script.

    Priority of brand context injection:
      1. brand_intelligence (live web-scraped)
      2. brand_context (RAG from uploaded docs)
      3. topic_research (general topic facts)
    """

    # ── Brand/research sections ───────────────────────────────────────────────
    brand_section = ""

    if brand_intelligence.strip():
        brand_section = f"""
═══════════════════════════════════════
LIVE BRAND INTELLIGENCE (web-researched — treat as ground truth):
{brand_intelligence}
═══════════════════════════════════════

CRITICAL BRAND RULES:
- Every claim must align with the brand's actual products, values, and voice above
- Use the audience pain points and desires to shape the emotional arc
- Reference real features/USPs, not generic claims
- Match the brand's CTA style exactly
- Do NOT invent features or make claims not supported by the research
"""
    elif brand_context.strip():
        brand_section = f"""
BRAND CONTEXT (from uploaded documents):
{brand_context}

Align all messaging, tone, and CTAs to this brand identity.
"""

    if topic_research.strip():
        brand_section += f"""
TOPIC RESEARCH DATA (use real stats and facts from this):
{topic_research}
"""

    # ── Creator style injection ───────────────────────────────────────────────
    style_section = ""
    if creator_style.strip():
        style_section = f"""
CREATOR STYLE (write in this exact voice):
{creator_style}
"""

    # ── Trend injection ───────────────────────────────────────────────────────
    trend_section = ""
    if trend_data.strip():
        trend_section = f"""
CURRENT TREND DATA (weave in naturally):
{trend_data}
"""

    # ── Build prompt ──────────────────────────────────────────────────────────
    emotion_str = ", ".join(target_emotions) if target_emotions else "Curiosity, Inspiration"
    framework_desc = EMOTIONAL_FRAMEWORKS.get(emotional_framework, "")
    hook_desc      = HOOK_TYPES.get(hook_type, "")

    system_prompt = """You are the world's top viral content strategist and scriptwriter.
You combine deep emotional intelligence, consumer psychology, and platform mastery
to create scripts that stop scrolls, hold attention, and drive action.

Your scripts are:
- Psychologically precise — every word earns its place
- Brand-authentic — they feel like the brand, not like AI
- Platform-native — they feel organic, not produced
- Emotionally intelligent — they mirror, validate, then elevate the viewer
- Data-backed — real stats, real features, real proof points

When brand intelligence is provided, you MUST use it.
Never invent product features or make claims not in the brief.
Every script must feel written for THIS brand, THIS audience, THIS moment."""

    prompt = f"""Create a high-converting {platform} script.

BRIEF:
- Topic: {topic}
- Platform: {platform}
- Duration: {duration}
- Tone: {tone}
- Hook Type: {hook_type} — {hook_desc}
- Narrative Framework: {emotional_framework} — {framework_desc}
- Target Emotions to Trigger: {emotion_str}
- Special Conditions: {conditions if conditions else "None"}
{brand_section}{style_section}{trend_section}

OUTPUT FORMAT — write the complete script in this structure:

🎣 HOOK (0-3s):
[The exact opening words — use {hook_type} hook technique]

📖 BODY:
[Main content — follow {emotional_framework} framework — use brand facts and research]

🎯 CTA:
[Clear, on-brand call to action]

---
📊 PATTERN USED: [framework name] + [hook type]
🧠 PSYCHOLOGY: [1 sentence on why this combination works for this topic/brand]
✅ BRAND ALIGNMENT: [1 sentence on how it reflects the brand intelligence above]

Rules:
- Write ONLY the script and the pattern note — no meta-commentary
- Make it feel real, not written by AI
- Every sentence must earn its place
- The hook must make stopping the scroll feel involuntary"""

    resp = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": prompt}
        ],
        max_tokens=1200,
        temperature=0.7,
        stream=True
    )

    full = ""
    for chunk in resp:
        delta = chunk.choices[0].delta.content
        if delta:
            full += delta
            yield delta

    return full

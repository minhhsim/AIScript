# modules/script_generator.py
"""
EQ-Powered Script Generator — v2
Upgrades:
  - TemperatureRouter: keyword scoring → winner-takes-all → LLM fallback → phase overrides
  - Human-first prompt engineering: anti-AI language, trending slang, platform-native voice
  - Per-platform word budget + speech rhythm rules
  - Humanization layer: filler patterns, sentence length variation, real people talk
"""

import hashlib

# ─────────────────────────────────────────────────────────────────────────────
# TEMPERATURE ROUTER (from TemperatureRouter Implementation Deep Dive)
# ─────────────────────────────────────────────────────────────────────────────

LOW_SIGNALS = [
    "competitor", "analysis", "compare", "metrics",
    "data", "analytics", "report", "audit",
    "benchmark", "performance", "numbers", "stats",
    "breakdown", "research", "fact-check",
    "compliance", "brand guidelines", "measurement",
    "track", "kpi", "roi", "percentage", "conversion",
]

MEDIUM_SIGNALS = [
    "strategy", "plan", "calendar", "schedule",
    "framework", "educational", "explain",
    "tutorial", "how-to", "guide", "outline",
    "structure", "format", "recommend",
    "optimize", "audience", "positioning",
    "funnel", "content plan", "organize", "series",
    "roadmap", "overview", "walkthrough",
]

HIGH_SIGNALS = [
    "script", "hook", "write", "creative",
    "ad copy", "caption", "hashtag", "skit",
    "comedy", "funny", "brainstorm", "ideas",
    "carousel", "reel", "story", "narrative",
    "trend", "viral", "variation", "alternate",
    "rewrite", "adapt", "remix", "generate",
    "draft", "compose", "craft", "create",
    "produce", "build", "make", "engaging",
    "entertaining", "catchy", "punchy", "bold",
]

PHASE_OVERRIDES = {
    "phase_1": 0.5,
    "phase_2": 0.2,
    "phase_4": 0.5,
}

_fallback_cache: dict = {}


def _count_signals(text: str, signals: list) -> int:
    t = text.lower()
    return sum(1 for s in signals if s in t)


def _llm_fallback(groq_client, request: str) -> float:
    key = hashlib.md5(request.encode()).hexdigest()
    if key in _fallback_cache:
        return _fallback_cache[key]
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a request classifier. "
                        "Reply with ONE word only: LOW, MEDIUM, or HIGH. "
                        "LOW=analytical/factual. MEDIUM=strategy/planning. HIGH=creative/script/hook. "
                        "No other output."
                    ),
                },
                {"role": "user", "content": request},
            ],
            max_tokens=5,
            temperature=0.0,
        )
        label = resp.choices[0].message.content.strip().upper()
        result = {"LOW": 0.2, "MEDIUM": 0.5, "HIGH": 0.9}.get(label, 0.5)
    except Exception:
        result = 0.5
    _fallback_cache[key] = result
    return result


class TemperatureRouter:
    def __init__(self, groq_client):
        self._client         = groq_client
        self.last_classification = "none"
        self.last_temperature    = 0.9
        self.last_band           = "HIGH"

    def route(self, request: str, phase: str = "phase_3") -> float:
        if phase in PHASE_OVERRIDES:
            temp = PHASE_OVERRIDES[phase]
            self.last_classification = f"phase_override({phase})"
            self.last_temperature    = temp
            self.last_band = {0.2:"LOW",0.5:"MEDIUM",0.9:"HIGH"}[temp]
            return temp
        return self._classify(request)

    def _classify(self, request: str) -> float:
        lo = _count_signals(request, LOW_SIGNALS)
        me = _count_signals(request, MEDIUM_SIGNALS)
        hi = _count_signals(request, HIGH_SIGNALS)

        # Weighted tie-break: HIGH >=2 and others <=1 → HIGH wins
        if hi >= 2 and lo <= 1 and me <= 1:
            self.last_classification = f"keyword_HIGH(hi={hi},weighted)"
            self.last_temperature = 0.9; self.last_band = "HIGH"; return 0.9

        if lo > me and lo > hi:
            self.last_classification = f"keyword_LOW(lo={lo})"
            self.last_temperature = 0.2; self.last_band = "LOW"; return 0.2

        if hi > me and hi > lo:
            self.last_classification = f"keyword_HIGH(hi={hi})"
            self.last_temperature = 0.9; self.last_band = "HIGH"; return 0.9

        if me > 0:
            self.last_classification = f"keyword_MED(me={me})"
            self.last_temperature = 0.5; self.last_band = "MEDIUM"; return 0.5

        temp = _llm_fallback(self._client, request)
        self.last_classification = f"llm_fallback→{temp}"
        self.last_temperature = temp
        self.last_band = {0.2:"LOW",0.5:"MEDIUM",0.9:"HIGH"}.get(temp,"MEDIUM")
        return temp


# ─────────────────────────────────────────────────────────────────────────────
# SCRIPT CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

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
    "Curiosity","Surprise","Urgency","Fear","Hope",
    "Inspiration","Validation","FOMO","Excitement","Trust",
    "Nostalgia","Empathy","Pride","Humor","Awe",
]

PLATFORM_RULES = {
    "TikTok": {
        "word_budget":    "60-120 words spoken aloud",
        "speech_style":   "Gen Z casual — contractions always, fragments OK, energy HIGH",
        "hook_window":    "first 1-2 seconds = 5-8 words max",
        "pacing":         "fast cuts implied, 1 idea per beat, punchy",
        "avoid":          "formal intros, slow build-up, corporate speak, padding",
        "trending_phrases": ["real talk","not gonna lie","here's the thing",
                             "this is your sign to","POV:","no cap","lowkey",
                             "the way that","main character energy","it's giving"],
    },
    "YouTube Shorts": {
        "word_budget":    "80-150 words spoken aloud",
        "speech_style":   "energetic but clear — hook instantly, one big insight, hard stop",
        "hook_window":    "first 2 seconds — opening line IS the whole point",
        "pacing":         "medium, punchy sentences, no filler, re-hook at midpoint",
        "avoid":          "long intros, subscribe asks mid-script, padding, weak endings",
        "trending_phrases": ["wait for it","this changes everything",
                             "here's what most people miss",
                             "the secret nobody talks about",
                             "I tried this so you don't have to"],
    },
    "Instagram Reels": {
        "word_budget":    "50-100 words spoken aloud",
        "speech_style":   "aspirational and warm — relatable, community feel, soft sell",
        "hook_window":    "first 1.5 seconds — visual hook implied in opening line",
        "pacing":         "smooth emotional beats, subtle CTA, cinematic rhythm",
        "avoid":          "aggressive selling, clickbait, overly formal, try-hard energy",
        "trending_phrases": ["if you needed a sign","be the person you needed",
                             "normalize","this is your reminder",
                             "hot girl tip","the algorithm brought you here"],
    },
    "YouTube Long-form": {
        "word_budget":    "800-1500 words (full video script)",
        "speech_style":   "conversational expert — smart friend energy, not professor energy",
        "hook_window":    "first 30 seconds must justify the full watch time",
        "pacing":         "chapter structure, re-hooks every 90s, payoff at midpoint",
        "avoid":          "monotone delivery cues, walls of text, no personality, boring transitions",
        "trending_phrases": ["here's what I found out","I tested this for 30 days",
                             "the part nobody mentions","and this is the part that shocked me",
                             "let me break this down"],
    },
    "LinkedIn": {
        "word_budget":    "150-300 words",
        "speech_style":   "professional but human — first-person story, zero buzzword soup",
        "hook_window":    "first line is a standalone statement worth reading alone",
        "pacing":         "short paragraphs, one idea per line, whitespace is content",
        "avoid":          "jargon, humble-brag openers, 'excited to announce', passive voice",
        "trending_phrases": ["unpopular opinion:","I used to think that",
                             "after [X] years I realised","nobody talks about this enough",
                             "the real reason","here's my honest take"],
    },
}

HUMANIZATION_RULES = """
════════════════════════════════════════════
HUMANIZATION RULES — APPLY ALL OF THESE WITHOUT EXCEPTION:
════════════════════════════════════════════

SENTENCE VARIETY (most important rule):
- Mix ultra-short (3-5 words) WITH medium (10-15 words) sentences constantly
- NEVER write 3+ sentences of the same length in a row
- Use deliberate fragments. Like this. They add punch.
- Start sentences with And, But, Because — real people do

CONTRACTIONS — MANDATORY:
- you're / don't / it's / I've / that's / we're / can't / won't
- Only drop a contraction for deliberate dramatic emphasis

SPOKEN RHYTHM (write for ears, not eyes):
- Every line should sound natural if spoken aloud
- Use dashes for natural mid-thought pauses — like this
- Use "..." for building tension that trails off...
- Put commas where a speaker would breathe

BANNED AI PHRASES — NEVER USE:
- "In today's fast-paced world" / "It's no secret that" / "Look no further"
- "game-changer" / "leverage" / "synergy" / "dive into" / "delve into"
- "In conclusion" / "To summarize" / "As we can see" / "It's worth noting"
- "Absolutely!" / "Certainly!" / "Great question!" / "Of course!"
- "Furthermore" / "Moreover" / "Additionally" / "In this day and age"
- Any opener that sounds like a blog post title

REAL HUMAN PATTERNS — USE THESE:
- Rhetorical check-ins: "You know what's wild?" / "But here's the thing..."
- Self-correction for authenticity: "Actually — scratch that."
- Direct address: "I'm talking to YOU — the one who..."
- Hyper-specific details: "3 weeks ago" not "recently" / "$47" not "a small fee"
- Unscripted openers: "Look..." / "Okay so..." / "Here's what happened."
- Vulnerability: admitting a mistake or surprising belief builds instant trust

TRENDING ENERGY BY PLATFORM:
- TikTok: raw, unfiltered, self-aware about being on camera
- Reels: aesthetic, warm, feels like a text from a friend
- YouTube: authoritative but conversational, story first
- LinkedIn: contrarian take that earns its ending

STORYTELLING TEXTURE:
- Anchor one specific sensory detail in every story
- "Because" is the most persuasive word in scripts — use it
- End each sentence with the word that carries the most weight
- The CTA must feel earned from the story, not bolted on the end
════════════════════════════════════════════
"""


# ─────────────────────────────────────────────────────────────────────────────
# GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

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
    phase: str = "phase_3",
):
    """
    Generate a humanized, temperature-routed, EQ-powered script.
    Yields text chunks for streaming.
    Last yielded chunk is a metadata comment for UI display.
    """

    # ── Temperature routing ───────────────────────────────────────────────────
    router = TemperatureRouter(groq_client)
    classification_input = f"{topic} {platform} write script hook creative {tone} {emotional_framework}"
    temperature = router.route(classification_input, phase)

    # ── Platform context ──────────────────────────────────────────────────────
    p_key   = platform if platform in PLATFORM_RULES else "TikTok"
    p_rules = PLATFORM_RULES[p_key]
    phrases = ", ".join(f'"{p}"' for p in p_rules["trending_phrases"][:5])

    # ── Brand / research ──────────────────────────────────────────────────────
    brand_section = ""
    if brand_intelligence.strip():
        brand_section = (
            f"\n{'='*40}\n"
            f"LIVE BRAND INTELLIGENCE (web-researched — ground truth only):\n"
            f"{brand_intelligence}\n"
            f"{'='*40}\n"
            f"RULES: Use ONLY these real facts. Zero invented features. "
            f"Reference specific USPs, pricing, product names, audience pain points.\n"
        )
    elif brand_context.strip():
        brand_section = (
            f"\nBRAND CONTEXT (uploaded documents):\n{brand_context}\n"
            f"Align ALL messaging, tone, CTAs, and vocabulary to this identity.\n"
        )
    if topic_research.strip():
        brand_section += (
            f"\nTOPIC RESEARCH — real stats/facts "
            f"(weave in naturally, don't just list):\n{topic_research}\n"
        )

    style_section = (
        f"\nCREATOR VOICE — write in THIS exact style only:\n{creator_style}\n"
        if creator_style.strip() else ""
    )
    trend_section = (
        f"\nTRENDS CONTEXT (reference naturally, don't force):\n{trend_data}\n"
        if trend_data.strip() else ""
    )

    framework_desc = EMOTIONAL_FRAMEWORKS.get(emotional_framework, "")
    hook_desc      = HOOK_TYPES.get(hook_type, "")
    emotion_str    = ", ".join(target_emotions) if target_emotions else "Curiosity, Inspiration"

    temp_mode = {
        0.2: "PRECISION (0.2) — factual, grounded, reproducible. Accuracy over flair.",
        0.5: "BALANCED (0.5) — strategic clarity with moderate creative energy.",
        0.9: "MAX CREATIVE (0.9) — push hard. Don't write the obvious first draft. Write the 10th.",
    }.get(temperature, "Balanced.")

    # ── System prompt ─────────────────────────────────────────────────────────
    system_prompt = f"""You are a viral script writer who has written for creators with 10M+ followers across TikTok, YouTube, and Instagram.

Your scripts feel like they came from a real person — not a content agency, not a template, not AI.
They get saved. They get shared. They make people feel seen.

TEMPERATURE MODE: {temp_mode}

PLATFORM: {platform}
Word budget: {p_rules['word_budget']}
Speech style: {p_rules['speech_style']}
Hook window: {p_rules['hook_window']}
Pacing: {p_rules['pacing']}
AVOID: {p_rules['avoid']}
Trending phrases to consider: {phrases}

{HUMANIZATION_RULES}

NARRATIVE FRAMEWORK: {emotional_framework}
{framework_desc}

HOOK TECHNIQUE: {hook_type}
{hook_desc}

TARGET EMOTIONS TO TRIGGER: {emotion_str}
Don't just mention these emotions — architect the script so the viewer FEELS them through word choice, rhythm, and specificity.

{brand_section}{style_section}{trend_section}

SELF-CHECK before outputting (fix anything that fails):
✓ Does the hook stop a scroll in under 2 seconds?
✓ Does every single sentence earn its place?
✓ Could a real human have written this naturally?
✓ Is there at least one hyper-specific detail that makes it feel real?
✓ Does the CTA feel earned by the story — or bolted on?"""

    # ── User prompt ───────────────────────────────────────────────────────────
    prompt = f"""Write a {platform} script.

BRIEF:
Topic: {topic}
Duration: {duration}
Tone: {tone}
Hook type: {hook_type}
Framework: {emotional_framework}
Special conditions: {conditions if conditions.strip() else "None"}

OUTPUT — use exactly this structure, no extra commentary:

🎣 HOOK [{p_rules['hook_window']}]:
[The exact opening words. {hook_type} technique. Make it impossible to scroll past.]

📖 BODY:
[Main content. {emotional_framework} arc. Spoken rhythm. Human phrasing. Platform-native energy. Use contractions. Vary sentence length.]

🎯 CTA:
[One clear action. Feels natural — not bolted on.]

---
🌡️ TEMPERATURE: {temperature} ({router.last_band}) — classified via {router.last_classification}
📊 PATTERN: {emotional_framework} + {hook_type}
🧠 WHY IT WORKS: [The psychological mechanism behind this combination in one sentence]
✍️ MOST HUMAN MOMENT: [The single most unexpected/human choice you made in this script]"""

    # ── Stream ────────────────────────────────────────────────────────────────
    resp = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": prompt},
        ],
        max_tokens=1400,
        temperature=temperature,
        stream=True,
    )

    for chunk in resp:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta

    # Metadata tag for UI to parse temperature band
    yield f"\n\n<!-- ROUTER:{temperature}:{router.last_band}:{router.last_classification} -->"

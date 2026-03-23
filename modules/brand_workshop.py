# modules/brand_workshop.py
"""
Brand Workshop — Script Intelligence Intake
Inspired by wowai.ch/brandmaker/workshop (13-module brand-building framework)
Adapted for script generation: collects exactly what the AI needs to write
on-brand, human, platform-native scripts.

6 modules → Groq synthesises answers → structured brand_context string
injected into every script generation call.

Modules:
  0  Identity & Scope       (wowai: Setup & Scope)
  1  DNA & Purpose          (wowai: Company DNA + Purpose Engine)
  2  Your Audience          (wowai: Personas & Stakeholders)
  3  What Makes You Different (wowai: Value Proposition + Competition)
  4  Brand Voice            (wowai: Archetypes + Tone of Voice)
  5  Script Rules           (ContentIQ-specific: hooks, CTAs, no-gos)
"""

import json

# ─────────────────────────────────────────────────────────────────────────────
# MODULE METADATA
# ─────────────────────────────────────────────────────────────────────────────

MODULES = [
    {
        "id":    0,
        "title": "Identity & Scope",
        "icon":  "🏢",
        "time":  "3 min",
        "desc":  "What your brand is and the boundaries it operates within",
        "wowai": "Setup & Scope",
    },
    {
        "id":    1,
        "title": "DNA & Purpose",
        "icon":  "🧬",
        "time":  "5 min",
        "desc":  "Why you exist and what drives everything you do",
        "wowai": "Company DNA + Purpose Engine",
    },
    {
        "id":    2,
        "title": "Your Audience",
        "icon":  "👥",
        "time":  "5 min",
        "desc":  "Who you speak to and what lives inside their heads",
        "wowai": "Personas & Stakeholders",
    },
    {
        "id":    3,
        "title": "What Makes You Different",
        "icon":  "⚡",
        "time":  "5 min",
        "desc":  "Your USP, proof points, and how you beat alternatives",
        "wowai": "Value Proposition + Competition",
    },
    {
        "id":    4,
        "title": "Brand Voice",
        "icon":  "🎙️",
        "time":  "5 min",
        "desc":  "Your archetype, personality, and how you actually sound",
        "wowai": "Archetypes + Tone of Voice",
    },
    {
        "id":    5,
        "title": "Script Rules",
        "icon":  "📋",
        "time":  "5 min",
        "desc":  "Hooks, CTAs, forbidden topics, and your winning content patterns",
        "wowai": "ContentIQ Script Intelligence (exclusive)",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# ARCHETYPE OPTIONS (wowai: Module 7)
# ─────────────────────────────────────────────────────────────────────────────

ARCHETYPES = {
    "The Hero":       "Brave, determined, always overcoming. Inspires action and conquest.",
    "The Creator":    "Imaginative, expressive, builds things of meaning and beauty.",
    "The Sage":       "Knowledgeable, trusted advisor. Truth-seeking, educational.",
    "The Everyman":   "Relatable, grounded, down-to-earth. Everyone's friend.",
    "The Rebel":      "Disrupts norms, challenges authority. Raw and unfiltered.",
    "The Explorer":   "Adventurous, freedom-seeking, authentic and restless.",
    "The Caregiver":  "Nurturing, empathetic, puts others first. Warm and safe.",
    "The Jester":     "Playful, funny, brings lightness. Wit over wisdom.",
    "The Lover":      "Passionate, intimate, emotionally intense. Desire-driven.",
    "The Ruler":      "Authoritative, premium, commands respect and status.",
    "The Magician":   "Transformational, visionary, makes the impossible happen.",
    "The Innocent":   "Optimistic, pure, hopeful. Simple and sincere.",
}

# ─────────────────────────────────────────────────────────────────────────────
# VALUE SETS (wowai: Module 1 + 4)
# ─────────────────────────────────────────────────────────────────────────────

BRAND_VALUES = [
    "Authenticity", "Innovation", "Community", "Excellence", "Simplicity",
    "Boldness", "Empathy", "Transparency", "Playfulness", "Education",
    "Sustainability", "Inclusion", "Speed", "Trust", "Freedom",
    "Ambition", "Warmth", "Expertise", "Disruption", "Transformation",
]

VOICE_ADJECTIVES = [
    "Confident", "Warm", "Playful", "Direct", "Inspiring",
    "Authoritative", "Conversational", "Bold", "Witty", "Empathetic",
    "Energetic", "Calm", "Premium", "Relatable", "Edgy",
    "Professional", "Passionate", "Humble", "Sharp", "Raw",
]

PRICE_POSITIONS = ["Budget / Accessible", "Mid-range", "Premium", "Luxury"]

PLATFORMS = ["TikTok", "Instagram Reels", "YouTube Shorts", "YouTube Long-form",
             "LinkedIn", "Facebook", "Twitter/X", "Podcast"]

HOOK_STYLES = [
    "Shock/Controversy — hot take that challenges assumptions",
    "Question — deeply relatable or provocative",
    "Statistic — shocking, counterintuitive data",
    "Story Drop — mid-story, no setup, straight to tension",
    "Direct Value — immediately promise specific value",
    "Pattern Interrupt — unexpected statement breaks scroll",
    "Relatability Mirror — mirrors viewer's internal monologue",
    "POV/Scenario — puts viewer inside a situation",
    "Cliffhanger — reveal ending first, then explain how",
    "Challenge/Dare — directly challenges viewer to disprove",
]

CTA_STYLES = [
    "Follow for more like this",
    "Comment your answer / experience",
    "Share this with someone who needs it",
    "Click the link in bio",
    "Book a call / DM me",
    "Try it yourself (challenge CTA)",
    "Save this for later",
    "Watch the next video",
    "Join the community / newsletter",
    "Buy now / Limited time offer",
]


# ─────────────────────────────────────────────────────────────────────────────
# BRAND CONTEXT SYNTHESISER
# Takes raw answers dict → Groq → structured brand_context string
# ─────────────────────────────────────────────────────────────────────────────

def synthesise_brand_context(groq_client, answers: dict) -> str:
    """
    Convert raw workshop answers into a structured brand_context string
    that the script generator can inject directly into prompts.
    """
    answers_json = json.dumps(answers, indent=2, ensure_ascii=False)

    resp = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a brand strategist converting a brand workshop into a "
                    "script writing brief. Be specific and actionable. "
                    "Write in present tense. No vague generalities. "
                    "This brief will be injected into an AI script generator — "
                    "every sentence must tell the writer something specific they can USE."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Convert these brand workshop answers into a structured script brief.\n\n"
                    f"WORKSHOP ANSWERS:\n{answers_json}\n\n"
                    f"OUTPUT FORMAT — use exactly these sections:\n\n"
                    f"## BRAND IDENTITY\n"
                    f"[Brand name, what they do, price position, primary platforms — 2-3 sentences]\n\n"
                    f"## MISSION & BELIEF\n"
                    f"[Why they exist, what they fight for, core belief — 2 sentences]\n\n"
                    f"## TARGET AUDIENCE\n"
                    f"[Specific person: age, situation, pain point, deepest desire — be hyper-specific]\n\n"
                    f"## AUDIENCE'S OWN WORDS\n"
                    f"[Actual phrases/vocabulary the audience uses — list 5-8 specific phrases]\n\n"
                    f"## USP & PROOF POINTS\n"
                    f"[What makes them different + 3 specific proof points with numbers if available]\n\n"
                    f"## BRAND VOICE\n"
                    f"[Archetype, 3 personality traits, sounds like who, energy level — actionable]\n\n"
                    f"## ALWAYS SAY / NEVER SAY\n"
                    f"Always: [5 phrases/words they use]\n"
                    f"Never: [5 phrases/words they avoid]\n\n"
                    f"## SCRIPT RULES\n"
                    f"Preferred hook: [specific style]\n"
                    f"Preferred CTA: [specific action]\n"
                    f"Always mention: [topics, features, values]\n"
                    f"Never mention: [forbidden topics]\n"
                    f"Winning content pattern: [what has worked before]\n\n"
                    f"## SAMPLE BRAND VOICE SENTENCE\n"
                    f"[Write ONE example sentence in their exact brand voice — "
                    f"use their adjectives, their audience's words, their energy. "
                    f"This is the tone target for every script.]\n\n"
                    f"Be specific. Be concrete. If information is missing, infer from what's given."
                ),
            },
        ],
        max_tokens=1200,
        temperature=0.3,
    )

    return resp.choices[0].message.content.strip()


# ─────────────────────────────────────────────────────────────────────────────
# SAVE / LOAD workshop answers from session state
# ─────────────────────────────────────────────────────────────────────────────

WORKSHOP_KEY = "brand_workshop_answers"
CONTEXT_KEY  = "brand_workshop_context"
COMPLETE_KEY = "brand_workshop_complete"


def get_answers(st) -> dict:
    return st.session_state.get(WORKSHOP_KEY, {})


def save_answers(st, answers: dict):
    st.session_state[WORKSHOP_KEY] = answers


def get_context(st) -> str:
    return st.session_state.get(CONTEXT_KEY, "")


def set_context(st, context: str):
    st.session_state[CONTEXT_KEY]  = context
    st.session_state[COMPLETE_KEY] = True


def is_complete(st) -> bool:
    return bool(st.session_state.get(COMPLETE_KEY, False))


def reset_workshop(st):
    for k in (WORKSHOP_KEY, CONTEXT_KEY, COMPLETE_KEY):
        st.session_state.pop(k, None)

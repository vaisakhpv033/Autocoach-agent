"""Gemini 3.8 Live Voice Management Module.

Provides cataloging, validation, and dynamic selection of Google Gemini 3.8 Live
prebuilt voices and custom voice IDs.
"""

import random
from typing import Optional, Literal

# Complete catalog of Google Gemini 3.8 Live 30 Curated Studio Voices
# Grouped by presentation and tone descriptions from Gemini API docs
GEMINI_MALE_VOICES: dict[str, str] = {
    "Puck": "Upbeat, energetic, engaging",
    "Charon": "Informative, serious, mature",
    "Fenrir": "Excitable, intense, animated",
    "Orus": "Firm, direct, confident",
    "Enceladus": "Breathy, thoughtful",
    "Iapetus": "Clear, articulate",
    "Umbriel": "Easy-going, relaxed",
    "Algieba": "Smooth, composed",
    "Algenib": "Gravelly, textured",
    "Rasalgethi": "Informative, measured",
    "Alnilam": "Firm, grounded",
    "Schedar": "Even, neutral",
    "Gacrux": "Mature, experienced",
    "Achird": "Friendly, approachable",
    "Zubenelgenubi": "Casual, conversational",
    "Sadachbia": "Lively, expressive",
    "Sadaltager": "Knowledgeable, professional",
}

GEMINI_FEMALE_VOICES: dict[str, str] = {
    "Aoede": "Breezy, natural, conversational",
    "Kore": "Firm, decisive, assertive",
    "Leda": "Youthful, bright",
    "Callirrhoe": "Easy-going, pleasant",
    "Autonoe": "Bright, vibrant",
    "Despina": "Smooth, calm",
    "Erinome": "Clear, direct",
    "Laomedeia": "Upbeat, energetic",
    "Achernar": "Soft, gentle",
    "Pulcherrima": "Forward, confident",
    "Vindemiatrix": "Gentle, polite",
    "Sulafat": "Warm, reassuring",
    "Zephyr": "Bright, friendly",
}

ALL_PREBUILT_VOICES: dict[str, str] = {**GEMINI_MALE_VOICES, **GEMINI_FEMALE_VOICES}
VOICE_NAME_LOOKUP: dict[str, str] = {name.lower(): name for name in ALL_PREBUILT_VOICES}


def normalize_voice_name(voice_name: Optional[str]) -> Optional[str]:
    """Validates and normalizes voice name to official Gemini capitalization.
    
    If the voice is a custom voice ID (e.g. 'voice_...' or 'voicekey_...'),
    it returns it verbatim.
    """
    if not voice_name:
        return None
    cleaned = voice_name.strip()
    # Check prebuilt catalog (case-insensitive)
    lower = cleaned.lower()
    if lower in VOICE_NAME_LOOKUP:
        return VOICE_NAME_LOOKUP[lower]
    # Allow custom voice ID or extended voice library ID
    if cleaned.startswith("voice_") or cleaned.startswith("voicekey_"):
        return cleaned
    return cleaned


def resolve_voice(
    voice: Optional[str] = None,
    gender: Optional[str] = None,
    temperament: Optional[str] = None,
    default_fallback: str = "Puck",
) -> str:
    """Dynamically resolves the best Gemini 3.8 voice based on parameters.
    
    Resolution Priority:
    1. Explicit `voice` parameter (validated against catalog or passed as custom ID)
    2. Gender-matched pool with optional temperament preference
    3. Random voice from selected gender
    4. Default fallback voice ('Puck' or 'Aoede')
    """
    # 1. Explicit voice provided
    normalized = normalize_voice_name(voice)
    if normalized:
        return normalized

    # 2. Gender resolution
    norm_gender: Optional[Literal["male", "female"]] = None
    if gender:
        g = gender.strip().lower()
        if g in ["male", "m", "man"]:
            norm_gender = "male"
        elif g in ["female", "f", "woman"]:
            norm_gender = "female"

    target_pool = (
        GEMINI_MALE_VOICES
        if norm_gender == "male"
        else GEMINI_FEMALE_VOICES
        if norm_gender == "female"
        else ALL_PREBUILT_VOICES
    )

    # 3. Temperament matching if provided
    if temperament:
        temp_lower = temperament.strip().lower()
        matching_voices = [
            v_name
            for v_name, desc in target_pool.items()
            if temp_lower in desc.lower()
        ]
        if matching_voices:
            return random.choice(matching_voices)

    # 4. Random choice from pool or fallback
    if target_pool:
        return random.choice(list(target_pool.keys()))

    return default_fallback

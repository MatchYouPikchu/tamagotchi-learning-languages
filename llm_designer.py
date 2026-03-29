"""LLM-powered pet designer — generates appearance from natural language descriptions."""

import json
import os

SYSTEM_PROMPT = """You are a creative pet designer for a kawaii virtual pet game.
Given a user's description, generate an appearance configuration as JSON.

The appearance MUST use ONLY these options:

- body_color: [R, G, B] (any RGB values 0-255)
- accent_color: [R, G, B] (any RGB values 0-255, used for ear inner/highlights)
- pattern: "solid" | "spots" | "stripes"
- pattern_color: [R, G, B] or null (only if pattern is not "solid")
- hat: null | "beret" | "crown" | "tophat" | "flower" | "bow" | "helmet" | "propeller"
- glasses: null | "round" | "cat_eye" | "sunglasses" | "monocle"
- scarf: null | "red" | "blue" | "rainbow" | "gold"
- collar: null | "bell" | "bowtie" | "bandana" | "tag"
- special: null | "sparkle_eyes" | "freckles" | "star_cheeks" | "rosy_cheeks"
- fur_style: null | "short" | "fluffy" | "long" | "curly" | "spiky" | "mohawk"
- tail_style: null | "normal" | "fluffy" | "curly" | "short" | "long" | "ribbon"
- eye_style: null | "normal" | "big" | "sleepy" | "sparkly" | "wink" | "dot"
- ear_style: null | "normal" | "floppy" | "pointy" | "round" | "tiny" | "big"
- personality: "playful" | "brave" | "sleepy" | "curious" | "mischievous" | "gentle"
- suggested_name: a fun name that fits the theme (string)
- flavor_text: a short (under 50 chars) fun description of this pet's personality

Your creative value is in choosing colors, accessories, and personality that tell a
cohesive story from the user's prompt. Make harmonious color choices.

IMPORTANT — Incremental vs. full design:
- If the user's request modifies specific aspects (e.g., "add a hat", "change fur to mohawk",
  "make eyes sparkly"), respond with ONLY the fields being changed. Omit all unchanged fields.
- If the user's request is a full redesign (e.g., "make a pirate cat", "design a space puppy",
  "I want a golden royal pet"), include ALL fields for a complete look.
- When the pet's current appearance is provided, respect it — only override what the user asked for.

Respond with ONLY valid JSON, no markdown, no explanation."""

VALID_HATS = {None, "beret", "crown", "tophat", "flower", "bow", "helmet", "propeller"}
VALID_GLASSES = {None, "round", "cat_eye", "sunglasses", "monocle"}
VALID_SCARVES = {None, "red", "blue", "rainbow", "gold"}
VALID_COLLARS = {None, "bell", "bowtie", "bandana", "tag"}
VALID_SPECIALS = {None, "sparkle_eyes", "freckles", "star_cheeks", "rosy_cheeks"}
VALID_PATTERNS = {"solid", "spots", "stripes"}
VALID_FUR_STYLES = {None, "short", "fluffy", "long", "curly", "spiky", "mohawk"}
VALID_TAIL_STYLES = {None, "normal", "fluffy", "curly", "short", "long", "ribbon"}
VALID_EYE_STYLES = {None, "normal", "big", "sleepy", "sparkly", "wink", "dot"}
VALID_EAR_STYLES = {None, "normal", "floppy", "pointy", "round", "tiny", "big"}


def _validate_color(value):
    """Validate and clamp an RGB color list."""
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        return None
    return [max(0, min(255, int(c))) for c in value]


def _validate_appearance(data, partial=False):
    """Validate and sanitize LLM output to only allowed values.

    Args:
        data: dict of appearance fields from LLM output.
        partial: if True, only validate/return fields present in data (for incremental updates).
    """
    result = {}

    # Colors — only include if present (or if full mode)
    if "body_color" in data or not partial:
        bc = _validate_color(data.get("body_color"))
        result["body_color"] = bc if bc else [200, 160, 80]

    if "accent_color" in data or not partial:
        ac = _validate_color(data.get("accent_color"))
        result["accent_color"] = ac

    # Pattern
    if "pattern" in data or not partial:
        pattern = data.get("pattern", "solid")
        result["pattern"] = pattern if isinstance(pattern, str) and pattern in VALID_PATTERNS else "solid"

    if "pattern_color" in data or not partial:
        pc = _validate_color(data.get("pattern_color"))
        if result.get("pattern") == "solid":
            result["pattern_color"] = None
        else:
            result["pattern_color"] = pc

    # Accessories
    for field, valid_set in [
        ("hat", VALID_HATS), ("glasses", VALID_GLASSES),
        ("scarf", VALID_SCARVES), ("collar", VALID_COLLARS),
        ("special", VALID_SPECIALS), ("fur_style", VALID_FUR_STYLES),
        ("tail_style", VALID_TAIL_STYLES), ("eye_style", VALID_EYE_STYLES),
        ("ear_style", VALID_EAR_STYLES),
    ]:
        if field in data or not partial:
            val = data.get(field)
            result[field] = val if val in valid_set else None

    # Metadata
    if "suggested_name" in data or not partial:
        result["suggested_name"] = str(data.get("suggested_name", ""))[:20]
    if "flavor_text" in data or not partial:
        result["flavor_text"] = str(data.get("flavor_text", ""))[:60]

    return result


def generate_appearance(pet_type, user_prompt, conversation_history=None,
                        current_appearance=None):
    """Call Anthropic API to generate appearance from user prompt.

    Args:
        pet_type: "cat" or "dog"
        user_prompt: user's text description
        conversation_history: list of {"role": "user"/"assistant", "content": str}
        current_appearance: dict of current pet appearance (enables incremental updates)

    Returns:
        Validated appearance dict, or None on failure.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        import anthropic
    except ImportError:
        return None

    client = anthropic.Anthropic(api_key=api_key)

    # Build user message with context
    if current_appearance:
        current = {k: v for k, v in current_appearance.items() if v is not None}
        content = (f"Pet type: {pet_type}.\n"
                   f"Current appearance: {json.dumps(current)}\n"
                   f"User request: {user_prompt}")
    else:
        content = f"Pet type: {pet_type}. User request: {user_prompt}"

    # Build messages
    messages = []
    if conversation_history:
        for msg in conversation_history:
            messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": content})

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=messages,
        )

        text = response.content[0].text.strip()

        # Try to extract JSON from response
        if text.startswith("```"):
            # Strip markdown code fences
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Fallback: extract JSON object from surrounding text
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end > start:
                data = json.loads(text[start:end + 1])
            else:
                return None

        if current_appearance:
            return _validate_appearance(data, partial=True)
        else:
            return _validate_appearance(data)

    except (json.JSONDecodeError, KeyError, IndexError, Exception):
        return None

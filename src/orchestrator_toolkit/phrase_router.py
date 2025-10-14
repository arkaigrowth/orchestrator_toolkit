"""
Phrase Router for Natural Language Command Interpretation

Routes user input to PLAN, SPEC, or EXECUTE commands based on pattern matching.
Priority: EXEC (with id) > SPEC (with plan) > verb hints > default PLAN
"""
import re
from pathlib import Path
from typing import Literal, Optional, Tuple

Command = Literal["plan", "spec", "execute"]

# Strip these filler words early to reduce false matches
# Note: 'for' is intentionally not included here as it's used in "spec for plan-X" pattern
FILLER_WORDS = r'\b(create|make|add|new|please|the|a|an|to)\b'

# Pattern definitions for command detection (updated for both ID formats)
EXEC_WITH_ID_PATTERNS = [
    r'(?:execute|run|build|implement)\s+(SPEC-\d{8}-[A-Z0-9]{6}[a-z0-9-]*|spec-\d+)',
    r'exec\s+(SPEC-[A-Za-z0-9-]+|spec-\d+)',
    r'(?:execute|run|build)\s+spec[- ]?([A-Za-z0-9-]+)',
]

SPEC_FOR_PLAN_PATTERNS = [
    r'spec.*(?:for|on|of)\s+(PLAN-\d{8}-[A-Z0-9]{6}[a-z0-9-]*|plan-\d+)',
    r'(?:design|blueprint|specify).*(?:for|on|of)\s+(PLAN-[A-Za-z0-9-]+|plan-\d+)',
    r'plan[- ]?([A-Za-z0-9-]+)\s+(?:spec|specification|design)',
]

SPEC_VERBS = r'\b(?:spec|specify|design|blueprint|detail)(?:\s+out)?\b'
EXEC_VERBS = r'^(?:execute|run|build|implement|start|exec)\b'
PLAN_VERBS = r'\b(?:task|plan|todo|work|feature)\b'

# Pattern for marking PLANs as ready
READY_PATTERNS = [
    r'(?:mark|set|make)\s+(?:as\s+)?ready\s+(PLAN-\d{8}-[A-Z0-9]{6}[a-z0-9-]*|plan-\d+)',
    r'ready\s+(PLAN-\d{8}-[A-Z0-9]{6}[a-z0-9-]*|plan-\d+)',
    r'plan\s+ready\s+(PLAN-[A-Za-z0-9-]+)',
    r'(PLAN-\d{8}-[A-Z0-9]{6}[a-z0-9-]*|plan-\d+)\s+ready',
]


def extract_quoted_title(text: str) -> Optional[str]:
    """
    Extract title from quotes, preserving special characters.

    Handles both single and double quotes.
    Returns None if no quoted content found.

    Examples:
        'plan "OAuth 2.1 & PKCE"' -> "OAuth 2.1 & PKCE"
        "spec 'Design: Auth flows'" -> "Design: Auth flows"
    """
    # Try double quotes first
    match = re.search(r'"([^"]+)"', text)
    if match:
        return match.group(1)

    # Try single quotes
    match = re.search(r"'([^']+)'", text)
    if match:
        return match.group(1)

    return None


def route_intent(user_input: str) -> Tuple[Command, Optional[str], str]:
    """
    Route user input to appropriate command based on natural language patterns.

    Args:
        user_input: Free-form text from user

    Returns:
        Tuple of (command, target_id, cleaned_text) where:
        - command: 'plan' | 'spec' | 'execute'
        - target_id: PLAN-xxx or SPEC-xxx if explicit, else None
        - cleaned_text: Title/description for creation after removing command words

    Priority:
        1. EXECUTE with explicit spec id
        2. SPEC for existing PLAN by reference
        3. SPEC verbs without parent (will prompt)
        4. EXECUTE verbs without spec (will prompt)
        5. DEFAULT = PLAN
    """
    if not user_input:
        return ("plan", None, "Untitled")

    text = user_input.strip()
    low = text.lower()

    # Check for quoted titles first (preserve special characters)
    quoted_title = extract_quoted_title(text)

    # Check for READY patterns first (highest priority for administrative commands)
    for pattern in READY_PATTERNS:
        m = re.search(pattern, low, re.IGNORECASE)
        if m:
            plan_id = m.group(1).upper()
            plan_id = normalize_id(plan_id, "PLAN")
            return ("ready", plan_id, "")

    # Check for SPEC patterns next (before stripping "for")
    # 2. SPEC for existing PLAN by reference
    for pattern in SPEC_FOR_PLAN_PATTERNS:
        m = re.search(pattern, low, re.IGNORECASE)
        if m:
            plan_id = m.group(1).upper()

            # Use quoted title if present, otherwise extract from text
            if quoted_title:
                title = quoted_title
            else:
                # Extract title by removing the spec command part
                title = re.sub(pattern, '', low, flags=re.IGNORECASE).strip()
                title = re.sub(SPEC_VERBS, '', title, flags=re.IGNORECASE).strip()

            # Normalize ID format
            plan_id = normalize_id(plan_id, "PLAN")
            return ("spec", plan_id, title)

    # Now strip filler words including "for" since we're not in a SPEC pattern
    filler_with_for = r'\b(create|make|add|new|please|the|a|an|for|to)\b'
    cleaned = re.sub(filler_with_for, ' ', text if not quoted_title else re.sub(r'["\'].*["\']', '', text), flags=re.IGNORECASE).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)  # Normalize whitespace
    low = cleaned.lower()

    # 1. EXECUTE with explicit spec id (highest priority)
    for pattern in EXEC_WITH_ID_PATTERNS:
        m = re.search(pattern, low, re.IGNORECASE)
        if m:
            spec_id = m.group(1).upper()
            spec_id = normalize_id(spec_id, "SPEC")
            return ("execute", spec_id, "")

    # 3. SPEC verb without parent (will prompt for plan)
    if re.search(SPEC_VERBS, low):
        if quoted_title:
            title = quoted_title
        else:
            title = re.sub(SPEC_VERBS, '', cleaned, flags=re.IGNORECASE).strip()
        return ("spec", None, title or "Specification")

    # 4. EXECUTE verb without spec (will prompt for spec)
    if re.search(EXEC_VERBS, low):
        if quoted_title:
            title = quoted_title
        else:
            title = re.sub(EXEC_VERBS, '', cleaned, flags=re.IGNORECASE).strip()
        return ("execute", None, title)

    # 5. DEFAULT = PLAN (catch-all for ambiguous input)
    if quoted_title:
        title = quoted_title
    else:
        # Remove common plan-related words from title
        title = re.sub(PLAN_VERBS, '', cleaned, flags=re.IGNORECASE).strip()

    return ("plan", None, title or cleaned or "Untitled")


def extract_owner_from_text(text: str) -> Tuple[Optional[str], str]:
    """
    Extract owner specification from text if present.

    Patterns:
        - owner:alex
        - --owner alex
        - @alex

    Returns:
        Tuple of (owner, cleaned_text)
    """
    # Check for owner patterns
    patterns = [
        (r'owner:\s*(\S+)', 1),
        (r'--owner\s+(\S+)', 1),
        (r'@(\S+)', 1),
    ]

    for pattern, group in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            owner = m.group(group)
            # Remove the owner part from text and normalize whitespace
            cleaned = re.sub(pattern, ' ', text, flags=re.IGNORECASE).strip()
            cleaned = re.sub(r'\s+', ' ', cleaned)  # Normalize multiple spaces
            return (owner, cleaned)

    return (None, text)


def normalize_id(id_str: str, prefix: str) -> str:
    """
    Normalize various ID formats to full format.

    Examples:
        normalize_id("123", "PLAN") -> "PLAN-123"
        normalize_id("PLAN-123", "PLAN") -> "PLAN-123"
        normalize_id("P-123", "PLAN") -> "P-123"  # Keep legacy format
    """
    if not id_str:
        return ""

    # Handle None case
    if id_str is None:
        return ""

    id_upper = id_str.upper()

    # Already has correct prefix
    if id_upper.startswith(f"{prefix}-"):
        return id_upper

    # Legacy format (T-XXX, P-XXX)
    if re.match(r'^[TP]-\d+$', id_upper):
        return id_upper

    # Just a number or short code
    if re.match(r'^[A-Z0-9]+$', id_upper):
        return f"{prefix}-{id_upper}"

    return id_upper
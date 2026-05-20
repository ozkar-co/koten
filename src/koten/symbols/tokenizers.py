"""Per-language tokenizers that parse natural text into syllables/tokens."""

from __future__ import annotations


def tokenize_lapag(text: str, root_mapping: dict[str, list]) -> list[str]:
    """
    Lapag: consonante+vocal (overlay) or vocal alone (= silencio+vocal).
    Parses letter by letter. Returns only tokens that exist in root_mapping.
    """
    vowels = {"i", "u", "e", "a", "o"}
    tokens: list[str] = []
    i = 0
    text = text.lower().strip()
    
    while i < len(text):
        char = text[i]
        
        if char in vowels:
            # Vocal sola
            if char in root_mapping:
                tokens.append(char)
            i += 1
        elif char == " ":
            # Espacio
            if char in root_mapping:
                tokens.append(char)
            i += 1
        else:
            # Consonante: try C+V first if exists in mapping, else just C
            if i + 1 < len(text) and text[i + 1] in vowels:
                syllable = text[i:i+2]
                if syllable in root_mapping:
                    tokens.append(syllable)
                    i += 2
                    continue
            # Fallback: just consonante
            if char in root_mapping:
                tokens.append(char)
            i += 1
    
    return tokens


def tokenize_goxjix(text: str, root_mapping: dict[str, list]) -> list[str]:
    """
    Gox'jix: consonante+vocal(es) or vocal(es) alone.
    Handles vowel pairs like ai, oi, au, eu, iu, ia.
    Only returns tokens that exist in root_mapping.
    """
    vowels = {"i", "u", "e", "a", "o"}
    tokens: list[str] = []
    i = 0
    text = text.lower().strip()
    
    while i < len(text):
        char = text[i]
        
        if char == " ":
            if char in root_mapping:
                tokens.append(char)
            i += 1
        elif char in vowels:
            # Check for vowel pair first
            if i + 1 < len(text) and text[i+1] in vowels:
                pair = text[i:i+2]
                if pair in root_mapping:
                    tokens.append(pair)
                    i += 2
                    continue
            # Single vowel
            if char in root_mapping:
                tokens.append(char)
            i += 1
        else:
            # Consonante: try C+vowel pair or C+single vowel if those exist in mapping
            if i + 1 < len(text) and text[i+1] in vowels:
                # Try C + vowel pair first
                if i + 2 < len(text) and text[i+2] in vowels:
                    pair = text[i+1:i+3]
                    if pair in root_mapping:
                        syllable = text[i:i+3]
                        if syllable in root_mapping:
                            tokens.append(syllable)
                            i += 3
                            continue
                # Try C + single vowel
                syllable = text[i:i+2]
                if syllable in root_mapping:
                    tokens.append(syllable)
                    i += 2
                    continue
                # Not in mapping, just add consonant
                if char in root_mapping:
                    tokens.append(char)
                i += 1
            else:
                if char in root_mapping:
                    tokens.append(char)
                i += 1
    
    return tokens


def tokenize_dekayun(text: str, root_mapping: dict[str, list]) -> list[str]:
    """
    Dekayun: consonante+vocal or vocal alone (= silencio+vocal).
    Same as Lapag: letter by letter.
    """
    return tokenize_lapag(text, root_mapping)


def tokenize_negelch(text: str, root_mapping: dict[str, list]) -> list[str]:
    """
    Negelch: each symbol is independent, no layering.
    Recognizes digraphs like ch as a single symbol.
    Returns only tokens that exist in root_mapping.
    """
    text = text.lower().strip()
    tokens: list[str] = []
    i = 0

    while i < len(text):
        char = text[i]

        if char == " ":
            if " " in root_mapping:
                tokens.append(" ")
            i += 1
            continue

        # Try digraph first (e.g., ch)
        if i + 1 < len(text):
            pair = text[i : i + 2]
            if pair in root_mapping:
                tokens.append(pair)
                i += 2
                continue

        if char in root_mapping:
            tokens.append(char)
        i += 1

    return tokens


def tokenize_idoling(text: str, root_mapping: dict[str, list]) -> list[str]:
    """
    Idoling: like Negelch, independent symbols.
    Handles digraphs ts, ch. Only returns tokens in root_mapping.
    """
    text = text.lower().strip()
    if " " in text:
        tokens = text.split()
        return [t for t in tokens if t in root_mapping]
    
    # Handle digraphs
    tokens: list[str] = []
    i = 0
    while i < len(text):
        # Try digraph first
        if i + 1 < len(text):
            pair = text[i:i+2]
            if pair in root_mapping:
                tokens.append(pair)
                i += 2
                continue
        # Single char
        char = text[i]
        if char in root_mapping:
            tokens.append(char)
        i += 1
    return tokens


def tokenize_jobide(text: str, root_mapping: dict[str, list]) -> list[str]:
    """
    Jobid'e: exactly 4 syllables. Each syllable is consonant+vowel.
    Takes pairs of characters. If odd-length, implicitly adds ' at end.
    
    "jobid'e" (7 chars) → implicitly becomes "jobid'e'" (8 chars)
    → pairs: jo, bi, d', e' → 4 syllables
    """
    text = text.lower().strip()
    text = text.replace(" ", "")  # Remove spaces
    
    # If odd-length, add implicit vowel at end
    if len(text) % 2 == 1:
        text += "'"
    
    tokens: list[str] = []
    i = 0
    
    while i < len(text):
        if i + 1 < len(text):
            # Try to take pair (C+V)
            pair = text[i:i+2]
            if pair in root_mapping:
                tokens.append(pair)
                i += 2
            else:
                # Pair not in mapping; try individual chars
                char = text[i]
                if char in root_mapping:
                    tokens.append(char)
                char = text[i+1]
                if char in root_mapping:
                    tokens.append(char)
                i += 2
        else:
            # Last char (shouldn't happen after padding)
            char = text[i]
            if char in root_mapping:
                tokens.append(char)
            i += 1
    
    return tokens


def tokenize_gornach_kagsha(text: str, root_mapping: dict[str, list]) -> list[str]:
    """
    Gornach-Kagsha: longest match greedy parsing.
    Tries lengths 4, 3, 2, 1 in that order.
    Token '-' stays as-is for column breaks.
    """
    text = text.lower().strip()
    tokens: list[str] = []
    i = 0
    
    while i < len(text):
        char = text[i]
        
        # '-' is special: column break token
        if char == "-":
            tokens.append("-")
            i += 1
            continue
        
        # Skip spaces
        if char == " ":
            i += 1
            continue
        
        # Try longest matches: 4, 3, 2, 1
        matched = False
        for length in [4, 3, 2, 1]:
            if i + length <= len(text):
                candidate = text[i:i+length]
                if candidate in root_mapping:
                    tokens.append(candidate)
                    i += length
                    matched = True
                    break
        
        if not matched:
            # No match found, skip character
            i += 1
    
    return tokens


# Registry of tokenizers per language
TOKENIZERS = {
    "lapag": tokenize_lapag,
    "goxjix": tokenize_goxjix,
    "dekayun": tokenize_dekayun,
    "negelch": tokenize_negelch,
    "idoling": tokenize_idoling,
    "jobide": tokenize_jobide,
    "gornach_kagsha": tokenize_gornach_kagsha,
}


def get_tokenizer(language_code: str):
    """Get the tokenizer function for a language."""
    return TOKENIZERS.get(language_code, lambda text, mapping: text.split())

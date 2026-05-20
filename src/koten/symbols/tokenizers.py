"""Per-language tokenizers that parse natural text into syllables/tokens."""

from __future__ import annotations


def tokenize_lapag(text: str, root_mapping: dict[str, list]) -> list[str]:
    """
    Lapag: consonante+vocal (overlay) or vocal alone (= silencio+vocal).
    Parses letter by letter.
    """
    vowels = {"i", "u", "e", "a", "o"}
    tokens: list[str] = []
    i = 0
    text = text.lower().strip()
    
    while i < len(text):
        char = text[i]
        
        if char in vowels:
            # Vocal sola → silencio + vocal
            tokens.append(char)
            i += 1
        else:
            # Consonante: check if next is vowel
            if i + 1 < len(text) and text[i + 1] in vowels:
                syllable = text[i:i+2]
                tokens.append(syllable)
                i += 2
            else:
                # Consonante solo
                tokens.append(char)
                i += 1
    
    return tokens


def tokenize_goxjix(text: str, root_mapping: dict[str, list]) -> list[str]:
    """
    Gox'jix: consonante+vocal(es) or vocal(es) alone.
    Handles vowel pairs like ai, oi, au, eu, iu, ia.
    """
    vowels = {"i", "u", "e", "a", "o"}
    vowel_pairs = {"ai", "oi", "au", "eu", "iu", "ia"}
    tokens: list[str] = []
    i = 0
    text = text.lower().strip()
    
    while i < len(text):
        char = text[i]
        
        if char in vowels:
            # Check if next is also vowel and forms a valid pair
            if i + 1 < len(text) and text[i+1] in vowels:
                pair = text[i:i+2]
                if pair in vowel_pairs:
                    tokens.append(pair)
                    i += 2
                    continue
            # Single vowel
            tokens.append(char)
            i += 1
        else:
            # Consonante
            if i + 1 < len(text) and text[i + 1] in vowels:
                # Check for vowel pair after consonante
                if i + 2 < len(text) and text[i+2] in vowels:
                    pair = text[i+1:i+3]
                    if pair in vowel_pairs:
                        syllable = text[i:i+3]
                        tokens.append(syllable)
                        i += 3
                        continue
                # Single vowel after consonante
                syllable = text[i:i+2]
                tokens.append(syllable)
                i += 2
            else:
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
    Negelch: cada símbolo es independiente, no hay sobreposición.
    Solo dividir por espacios y caracteres individuales si no hay espacios.
    """
    text = text.lower().strip()
    # Try splitting by space first
    if " " in text:
        return text.split()
    # Otherwise each character is a token
    return list(text)


def tokenize_idoling(text: str, root_mapping: dict[str, list]) -> list[str]:
    """
    Idoling: similar a Negelch, símbolos independientes.
    Maneja digrafos ts, ch.
    """
    text = text.lower().strip()
    if " " in text:
        return text.split()
    
    # Handle digraphs
    digraphs = {"ts", "ch"}
    tokens: list[str] = []
    i = 0
    while i < len(text):
        if i + 1 < len(text):
            pair = text[i:i+2]
            if pair in digraphs:
                tokens.append(pair)
                i += 2
                continue
        tokens.append(text[i])
        i += 1
    return tokens


def tokenize_jobide(text: str, root_mapping: dict[str, list]) -> list[str]:
    """
    Jobid'e: de a 2 caracteres (consonante+vocal).
    La vocal puede ser i,u,e,a,o,'.
    Si la palabra tiene longitud impar, la última es '.
    """
    text = text.lower().strip()
    text = text.replace(" ", "")  # Remove spaces
    
    tokens: list[str] = []
    i = 0
    
    while i < len(text):
        if i + 1 < len(text):
            # Take pair
            pair = text[i:i+2]
            tokens.append(pair)
            i += 2
        else:
            # Last char alone (should be ')
            tokens.append(text[i])
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

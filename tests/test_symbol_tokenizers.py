from koten.symbols.tokenizers import tokenize_dekayun, tokenize_lapag


def _lapag_root_mapping() -> dict[str, list[int]]:
    return {
        "_": [0, 0],
        "a": [0, 1],
        "i": [0, 2],
        "b": [0, 3],
        "n": [0, 4],
        " ": [0, 5],
    }


def test_lapag_inserts_silence_before_initial_vowel() -> None:
    tokens = tokenize_lapag("ani", _lapag_root_mapping())

    assert tokens[:2] == ["_", "a"]


def test_lapag_inserts_silence_after_space_before_vowel() -> None:
    tokens = tokenize_lapag("b a", _lapag_root_mapping())

    assert tokens == ["b", " ", "_", "a"]


def test_dekayun_inserts_silence_before_initial_vowel() -> None:
    tokens = tokenize_dekayun("ani", _lapag_root_mapping())

    assert tokens[:2] == ["_", "a"]
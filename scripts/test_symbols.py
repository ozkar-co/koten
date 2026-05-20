#!/usr/bin/env python3
"""Manual test script for symbol generation."""

import sys
from pathlib import Path

# Add src/ to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from koten.symbols.generator import SymbolGenerator
from koten.symbols.tokenizers import get_tokenizer

# Test cases: supports multiple words for the same language
TEST_CASES = [
    ("lapag", "lapag"),
    ("goxjix", "gox'jix"),
    ("goxjix", "yuxejai"),
    ("dekayun", "dekayun"),
    ("negelch", "negelch"),
    ("idoling", "idoling"),
    ("jobide", "jobid'e"),
    ("gornach_kagsha", "gornash-kagsha"),
    ("gornach_kagsha", "garor-kageshlug"),
]

def main():
    # Create temp directory
    temp_dir = project_root / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    print(f"📁 Output directory: {temp_dir}")
    print(f"🔤 Testing {len(TEST_CASES)} cases...\n")
    
    generator = SymbolGenerator(str(project_root / "src" / "koten" / "symbols"))
    
    for language, word in TEST_CASES:
        try:
            # Get config and tokenize for debug output
            if language in generator.configs:
                config = generator.configs[language]
                tokenizer = get_tokenizer(language)
                root_mapping = config.config.get("root_mapping", {})
                tokens = tokenizer(word, root_mapping)
                
                print(f"  {language:20} '{word}'")
                print(f"    → tokens: {tokens}")
            
            # Generate image
            image = generator.generate_word_image(
                word,
                language,
                spacing_x=0,
                spacing_y=0,
            )
            
            # Save to temp/
            safe_word = word.replace("'", "")
            output_path = temp_dir / f"{language}_{safe_word}.png"
            image.save(output_path)
            
            print(f"    ✓ {image.size[0]}×{image.size[1]} → {output_path.relative_to(project_root)}\n")
            
        except Exception as e:
            print(f"    ✗ Error: {e}\n")
    
    print(f"✅ Done. Check temp/ directory for generated images.")

if __name__ == "__main__":
    main()

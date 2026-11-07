"""Remove emojis and other problematic characters from the tweets CSV.

Usage:
    python src/clean_text.py --input dataset.csv --check                 # check for unicode issues and emojis
    python src/clean_text.py --input dataset.csv                         # dry run cleaning
    python src/clean_text.py --input dataset.csv --output clean.csv --apply  # apply cleaning
"""
import os
import re
import sys
import unicodedata
from collections import Counter

import pandas as pd

# Project root, found from this file's location (src/ -> one level up), so paths work from any working directory.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Parse command-line arguments
apply = "--apply" in sys.argv
check_only = "--check" in sys.argv
input_filename = "dataset.csv"      # default input filename
output_filename = "text_cleaned.csv"  # default output filename

# Get input filename from --input argument
if "--input" in sys.argv:
    input_index = sys.argv.index("--input")
    if input_index + 1 < len(sys.argv):
        input_filename = sys.argv[input_index + 1]

# Get output filename from --output argument
if "--output" in sys.argv:
    output_index = sys.argv.index("--output")
    if output_index + 1 < len(sys.argv):
        output_filename = sys.argv[output_index + 1]

csv_path = os.path.join(project_root, "data", input_filename)
output_path = os.path.join(project_root, "data", output_filename)

# Unicode categories to drop:
#   So - other symbols: emojis, pictographs, flags, arrows, the "�" replacement character
#   Cc - control characters (newlines and tabs are turned into spaces first, so they survive)
#   Cf - invisible format characters: zero-width spaces/joiners, text-direction marks, BOM
#   Co - private use (renders as boxes), Cs - broken surrogates, Cn - unassigned code points
#   Me - enclosing marks, e.g. the keycap in "1️⃣"
DROP_CATEGORIES = {"So", "Cc", "Cf", "Co", "Cs", "Cn", "Me"}


def is_dropped(char):
    if unicodedata.category(char) in DROP_CATEGORIES:
        return True
    # Emoji variation selectors (U+FE00-U+FE0F) and skin tone modifiers (U+1F3FB-U+1F3FF).
    return "︀" <= char <= "️" or "\U0001f3fb" <= char <= "\U0001f3ff"


def clean(text):
    # NFKC turns look-alike characters into plain ones (e.g. "𝐘𝐀𝐑𝐃𝐈𝐌" -> "YARDIM", "…" -> "...")
    # and keeps Turkish letters (ç, ğ, ı, İ, ö, ş, ü) intact.
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s", " ", text)
    text = "".join(c for c in text if not is_dropped(c))
    # Removing emojis can leave double spaces behind; collapse them.
    return re.sub(r" {2,}", " ", text).strip()


def check_ambiguous_unicode(text):
    """Detect homoglyphs and other ambiguous Unicode characters."""
    HOMOGLYPHS = {
        'а': ('CYRILLIC SMALL LETTER A', 'a'),
        'е': ('CYRILLIC SMALL LETTER IE', 'e'),
        'о': ('CYRILLIC SMALL LETTER O', 'o'),
        'р': ('CYRILLIC SMALL LETTER ER', 'p'),
        'с': ('CYRILLIC SMALL LETTER ES', 'c'),
        'х': ('CYRILLIC SMALL LETTER HA', 'x'),
        'у': ('CYRILLIC SMALL LETTER U', 'y'),
        'А': ('CYRILLIC CAPITAL LETTER A', 'A'),
        'Е': ('CYRILLIC CAPITAL LETTER IE', 'E'),
        'О': ('CYRILLIC CAPITAL LETTER O', 'O'),
        'Р': ('CYRILLIC CAPITAL LETTER ER', 'P'),
        'С': ('CYRILLIC CAPITAL LETTER ES', 'C'),
        'Х': ('CYRILLIC CAPITAL LETTER HA', 'X'),
        'У': ('CYRILLIC CAPITAL LETTER U', 'Y'),
    }

    for homoglyph in HOMOGLYPHS:
        if homoglyph in text:
            return True
    return False


def check_problematic_chars(text):
    """Detect emojis and other problematic characters that would be removed."""
    for char in text:
        if is_dropped(char):
            return True
    return False


def main():
    df = pd.read_csv(csv_path)

    # Remove unnamed index column if it exists (from files saved with index=True)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    original = df["Tweets"].astype(str)

    # If --check flag is used, only check for issues without cleaning
    if check_only:
        print("🔍 Scanning for Unicode issues and problematic characters...\n")

        ambiguous_rows = []
        problematic_rows = []

        for idx, tweet in original.items():
            if check_ambiguous_unicode(tweet):
                ambiguous_rows.append((idx, tweet))
            if check_problematic_chars(tweet):
                problematic_rows.append((idx, tweet))

        # Report ambiguous characters
        if ambiguous_rows:
            print(f"⚠️  Found {len(ambiguous_rows)} tweets with AMBIGUOUS UNICODE (homoglyphs):\n")
            for idx, tweet in ambiguous_rows[:5]:
                print(f"  Row {idx}: {tweet[:100]}...\n")
            if len(ambiguous_rows) > 5:
                print(f"  ... and {len(ambiguous_rows) - 5} more\n")
        else:
            print("✅ No ambiguous Unicode characters found.\n")

        # Report emojis and problematic characters
        if problematic_rows:
            removed = Counter(c for text in original for c in unicodedata.normalize("NFKC", text) if is_dropped(c))
            print(f"⚠️  Found {len(problematic_rows)} tweets with EMOJIS/PROBLEMATIC CHARS ({sum(removed.values())} total):\n")
            print("Most common problematic characters:")
            for char, count in removed.most_common(10):
                name = unicodedata.name(char, "UNKNOWN")
                print(f"  {count:3}x  U+{ord(char):04X}  {name}")
            print()
            for idx, tweet in problematic_rows[:5]:
                print(f"  Row {idx}: {tweet[:100]}...\n")
            if len(problematic_rows) > 5:
                print(f"  ... and {len(problematic_rows) - 5} more\n")
        else:
            print("✅ No emojis or problematic characters found.\n")

        return

    # Regular cleaning mode (not --check)
    cleaned = original.map(clean)
    changed = cleaned != original

    removed = Counter(c for text in original for c in unicodedata.normalize("NFKC", text) if is_dropped(c))
    print(f"{changed.sum()} of {len(df)} tweets {'changed' if apply else 'would change'}.")
    print(f"{sum(removed.values())} characters {'were' if apply else 'would be'} removed. Most common:")
    for char, count in removed.most_common(15):
        name = unicodedata.name(char, "UNKNOWN")
        print(f"  {count:5}  U+{ord(char):04X}  {name}")

    empty = (cleaned == "").sum()
    if empty:
        print(f"\nWarning: {empty} tweets {'became' if apply else 'would become'} empty.")

    if not apply:
        print()
        for before, after in list(zip(original[changed], cleaned[changed]))[:5]:
            print("BEFORE:", before)
            print("AFTER: ", after, "\n")
        print(f"Dry run only. Re-run with --apply to clean text and save to {output_filename}")
        return

    df["Tweets"] = cleaned
    df.to_csv(output_path, index=False)
    print(f"\nCleaned emojis and problematic characters from {len(df)} tweets.")
    print(f"Read from: {input_filename}")
    print(f"Saved to: {output_filename}")


if __name__ == "__main__":
    main()

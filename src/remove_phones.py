"""Replace Turkish phone numbers in the tweets CSV with [TELEFON].

Usage:
    python src/remove_phones.py --input dataset.csv --check              # check for phone numbers only
    python src/remove_phones.py --input dataset.csv                      # dry run with defaults
    python src/remove_phones.py --input dataset.csv --output phones_clean.csv  # dry run with custom output
    python src/remove_phones.py --input dataset.csv --output phones_clean.csv --apply  # apply redaction
"""
import os
import re
import sys

import pandas as pd

# Project root, found from this file's location (src/ -> one level up), so paths work from any working directory.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Parse command-line arguments
apply = "--apply" in sys.argv
check_only = "--check" in sys.argv
input_filename = "dataset.csv"        # default input filename
output_filename = "phones_removed.csv"  # default output filename

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

# One Turkish phone number: optional +90 and/or leading 0, then a 10-digit mobile (5xx) or landline (2xx-4xx)
# number, with optional spaces, dots, dashes or parentheses between groups (e.g. "+90 (546) 811 35 16").
# Second alternative: the unusual 3-3-5 grouping with a leading 0 (e.g. "053-504-92043"); separators are
# required there so it can't match unrelated digit runs such as GPS coordinates.
# The lookarounds stop it from matching part of a longer digit sequence.
PHONE = re.compile(
    r"(?<!\d)(?:"
    r"(?:\+?90[\s.-]?)?\(?0?\s?\(?[2-5]\d{2}\)?[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}"
    r"|0[2-5]\d[\s.-]\d{3}[\s.-]\d{5}"
    r")(?!\d)"
)


def redact(text):
    return PHONE.sub("[TELEFON]", text)


def main():
    df = pd.read_csv(csv_path)

    # Remove unnamed index column if it exists (from files saved with index=True)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    redacted = df["Tweets"].astype(str).map(redact)
    changed = redacted != df["Tweets"].astype(str)

    # Count matches in the original text, so [TELEFON] markers left by an earlier run aren't counted again.
    replaced = sum(len(PHONE.findall(text)) for text in df["Tweets"].astype(str))

    # If --check flag is used, only report phone numbers
    if check_only:
        print("🔍 Scanning for phone numbers...\n")
        print(f"{changed.sum()} of {len(df)} tweets contain phone numbers.")
        print(f"{replaced} phone numbers found.\n")

        if changed.sum() > 0:
            print("Sample tweets with phone numbers:\n")
            for before, after in list(zip(df["Tweets"][changed], redacted[changed]))[:5]:
                print("BEFORE:", before)
                print("AFTER: ", after, "\n")
            if changed.sum() > 5:
                print(f"... and {changed.sum() - 5} more tweets with phone numbers\n")
        else:
            print("✅ No phone numbers found.\n")

        return

    # Normal mode: dry run or apply
    print(f"{changed.sum()} of {len(df)} tweets contain phone numbers.")
    print(f"{replaced} numbers {'were' if apply else 'would be'} replaced.\n")

    if not apply:
        for before, after in list(zip(df["Tweets"][changed], redacted[changed]))[:5]:
            print("BEFORE:", before)
            print("AFTER: ", after, "\n")
        print(f"Dry run only. Re-run with --apply to remove phones and save to {output_filename}")
        return

    df["Tweets"] = redacted
    df.to_csv(output_path, index=False)
    print(f"\nRemoved phone numbers from {len(df)} tweets.")
    print(f"Read from: {input_filename}")
    print(f"Saved to: {output_filename}")


if __name__ == "__main__":
    main()

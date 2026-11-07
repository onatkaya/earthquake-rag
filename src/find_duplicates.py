"""Remove duplicate tweets from the dataset CSV.

Usage:
    python src/find_duplicates.py --input dataset.csv --check              # check for duplicates only
    python src/find_duplicates.py --input dataset.csv                      # dry run with defaults
    python src/find_duplicates.py --input dataset.csv --output my_data.csv # dry run with custom output
    python src/find_duplicates.py --input dataset.csv --output my_data.csv --apply  # apply deduplication
"""
import os
import sys
import pandas as pd

# Project root, found from this file's location (src/ -> one level up)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Parse command-line arguments
apply = "--apply" in sys.argv
check_only = "--check" in sys.argv
input_filename = "dataset.csv"      # default input filename
output_filename = "new_dataset.csv"  # default output filename

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


def main():
    df = pd.read_csv(csv_path)

    # Remove unnamed index column if it exists (from files saved with index=True)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # Find duplicate tweets
    duplicates = df[df.duplicated(subset=["Tweets"], keep=False)].sort_values("Tweets")
    duplicates_to_remove = df[df.duplicated(subset=["Tweets"], keep="first")]

    if len(duplicates) == 0:
        print("✅ No duplicate tweets found.")
        return

    # If --check flag is used, only report duplicates
    if check_only:
        print("🔍 Checking for duplicate tweets...\n")
        print(f"Found {len(duplicates)} duplicate rows ({len(duplicates_to_remove)} duplicates to remove):\n")

        # Group by tweet to show all occurrences
        for tweet, group in duplicates.groupby("Tweets"):
            indices = group.index.tolist()
            count = len(indices)
            kept_index = indices[0]
            removed_indices = indices[1:]
            print(f"Tweet appears {count} times:")
            print(f"  Keep index: {kept_index}")
            print(f"  Remove indices: {removed_indices}")
            print(f"  Content: {tweet[:80]}...\n" if len(tweet) > 80 else f"  Content: {tweet}\n")

        print(f"Summary: {len(df)} rows → {len(df) - len(duplicates_to_remove)} rows after deduplication")
        return

    # Normal mode: dry run or apply
    print(f"Found {len(duplicates)} duplicate rows ({len(duplicates_to_remove)} would be removed):\n")

    # Group by tweet to show all occurrences
    for tweet, group in duplicates.groupby("Tweets"):
        indices = group.index.tolist()
        count = len(indices)
        kept_index = indices[0]
        removed_indices = indices[1:]
        print(f"Tweet appears {count} times:")
        print(f"  Keep index: {kept_index}")
        print(f"  Remove indices: {removed_indices}")
        print(f"  Content: {tweet[:80]}...\n" if len(tweet) > 80 else f"  Content: {tweet}\n")

    if not apply:
        print(f"Dry run only. Original dataset: {len(df)} rows")
        print(f"After deduplication: {len(df) - len(duplicates_to_remove)} rows")
        print(f"Re-run with --apply to remove duplicates and save to {output_filename}")
        return

    # Remove duplicates (keep first occurrence)
    df_clean = df.drop_duplicates(subset=["Tweets"], keep="first")

    # Reset indices to be sequential (0, 1, 2, ...) instead of keeping gaps from removed rows
    df_clean = df_clean.reset_index(drop=True)

    # Save to output file (without index to prevent 'Unnamed: 0' column)
    df_clean.to_csv(output_path, index=False)
    print(f"\nRemoved {len(duplicates_to_remove)} duplicate rows.")
    print(f"Read from: {input_filename}")
    print(f"Saved to: {output_filename}")
    print(f"Cleaned dataset: {len(df_clean)} rows (was {len(df)} rows)")
    print(f"Indices reset to sequential order (0 to {len(df_clean)-1})")


if __name__ == "__main__":
    main()

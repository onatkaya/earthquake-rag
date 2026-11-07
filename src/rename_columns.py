"""Convert numeric Class column values to descriptive text labels.

Usage:
    python src/rename_columns.py --input dataset.csv --check              # check for conversion only
    python src/rename_columns.py --input dataset.csv                      # dry run with defaults
    python src/rename_columns.py --input dataset.csv --output labeled.csv # dry run with custom output
    python src/rename_columns.py --input dataset.csv --output labeled.csv --apply  # apply conversion
"""
import os
import sys
import pandas as pd

# Project root, found from this file's location (src/ -> one level up)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Parse command-line arguments
apply = "--apply" in sys.argv
check_only = "--check" in sys.argv
input_filename = "dataset.csv"        # default input filename
output_filename = "dataset_labeled.csv"  # default output filename

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

# Mapping from numeric to text labels
CLASS_MAPPING = {
    0.0: "Negatif İçerik",      # Negative/unrelated content
    1.0: "Yardım Çağrısı",      # Help requests
}


def main():
    df = pd.read_csv(csv_path)

    # Remove unnamed index column if it exists (from files saved with index=True)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # Check if Class column exists and has numeric values
    if "Class" not in df.columns:
        print("❌ Error: 'Class' column not found in the dataset.")
        return

    # Get current unique values
    unique_classes = sorted(df["Class"].unique())

    # Convert to text labels
    converted = df["Class"].map(CLASS_MAPPING)
    changed = converted != df["Class"].astype(str)

    # If --check flag is used, only report conversions
    if check_only:
        print("🔍 Scanning for numeric Class values to convert...\n")
        print(f"Current unique Class values: {unique_classes}")
        print(f"Conversion mapping:")
        for numeric, text in sorted(CLASS_MAPPING.items()):
            count = (df["Class"] == numeric).sum()
            print(f"  {numeric} → '{text}' ({count} tweets)")

        print(f"\nTotal tweets to convert: {changed.sum()}")
        print(f"\nSample conversions:\n")

        sample_indices = df.index[changed][:5]
        for idx in sample_indices:
            old_val = df.loc[idx, "Class"]
            new_val = converted.loc[idx]
            print(f"  Row {idx}: {old_val} → {new_val}")

        if changed.sum() > 5:
            print(f"\n  ... and {changed.sum() - 5} more\n")

        return

    # Normal mode: dry run or apply
    print(f"Found {changed.sum()} rows with numeric Class values.")
    print(f"Conversion mapping:")
    for numeric, text in sorted(CLASS_MAPPING.items()):
        count = (df["Class"] == numeric).sum()
        print(f"  {numeric} → '{text}' ({count} tweets)\n")

    if not apply:
        print(f"Sample conversions:\n")

        sample_indices = df.index[changed][:5]
        for idx in sample_indices:
            old_val = df.loc[idx, "Class"]
            new_val = converted.loc[idx]
            print(f"  Row {idx}: {old_val} → {new_val}")

        if changed.sum() > 5:
            print(f"\n  ... and {changed.sum() - 5} more\n")

        print(f"Dry run only. Original dataset: {len(df)} rows")
        print(f"Re-run with --apply to convert Class labels and save to {output_filename}")
        return

    # Apply conversion
    df["Class"] = converted
    df.to_csv(output_path, index=False)
    print(f"\nConverted numeric Class values to text labels.")
    print(f"Read from: {input_filename}")
    print(f"Saved to: {output_filename}")
    print(f"Total rows converted: {changed.sum()}")


if __name__ == "__main__":
    main()

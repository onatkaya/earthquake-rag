"""
Full Data Preprocessing Pipeline for EarthquakeRAG

This script orchestrates all preprocessing steps in sequence:
1. Remove duplicates
2. Convert numeric Class labels to text
3. Redact phone numbers
4. Remove emojis and problematic characters

Usage:
    python src/preprocess_all.py                                    # process with defaults
    python src/preprocess_all.py --input dataset.csv --output final_clean.csv  # process with custom files
    python src/preprocess_all.py --check                           # preview all steps without applying

The pipeline chains the outputs, so each step uses the previous step's output as input.
"""
import os
import sys
import subprocess

# Project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Parse command-line arguments
check_mode = "--check" in sys.argv
input_filename = "dataset.csv"
output_filename = "dataset_preprocessed.csv"

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

# Define the preprocessing pipeline
steps = [
    {
        "name": "1. Remove Duplicates",
        "script": "find_duplicates.py",
        "input": input_filename,
        "output": "step1_deduped.csv",
    },
    {
        "name": "2. Convert Class Labels",
        "script": "rename_columns.py",
        "input": "step1_deduped.csv",
        "output": "step2_labeled.csv",
    },
    {
        "name": "3. Redact Phone Numbers",
        "script": "remove_phones.py",
        "input": "step2_labeled.csv",
        "output": "step3_no_phones.csv",
    },
    {
        "name": "4. Remove Emojis & Problematic Characters",
        "script": "clean_text.py",
        "input": "step3_no_phones.csv",
        "output": output_filename,
    },
]


def run_step(step, check_flag=False):
    """Run a single preprocessing step."""
    print(f"\n{'='*60}")
    print(f"  {step['name']}")
    print(f"{'='*60}")

    # Build the command
    script_path = os.path.join(project_root, "src", step["script"])
    cmd = [
        sys.executable,
        script_path,
        "--input", step["input"],
        "--output", step["output"],
    ]

    # In check mode, preview only; otherwise always apply for pipeline
    if check_flag:
        cmd.append("--check")
    else:
        cmd.append("--apply")

    # Run the script
    try:
        result = subprocess.run(cmd, cwd=os.path.join(project_root, "data"), check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running {step['name']}")
        print(f"   Script: {step['script']}")
        print(f"   Command: {' '.join(cmd)}")
        return False


def main():
    """Run the full preprocessing pipeline."""
    print("\n" + "="*60)
    print("  🔧 EarthquakeRAG Full Preprocessing Pipeline")
    print("="*60)

    if check_mode:
        print("\n📋 CHECK MODE - Previewing all steps without applying changes")
        print("   Run without --check to actually process the data\n")
    else:
        print("\n⚙️  PROCESSING DATA - Running all preprocessing steps...\n")

    print(f"Input file:  {input_filename}")
    print(f"Output file: {output_filename}")
    print(f"Pipeline steps: {len(steps)}")

    # Run each step
    successful_steps = 0
    for step in steps:
        if run_step(step, check_flag=check_mode):
            successful_steps += 1
        else:
            print(f"\n⚠️  Pipeline stopped at step {successful_steps + 1}/{len(steps)}")
            return False

    # Summary
    print(f"\n" + "="*60)
    print(f"  ✅ Pipeline Complete!")
    print(f"="*60)
    print(f"Successfully completed: {successful_steps}/{len(steps)} steps")

    if not check_mode:
        output_path = os.path.join(project_root, "data", output_filename)
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / 1024  # Convert to KB
            print(f"Output file: {output_filename} ({file_size:.1f} KB)")
            print(f"\n✨ Your fully preprocessed dataset is ready!")
            print(f"   Location: data/{output_filename}")
        else:
            print(f"\n⚠️  Warning: Output file not found at {output_path}")
    else:
        print(f"\nTo process the data, run:")
        print(f"  python src/preprocess_all.py")

    print()
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

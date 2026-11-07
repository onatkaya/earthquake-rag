# EarthquakeRAG: AI-based Turkey 2023 Earthquake Tweet Assistant

![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-RAG-brightgreen?style=flat-square)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-orange?style=flat-square)
![Chroma](https://img.shields.io/badge/Chroma-Vector%20DB-purple?style=flat-square)
![Turkish NLP](https://img.shields.io/badge/Turkish-NLP-red?style=flat-square)
![Privacy](https://img.shields.io/badge/Privacy-Local%20Only-yellow?style=flat-square)

## Summary

This is a RAG-based AI assistant that answers questions about tweets from the [February 6, 2023 earthquake in Turkey](https://en.wikipedia.org/wiki/2023_Turkey%E2%80%93Syria_earthquakes).

Instead of scrolling through hundreds of tweets, you can ask a question in Turkish (e.g. "Hatay'da ne tür yardımlar isteniyordu?") and the assistant will search the data and give you an answer based on what people actually posted.

*Everything runs locally. No data or questions leave your machine.*

## Technologies Used

- **RAG** (Retrieval-Augmented Generation) - answers come from real tweets, not from the model's memory, so you can trace where the answer came from.
- **Vector Database** - tweets are converted to embeddings and stored in Chroma, so you can search by meaning.
- **Turkish LLM and Embedding Model**

## Why does this project matter?

Earthquakes trigger floods of social media activity: some tweets are urgent requests for help, while others are commentary. Sorting through them manually in order to have context about some questions takes time. However, in an emergency, *time is the most valuable asset*. 

This project shows how AI can pull out the important information from social media quickly.

## How it works 🤖

1. A dataset of real, pre-processed tweets from the 2023 earthquake is loaded
   (`data/dataset.csv`), each one labeled as either **"Yardım Çağrısı"**
   (a call for help) or **"Negatif İçerik"** (negative/critical content).
2. Each tweet is converted into a format the AI can search by *meaning*,
   not just exact keywords, and stored in a local, searchable database.
3. When someone asks a question, the system finds the k-most relevant
   tweets from that database. Currently, that value is set to 30.
4. Those tweets are handed to a Turkish-language AI model, which reads
   them and writes an answer to the question, grounded in what people
   actually posted.

## Project Structure

```
earthquake-rag/
├── README.md                    # Project documentation
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies
├── src/                         # Source code directory
│   ├── main.py                  # Main chatbot application
│   ├── vector.py                # Vector database & retriever setup
│   ├── preprocess_all.py        # Master preprocessing pipeline
│   ├── find_duplicates.py       # Remove duplicate tweets
│   ├── rename_columns.py        # Convert class labels to text
│   ├── remove_phones.py         # Redact phone numbers
│   └── clean_text.py            # Remove emojis & problematic chars
└── data/                        # Data directory
    └── dataset.csv              # Pre-processed tweets
```

Key files:
- src/main.py - Start the chatbot
- src/preprocess_all.py - Run all preprocessing steps
- data/dataset.csv - Tweet dataset (from Kaggle)

## Dataset

The dataset (`data/dataset.csv`) is a pre-processed version of the [Turkey Earthquake Relief Tweets Dataset](https://www.kaggle.com/datasets/ulkutuncerkucuktas/turkey-earthquake-relief-tweets-dataset/) from Kaggle.

The final, pre-processed dataset could be downloaded and checked out [here](https://www.kaggle.com/datasets/-onatkaya1-turkey-earthquake-relief-tweets-dataset).

## Data Preprocessing Tools

The provided dataset is already clean and ready to use. 

These scripts are for reference if you want to preprocess the original Kaggle dataset yourself.

### Master Pipeline - Run All Steps at Once

Run all four preprocessing steps in one command using preprocess_all.py:

```bash
# Process data with defaults (reads dataset.csv, outputs dataset_preprocessed.csv)
python src/preprocess_all.py

# Preview all changes without applying them
python src/preprocess_all.py --check

# Use custom input/output filenames
python src/preprocess_all.py --input raw_data.csv --output cleaned_data.csv
```

The pipeline automatically chains the outputs:
1. Removes duplicates → `step1_deduped.csv`
2. Converts class labels → `step2_labeled.csv`
3. Redacts phone numbers → `step3_no_phones.csv`
4. Cleans emojis & problematic characters → final output

**Example output:**
```
✅ Step 1: Removed 35 duplicate tweets (499 → 464 rows)
✅ Step 2: Converted numeric Class values to text labels
✅ Step 3: Redacted 238 phone numbers from 211 tweets
✅ Step 4: Cleaned 303 emoji/problematic characters from 311 tweets

✨ Final dataset ready: dataset_preprocessed.csv (464 rows, clean format)
```

---

### Individual Tools

Four utility scripts are also available for data inspection and targeted cleaning:

### `find_duplicates.py` - Remove Duplicate Tweets
```bash
# Check for duplicates without removing them
python src/find_duplicates.py --input dataset.csv --check

# Dry run: show what would be removed
python src/find_duplicates.py --input dataset.csv

# Apply deduplication and save
python src/find_duplicates.py --input dataset.csv --output deduped.csv --apply
```

### `rename_columns.py` - Convert Class Labels to Text
```bash
# Check for numeric Class values without converting
python src/rename_columns.py --input dataset.csv --check

# Dry run: show what would be converted
python src/rename_columns.py --input dataset.csv

# Apply conversion and save
python src/rename_columns.py --input dataset.csv --output dataset_labeled.csv --apply
```

**Conversion Mapping:**
- `0.0` → `"Negatif İçerik"` (negative/unrelated content)
- `1.0` → `"Yardım Çağrısı"` (help requests)

### `remove_phones.py` - Redact Phone Numbers
```bash
# Check for phone numbers without redacting
python src/remove_phones.py --input dataset.csv --check

# Dry run: show what would be redacted
python src/remove_phones.py --input dataset.csv

# Apply redaction and save
python src/remove_phones.py --input dataset.csv --output phones_clean.csv --apply
```

### `clean_text.py` - Remove Emojis & Problematic Characters
```bash
# Check for Unicode issues and emojis
python src/clean_text.py --input dataset.csv --check

# Dry run: show what would be removed
python src/clean_text.py --input dataset.csv

# Apply cleaning and save
python src/clean_text.py --input dataset.csv --output text_clean.csv --apply
```

**All tools support:**
- `--input <filename>` — specify input CSV file (default: `dataset.csv`)
- `--output <filename>` — specify output CSV file (default: depends on script)
- `--check` — inspect issues without modifying data
- `--apply` — actually perform the operation and save results

## Requirements

Software needed:
- Python 3.9 or newer
- [Ollama](https://ollama.com) - runs AI models locally, no cloud subscription or per-question fees

Python packages:
- `langchain-ollama`
- `langchain-core`
- `langchain-chroma`
- `pandas`

**AI models** (downloaded once via Ollama, then run locally for free):
- [`RefinedNeuro/Turkcell-LLM-7b-v1`](https://ollama.com/RefinedNeuro/Turkcell-LLM-7b-v1) — a Turkish-language model that writes the answers
- [`mxbai-embed-large`](https://ollama.com/library/mxbai-embed-large) — the model that helps search tweets by meaning rather than exact keywords

## Installation

```bash
# 1. Install Ollama (one-time setup)
# Download from https://ollama.com and follow the installer for your OS

# 2. Download the required AI models
ollama pull RefinedNeuro/Turkcell-LLM-7b-v1
ollama pull mxbai-embed-large

# 3. Install Python dependencies
pip install -r requirements.txt
```

**Dataset:** Download the preprocessed tweet dataset from Kaggle:
[Turkey Earthquake Relief Tweets Dataset](https://www.kaggle.com/datasets/onatkaya1/turkey-earthquake-relief-tweets-dataset)

Extract `dataset.csv` and place it at `data/dataset.csv`. The dataset is pre-processed and ready to use, as previously mentioned.


## How to run it

```bash
python src/main.py
```

Ask a question in Turkish (like `Hatay'da ne tür yardımlar isteniyordu?`) and press Enter. Type `q` or `Q` to quit.

## Cost & Privacy

Everything runs locally, so there's no per-question cost and your data never leaves your machine.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

The preprocessed and original dataset are Creative Commons licensed.


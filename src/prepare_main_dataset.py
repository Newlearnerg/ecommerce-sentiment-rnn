import os
import pandas as pd

INPUT_PATH = "data/Bản sao của data_new.csv"
OUTPUT_PATH = "data/data_main_clean.csv"
VALID_LABELS = {"positive", "negative", "neutral", "other"}


def clean_main_dataset(input_path=INPUT_PATH, output_path=OUTPUT_PATH):
    df = pd.read_csv(input_path, encoding="utf-8-sig")

    expected_cols = ["user", "review", "rating", "app", "word_count", "label", "note"]
    present_expected = [c for c in expected_cols if c in df.columns]
    if not present_expected:
        raise ValueError("Input file does not contain expected columns.")

    # Keep only expected columns and drop malformed unnamed trailing columns.
    df = df[present_expected].copy()

    if "note" not in df.columns:
        df["note"] = ""

    # Basic normalization.
    df["review"] = df["review"].astype(str).str.strip()
    df["app"] = df["app"].astype(str).str.strip()
    df["label"] = df["label"].astype(str).str.strip().str.lower()

    rating_num = pd.to_numeric(df["rating"], errors="coerce")
    word_count_num = pd.to_numeric(df["word_count"], errors="coerce")
    df["rating"] = rating_num

    # Recompute word_count when missing/invalid.
    recomputed_wc = df["review"].str.split().str.len()
    df["word_count"] = word_count_num.where(word_count_num.notna(), recomputed_wc)

    invalid_label_mask = (~df["label"].isin(VALID_LABELS)) & (df["label"] != "")
    invalid_label_count = int(invalid_label_mask.sum())

    # Keep rows that are either valid labels or unlabeled (for further manual annotation).
    df_clean = df[(df["label"].isin(VALID_LABELS)) | (df["label"] == "")].copy()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_clean.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Input rows: {len(df):,}")
    print(f"Output rows: {len(df_clean):,}")
    print(f"Dropped invalid-label rows: {len(df) - len(df_clean):,}")
    print(f"Invalid non-empty labels found: {invalid_label_count:,}")
    print("\nLabel distribution (non-empty):")
    print(df_clean[df_clean["label"] != ""]["label"].value_counts())
    print(f"\nSaved cleaned dataset to: {output_path}")


if __name__ == "__main__":
    clean_main_dataset()

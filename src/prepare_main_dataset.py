import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.utils import resample
from sklearn.model_selection import train_test_split

INPUT_PATH = "data/data_final.csv"
OUTPUT_PATH = "data/data_main_clean.csv"
TRAIN_OUTPUT_PATH = "data/data_main_train.csv"
TEST_OUTPUT_PATH = "data/data_main_test.csv"
TRAIN_BALANCED_OUTPUT_PATH = "data/data_main_train_balanced.csv"
VALID_LABELS = {"positive", "negative", "neutral", "other"}
RESULTS_DIR = "results"
LABEL_ORDER = ["negative", "positive", "neutral", "other"]
MAX_UPSAMPLE_MULTIPLIER = 3


def _plot_label_counts(before_counts, after_counts):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    before = before_counts.reindex(LABEL_ORDER, fill_value=0)
    after = after_counts.reindex(LABEL_ORDER, fill_value=0)
    plot_df = pd.DataFrame({
        "label": LABEL_ORDER * 2,
        "count": list(before.values) + list(after.values),
        "stage": ["before_balance"] * len(LABEL_ORDER) + ["after_balance"] * len(LABEL_ORDER),
    })

    plt.figure(figsize=(9, 5))
    sns.barplot(data=plot_df, x="label", y="count", hue="stage", palette="Set2")
    plt.title("Label Distribution: Before vs After Balancing")
    plt.xlabel("Label")
    plt.ylabel("Samples")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "balance_before_after_counts.png"), dpi=150)
    plt.close()


def _plot_word_count_before_after(df_before, df_after):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    before = df_before[["label", "word_count"]].copy()
    before["stage"] = "before_balance"
    after = df_after[["label", "word_count"]].copy()
    after["stage"] = "after_balance"
    merged = pd.concat([before, after], ignore_index=True)
    merged = merged[merged["label"].isin(LABEL_ORDER)]

    plt.figure(figsize=(11, 6))
    sns.boxplot(
        data=merged,
        x="label",
        y="word_count",
        hue="stage",
        order=LABEL_ORDER,
    )
    plt.title("Word Count by Label: Before vs After Balancing")
    plt.xlabel("Label")
    plt.ylabel("Words per review")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "balance_before_after_word_count.png"), dpi=150)
    plt.close()


def balance_dataset(df):
    labeled = df[df["label"].isin(VALID_LABELS)].copy()
    counts = labeled["label"].value_counts().sort_values(ascending=False)
    if counts.empty:
        return labeled

    # Soft balancing: use the 2nd largest class as anchor to avoid extreme duplication.
    target_size = int(counts.iloc[1]) if len(counts) > 1 else int(counts.iloc[0])

    balanced_parts = []
    for label in LABEL_ORDER:
        subset = labeled[labeled["label"] == label]
        if subset.empty:
            continue

        max_for_label = int(len(subset) * MAX_UPSAMPLE_MULTIPLIER)
        desired_size = min(target_size, max_for_label)

        if len(subset) < desired_size:
            subset_balanced = resample(
                subset,
                replace=True,
                n_samples=desired_size,
                random_state=42,
            )
        else:
            subset_balanced = subset.copy()
        balanced_parts.append(subset_balanced)

    balanced = pd.concat(balanced_parts, ignore_index=True)
    balanced = balanced.sample(frac=1.0, random_state=42).reset_index(drop=True)
    return balanced


def clean_main_dataset(
    input_path=INPUT_PATH,
    output_path=OUTPUT_PATH,
    train_output_path=TRAIN_OUTPUT_PATH,
    test_output_path=TEST_OUTPUT_PATH,
    train_balanced_output_path=TRAIN_BALANCED_OUTPUT_PATH,
):
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

    df_labeled = df_clean[df_clean["label"].isin(VALID_LABELS)].copy()
    full_counts = df_labeled["label"].value_counts()

    df_train, df_test = train_test_split(
        df_labeled,
        test_size=0.2,
        random_state=42,
        stratify=df_labeled["label"],
    )

    train_before_counts = df_train["label"].value_counts()

    print(f"Input rows: {len(df):,}")
    print(f"Clean rows: {len(df_clean):,}")
    print(f"Labeled rows for modeling: {len(df_labeled):,}")
    print(f"Dropped invalid-label rows: {len(df) - len(df_clean):,}")
    print(f"Invalid non-empty labels found: {invalid_label_count:,}")
    print("\nSample rows before balance:")
    print(
        df_train[["review", "label"]]
        .head(5)
        .to_string(index=False)
    )
    print("\nFull labeled distribution (before split):")
    print(full_counts.reindex(LABEL_ORDER, fill_value=0))

    print("\nTrain distribution before balance:")
    print(train_before_counts.reindex(LABEL_ORDER, fill_value=0))

    print("\nTest distribution (kept original):")
    print(df_test["label"].value_counts().reindex(LABEL_ORDER, fill_value=0))

    df_train_balanced = balance_dataset(df_train)
    train_after_counts = df_train_balanced["label"].value_counts()

    df_train.to_csv(train_output_path, index=False, encoding="utf-8-sig")
    df_test.to_csv(test_output_path, index=False, encoding="utf-8-sig")
    df_train_balanced.to_csv(train_balanced_output_path, index=False, encoding="utf-8-sig")

    print("\nTrain distribution after balance:")
    print(train_after_counts.reindex(LABEL_ORDER, fill_value=0))
    print(
        f"\nBalancing strategy: soft upsampling (anchor=2nd largest class, "
        f"max multiplier={MAX_UPSAMPLE_MULTIPLIER}x per class)"
    )

    _plot_label_counts(train_before_counts, train_after_counts)
    _plot_word_count_before_after(
        df_train,
        df_train_balanced,
    )

    print(f"\nSaved cleaned dataset to: {output_path}")
    print(f"Saved train split to: {train_output_path}")
    print(f"Saved test split to: {test_output_path}")
    print(f"Saved balanced train dataset to: {train_balanced_output_path}")
    print(f"Saved balance plots to: {RESULTS_DIR}/")


if __name__ == "__main__":
    clean_main_dataset()

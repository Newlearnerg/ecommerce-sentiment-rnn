import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

DATA_PATH = "data/Bản sao của data_new.csv"
CLEAN_DATA_PATH = "data/data_main_clean.csv"
RESULTS_DIR = "results"
VALID_LABELS = ["negative", "neutral", "positive", "other"]
REQUIRED_COLUMNS = ["review", "label", "app", "rating"]


def load_dataset(path=DATA_PATH):
    read_path = CLEAN_DATA_PATH if os.path.exists(CLEAN_DATA_PATH) else path
    df = pd.read_csv(read_path, encoding="utf-8-sig")
    print(f"Using dataset: {read_path}")

    # Keep only the expected columns if malformed extra columns exist.
    safe_cols = [c for c in ["user", "review", "rating", "app", "word_count", "label", "note"] if c in df.columns]
    if safe_cols:
        df = df[safe_cols].copy()

    if "label" in df.columns:
        df["label"] = df["label"].astype(str).str.strip().str.lower()

    if "review" in df.columns:
        df["review"] = df["review"].astype(str)

    if "word_count" not in df.columns and "review" in df.columns:
        df["word_count"] = df["review"].str.split().str.len()

    return df


def save_plot(fig, filename):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, filename), dpi=150)
    plt.close(fig)


def plot_class_distribution(df):
    counts = df["label"].value_counts().reindex(VALID_LABELS, fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=counts.index, y=counts.values, palette="Set2", ax=ax)
    ax.set_title("Class Distribution (4 labels)")
    ax.set_xlabel("Label")
    ax.set_ylabel("Samples")
    for i, v in enumerate(counts.values):
        ax.text(i, v, str(v), ha="center", va="bottom", fontsize=9)
    save_plot(fig, "eda_class_distribution.png")


def plot_word_count_distribution(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(df["word_count"].dropna(), bins=40, kde=True, ax=ax, color="#2E86AB")
    ax.set_title("Word Count Distribution")
    ax.set_xlabel("Words per review")
    save_plot(fig, "eda_word_count_hist.png")

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.boxplot(data=df[df["label"].isin(VALID_LABELS)], x="label", y="word_count", order=VALID_LABELS, ax=ax)
    ax.set_title("Word Count by Label")
    ax.set_xlabel("Label")
    ax.set_ylabel("Words per review")
    save_plot(fig, "eda_word_count_by_label_box.png")


def plot_label_by_app(df):
    ctab = pd.crosstab(df["app"], df["label"])
    ctab = ctab.reindex(columns=VALID_LABELS, fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 6))
    ctab.plot(kind="bar", stacked=True, ax=ax, colormap="tab20")
    ax.set_title("Label Distribution by App")
    ax.set_xlabel("App")
    ax.set_ylabel("Samples")
    ax.legend(title="Label")
    save_plot(fig, "eda_label_by_app.png")


def plot_rating_label_heatmap(df):
    # Convert rating to numeric and keep expected range where possible.
    rating_num = pd.to_numeric(df["rating"], errors="coerce")
    temp = df.copy()
    temp["rating_num"] = rating_num
    ctab = pd.crosstab(temp["rating_num"], temp["label"])
    ctab = ctab.reindex(columns=VALID_LABELS, fill_value=0)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(ctab, annot=True, fmt="d", cmap="YlGnBu", ax=ax)
    ax.set_title("Rating x Label")
    ax.set_xlabel("Label")
    ax.set_ylabel("Rating")
    save_plot(fig, "eda_rating_label_heatmap.png")


def plot_missingness(df):
    miss = df[REQUIRED_COLUMNS].isna().sum()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=miss.index, y=miss.values, palette="rocket", ax=ax)
    ax.set_title("Missing Values (Required Columns)")
    ax.set_xlabel("Column")
    ax.set_ylabel("Missing rows")
    for i, v in enumerate(miss.values):
        ax.text(i, v, str(int(v)), ha="center", va="bottom", fontsize=9)
    save_plot(fig, "eda_missing_required_columns.png")


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    df = load_dataset(DATA_PATH)

    missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    df_valid = df[df["label"].isin(VALID_LABELS)].copy()
    invalid_label_count = len(df) - len(df_valid)

    print(f"Total rows: {len(df):,}")
    print(f"Valid labeled rows: {len(df_valid):,}")
    print(f"Invalid/unknown label rows: {invalid_label_count:,}")
    print("\nLabel counts:")
    print(df_valid["label"].value_counts().reindex(VALID_LABELS, fill_value=0))

    plot_class_distribution(df_valid)
    plot_word_count_distribution(df_valid)
    plot_label_by_app(df_valid)
    plot_rating_label_heatmap(df_valid)
    plot_missingness(df)

    print("\nSaved plots to results/")


if __name__ == "__main__":
    main()

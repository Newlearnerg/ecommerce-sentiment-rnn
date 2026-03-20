from google_play_scraper import reviews, Sort
import pandas as pd
import re
import time
import os

APPS = {
    "com.shopee.vn"      : "Shopee",
    "vn.tiki.app.tikiandroid"    : "Tiki",
    "com.lazada.android" : "Lazada",
    "com.sendo"       : "Sendo",
}

OUTPUT_PATH = "data/reviews_raw_filtered.csv"

# Mục tiêu tăng dữ liệu cho từng nhóm ứng viên.
TARGET_COUNTS = {
    "neutral_candidate": 3500,  # review 3-4 sao
    "positive_candidate": 1000, # review 5 sao
    "spam_candidate": 1200,     # quảng cáo / ký tự vô nghĩa
}

# Cào rộng trước để có đủ nguồn mẫu cho bước chọn theo quota.
RAW_FETCH_PER_APP = 12000

def clean_text(text):
    text = str(text).lower().strip()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def is_spam_like(text):
    text = str(text).strip().lower()
    if not text:
        return True

    ad_pattern = (
        r"(inbox|ib\b|zalo|telegram|li[eê]n h[eệ]|"
        r"li[eê]n h[eệ] m[ìi]nh|s[ốo] ?đi[eệ]n ?tho[ạa]i|sđt|"
        r"khuy[eế]n m[aạ]i|m[aã] gi[aả]m gi[aá]|"
        r"click|nh[aắ]n tin|hotline|0\d{9,10})"
    )
    if re.search(ad_pattern, text):
        return True

    # Nhiều ký tự lặp hoặc nhiều ký tự không mang ngữ nghĩa.
    if re.search(r"(.)\1{5,}", text):
        return True

    non_word_ratio = len(re.findall(r"[^\w\s]", text)) / max(len(text), 1)
    if len(text) <= 25 and non_word_ratio > 0.35:
        return True

    token_count = len(text.split())
    if token_count <= 2 and re.search(r"[^a-zA-ZÀ-ỹ\d\s]", text):
        return True

    return False


def crawl_app(app_id, app_name, n=RAW_FETCH_PER_APP):
    all_reviews, token = [], None
    while len(all_reviews) < n:
        result, token = reviews(
            app_id, lang="vi", country="vn",
            sort=Sort.NEWEST, count=200,
            continuation_token=token
        )
        all_reviews.extend(result)
        print(f"  [{app_name}] {len(all_reviews)} raw reviews...")
        if not token:
            break
        time.sleep(1)

    df = pd.DataFrame(all_reviews[:n])[["userName", "content", "score", "at"]]
    df.columns = ["user", "review", "rating", "date"]
    df["app"]        = app_name
    df["review"]     = df["review"].apply(clean_text)
    df["word_count"] = df["review"].str.split().str.len()
    return df


def merge_with_existing(new_df, output_path=OUTPUT_PATH):
    if not os.path.exists(output_path):
        return new_df.reset_index(drop=True)

    df_existing = pd.read_csv(output_path, encoding="utf-8-sig")
    combined_df = pd.concat([df_existing, new_df], ignore_index=True)

    # Giữ cùng một review nếu nó thuộc app khác nhau, chỉ loại trùng trong cùng app.
    combined_df = combined_df.drop_duplicates(subset=["app", "review"])
    combined_df = combined_df.reset_index(drop=True)
    return combined_df


def pick_quota(df, mask, n, random_state=42):
    pool = df[mask]
    if len(pool) <= n:
        return pool.copy()
    return pool.sample(n=n, random_state=random_state)


def build_target_dataset(df_raw):
    df_raw = df_raw.drop_duplicates(subset=["app", "review"])
    df_raw = df_raw.dropna(subset=["review"])
    df_raw = df_raw.reset_index(drop=True)

    df_raw["is_spam_candidate"] = df_raw["review"].apply(is_spam_like)

    spam_df = pick_quota(
        df_raw,
        df_raw["is_spam_candidate"],
        TARGET_COUNTS["spam_candidate"],
    )
    spam_df["target_group"] = "spam_candidate"

    used_idx = set(spam_df.index)

    neutral_mask = (
        df_raw["rating"].isin([3, 4])
        & (~df_raw["is_spam_candidate"])
        & (~df_raw.index.isin(used_idx))
    )
    neutral_df = pick_quota(
        df_raw,
        neutral_mask,
        TARGET_COUNTS["neutral_candidate"],
    )
    neutral_df["target_group"] = "neutral_candidate"
    used_idx.update(neutral_df.index)

    positive_mask = (
        (df_raw["rating"] == 5)
        & (~df_raw["is_spam_candidate"])
        & (~df_raw.index.isin(used_idx))
    )
    positive_df = pick_quota(
        df_raw,
        positive_mask,
        TARGET_COUNTS["positive_candidate"],
    )
    positive_df["target_group"] = "positive_candidate"

    df_target = pd.concat([neutral_df, positive_df, spam_df], ignore_index=True)
    df_target = df_target.drop_duplicates(subset=["app", "review"])
    df_target = df_target.reset_index(drop=True)
    return df_target


def print_target_summary(df_target):
    print("\n📊 Kết quả theo nhóm mục tiêu:")
    print(df_target["target_group"].value_counts())
    print("\n📊 Phân bố app:")
    print(df_target["app"].value_counts())

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    all_dfs = []
    for app_id, app_name in APPS.items():
        print(f"\n🔄 Crawling {app_name}...")
        all_dfs.append(crawl_app(app_id, app_name))

    df_raw = pd.concat(all_dfs, ignore_index=True)

    df_target = build_target_dataset(df_raw)
    df_target.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"\n✅ Tổng mẫu theo quota: {len(df_target):,}")
    print_target_summary(df_target)

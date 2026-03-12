from google_play_scraper import reviews, Sort
import pandas as pd
import re
import time
import os

APPS = {
    "com.shopee.vn"      : "Shopee",
    "vn.tiki.android"    : "Tiki",
    "com.lazada.android" : "Lazada",
    "vn.sendo.app"       : "Sendo",
}

def clean_text(text):
    text = str(text).lower().strip()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

def crawl_app(app_id, app_name, n=2500):
    all_reviews, token = [], None
    while len(all_reviews) < n:
        result, token = reviews(
            app_id, lang="vi", country="vn",
            sort=Sort.NEWEST, count=200,
            continuation_token=token
        )
        all_reviews.extend(result)
        print(f"  [{app_name}] {len(all_reviews)} reviews...")
        if not token:
            break
        time.sleep(1)

    df = pd.DataFrame(all_reviews[:n])[["userName", "content", "score", "at"]]
    df.columns = ["user", "review", "rating", "date"]
    df["app"]        = app_name
    df["review"]     = df["review"].apply(clean_text)
    df["word_count"] = df["review"].str.split().str.len()
    return df

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    all_dfs = []
    for app_id, app_name in APPS.items():
        print(f"\n🔄 Crawling {app_name}...")
        all_dfs.append(crawl_app(app_id, app_name))

    df_raw = pd.concat(all_dfs, ignore_index=True)

    # Lọc cơ bản
    df_raw = df_raw[df_raw["word_count"] >= 5]
    df_raw = df_raw[df_raw["word_count"] <= 100]
    df_raw = df_raw.drop_duplicates(subset=["review"])
    df_raw = df_raw.dropna(subset=["review"])
    df_raw = df_raw.reset_index(drop=True)

    df_raw.to_csv("data/reviews_raw_filtered.csv", index=False, encoding="utf-8-sig")
    print(f"\n✅ Tổng mẫu sau lọc: {len(df_raw):,}")
    print(df_raw["app"].value_counts())

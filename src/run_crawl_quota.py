import os
import pandas as pd

import crawler_chplay as crawler

# Target mix requested by user.
TARGET_COUNTS = {
    "neutral_candidate": 3500,
    "positive_candidate": 1000,
    "spam_candidate": 1200,
}

OUTPUT_PATH = "data/reviews_raw_balanced_quota.csv"


def main():
    os.makedirs("data", exist_ok=True)

    # Update target counts without changing base crawler source again.
    crawler.TARGET_COUNTS.update(TARGET_COUNTS)

    all_dfs = []
    for app_id, app_name in crawler.APPS.items():
        print(f"\nCrawling {app_name}...")
        all_dfs.append(crawler.crawl_app(app_id, app_name))

    df_raw = pd.concat(all_dfs, ignore_index=True)
    df_target = crawler.build_target_dataset(df_raw)

    df_target.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"\nSaved: {OUTPUT_PATH}")
    print(f"Total rows: {len(df_target):,}")
    crawler.print_target_summary(df_target)


if __name__ == "__main__":
    main()

import pandas as pd
import os

def export_annotation_csv(input_path="data/reviews_raw_filtered.csv",
                           output_path="data/annotation_todo.csv",
                           n_per_app=1000):
    """
    Tạo file CSV để dán nhãn tay.
    Mỗi app lấy n_per_app mẫu, tổng cộng 4 app = 4000 mẫu.
    """
    df_raw = pd.read_csv(input_path, encoding="utf-8-sig")

    # Lấy mẫu cân bằng giữa các app
    df_sample = (
        df_raw
        .groupby("app", group_keys=False)
        .apply(lambda x: x.sample(min(len(x), n_per_app), random_state=42))
        .reset_index(drop=True)
    )

    # Thêm cột label trống và note
    df_sample["label"] = ""   # Annotator điền: positive / negative / neutral
    df_sample["note"]  = ""   # Ghi chú nếu khó phân loại

    # Sắp xếp cột
    df_annotation = df_sample[[
        "app", "review", "rating", "word_count", "date", "label", "note"
    ]].sort_values("app").reset_index(drop=True)

    # Thêm ID
    df_annotation.insert(0, "id", range(1, len(df_annotation) + 1))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_annotation.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✅ Đã xuất {len(df_annotation):,} mẫu → {output_path}")
    print("\nHướng dẫn:")
    print("  - Mở file bằng Excel hoặc Google Sheets")
    print("  - Điền vào cột 'label': positive / negative / neutral")
    print("  - Xem ANNOTATION_GUIDELINE.md để biết quy tắc dán nhãn")
    return df_annotation


if __name__ == "__main__":
    export_annotation_csv()

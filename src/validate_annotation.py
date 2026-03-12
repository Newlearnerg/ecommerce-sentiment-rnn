import pandas as pd
from sklearn.metrics import cohen_kappa_score
import os

VALID_LABELS = {"positive", "negative", "neutral"}


def validate_annotation(input_path="data/annotation_done.csv",
                         output_path="data/annotation_final.csv"):
    """Kiểm tra và làm sạch file CSV đã dán nhãn"""
    df = pd.read_csv(input_path, encoding="utf-8-sig")

    # Chuẩn hóa label
    df["label"] = df["label"].str.strip().str.lower()

    invalid = df[~df["label"].isin(VALID_LABELS) & (df["label"].notna()) & (df["label"] != "")]
    skipped = df[df["note"].str.lower().str.contains("skip", na=False)]

    print(f"✅ Tổng mẫu         : {len(df):,}")
    print(f"❌ Nhãn sai/thiếu   : {len(invalid)}")
    print(f"⏭️  Mẫu bị skip     : {len(skipped)}")

    if len(invalid) > 0:
        print("\nCác dòng nhãn không hợp lệ:")
        print(invalid[["id", "review", "label"]].to_string())

    # Giữ lại mẫu hợp lệ
    df_valid = df[
        df["label"].isin(VALID_LABELS) &
        ~df["note"].str.lower().str.contains("skip", na=False)
    ].copy()

    print(f"\n📊 Phân bố nhãn:")
    print(df_valid["label"].value_counts())
    print(df_valid["label"].value_counts(normalize=True).mul(100).round(1).astype(str) + "%")

    print(f"\n📱 Phân bố theo App:")
    print(df_valid.groupby(["app", "label"]).size().unstack(fill_value=0))

    df_valid.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n✅ Lưu {len(df_valid):,} mẫu → {output_path}")
    return df_valid


def compute_kappa(ann1_path, ann2_path):
    """Tính Cohen's Kappa giữa 2 annotators"""
    ann1 = pd.read_csv(ann1_path)["label"].str.strip().str.lower()
    ann2 = pd.read_csv(ann2_path)["label"].str.strip().str.lower()

    kappa = cohen_kappa_score(ann1, ann2)
    print(f"\nCohen's Kappa = {kappa:.3f}")
    if   kappa >= 0.8: print("✅✅ Rất tốt  — Độ tin cậy cao")
    elif kappa >= 0.6: print("✅   Tốt     — Chấp nhận được")
    elif kappa >= 0.4: print("⚠️   Trung bình — Cần review lại guideline")
    else:              print("❌   Kém     — Cần thống nhất lại tiêu chí")
    return kappa


if __name__ == "__main__":
    validate_annotation()

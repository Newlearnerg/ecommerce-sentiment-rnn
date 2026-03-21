import time
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report, confusion_matrix,
    precision_recall_curve, roc_curve, auc,
)
from sklearn.preprocessing import label_binarize


CLASS_NAMES = ["Negative", "Neutral", "Positive", "Other"]
RESULTS_DIR = "results"
MODELS_DIR = "models"
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


def _prepare_run_dirs(model_name):
    run_results_dir = os.path.join(RESULTS_DIR, model_name)
    run_models_dir = os.path.join(MODELS_DIR, model_name)
    os.makedirs(run_results_dir, exist_ok=True)
    os.makedirs(run_models_dir, exist_ok=True)
    return run_results_dir, run_models_dir


def evaluate_model(
    model,
    X_test,
    y_test,
    model_name,
    history=None,
    train_time_sec=None,
    train_samples=None,
    train_epochs=None,
):
    """Đánh giá model toàn diện và lưu kết quả"""
    results = {}
    run_results_dir, run_models_dir = _prepare_run_dirs(model_name)

    # 1. Predict + đo thời gian inference
    t0     = time.time()
    y_prob = model.predict(X_test, verbose=0)
    t_infer = time.time() - t0
    y_pred = np.argmax(y_prob, axis=1)

    # 2. Metrics chính
    report = classification_report(
        y_test, y_pred,
        target_names=CLASS_NAMES,
        output_dict=True, zero_division=0
    )
    results["model"]     = model_name
    results["accuracy"]  = round(report["accuracy"], 4)
    results["precision"] = round(report["macro avg"]["precision"], 4)
    results["recall"]    = round(report["macro avg"]["recall"], 4)
    results["f1"]        = round(report["macro avg"]["f1-score"], 4)

    # 3. Kích thước model
    model_path = os.path.join(run_models_dir, f"{model_name}.keras")
    model.save(model_path)
    results["model_size_mb"] = round(os.path.getsize(model_path) / (1024 * 1024), 2)
    results["trainable_params"] = int(model.count_params())

    # 4. FPS
    results["fps"] = round(len(X_test) / t_infer, 1)
    results["inference_time_sec"] = round(t_infer, 3)

    # 4.1 Training performance
    if train_time_sec is not None and train_time_sec > 0:
        results["train_time_sec"] = round(train_time_sec, 2)
        if train_samples is not None:
            results["train_samples_per_sec"] = round(train_samples / train_time_sec, 1)
        if train_epochs is not None and train_epochs > 0:
            results["sec_per_epoch"] = round(train_time_sec / train_epochs, 2)
    else:
        results["train_time_sec"] = np.nan
        results["train_samples_per_sec"] = np.nan
        results["sec_per_epoch"] = np.nan

    # 5. Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
    plt.title(f"Confusion Matrix — {model_name}")
    plt.tight_layout()
    plt.savefig(os.path.join(run_results_dir, "confusion_matrix.png"), dpi=120)
    plt.close()

    # 6. Precision-Recall Curve
    y_bin = label_binarize(y_test, classes=list(range(len(CLASS_NAMES))))
    fig, ax = plt.subplots(figsize=(7, 5))
    for i, cls in enumerate(CLASS_NAMES):
        p, r, _ = precision_recall_curve(y_bin[:, i], y_prob[:, i])
        ax.plot(r, p, label=f"{cls} (AUC={auc(r, p):.2f})")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title(f"Precision-Recall Curve — {model_name}")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(run_results_dir, "precision_recall_curve.png"), dpi=120)
    plt.close()

    # 7. ROC-AUC Curve
    fig, ax = plt.subplots(figsize=(7, 5))
    for i, cls in enumerate(CLASS_NAMES):
        fpr, tpr, _ = roc_curve(y_bin[:, i], y_prob[:, i])
        ax.plot(fpr, tpr, label=f"{cls} (AUC={auc(fpr, tpr):.2f})")
    ax.plot([0, 1], [0, 1], "k--")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(f"ROC-AUC Curve — {model_name}")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(run_results_dir, "roc_curve.png"), dpi=120)
    plt.close()

    # 8. Training curves
    if history:
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        axes[0].plot(history.history["loss"], label="Train")
        axes[0].plot(history.history["val_loss"], label="Val")
        axes[0].set_title(f"Loss — {model_name}")
        axes[0].legend()
        axes[1].plot(history.history["accuracy"], label="Train")
        axes[1].plot(history.history["val_accuracy"], label="Val")
        axes[1].set_title(f"Accuracy — {model_name}")
        axes[1].legend()
        plt.tight_layout()
        plt.savefig(os.path.join(run_results_dir, "training_curves.png"), dpi=120)
        plt.close()

        # 9. Save per-model report for easier inspection
        report_df = pd.DataFrame(report).transpose()
        report_df.to_csv(os.path.join(run_results_dir, "classification_report.csv"), index=True)

        metrics_row = pd.DataFrame([results])
        metrics_row.to_csv(os.path.join(run_results_dir, "metrics.csv"), index=False)

    print(f"\n[{model_name}] Acc={results['accuracy']:.4f} | "
            f"F1={results['f1']:.4f} | FPS={results['fps']} | "
            f"Train={results['train_time_sec']}s | "
            f"Params={results['trainable_params']:,} | "
            f"Size={results['model_size_mb']}MB")
    return results


def compare_all_models(all_results):
    """Tạo bảng so sánh và biểu đồ tổng hợp tất cả models"""
    df = pd.DataFrame(all_results).sort_values("f1", ascending=False)

    print("\n" + "=" * 70)
    print(df.to_string(index=False))
    print("=" * 70)

    df.to_csv(f"{RESULTS_DIR}/model_comparison.csv", index=False)

    # Biểu đồ so sánh metrics
    metrics = ["accuracy", "precision", "recall", "f1"]
    fig, axes = plt.subplots(1, 4, figsize=(18, 5))
    fig.suptitle("So sánh hiệu năng các mô hình", fontsize=13, fontweight="bold")
    for ax, metric in zip(axes, metrics):
        bars = ax.barh(df["model"], df[metric], color="#3498db")
        ax.set_xlim(0.5, 1.0)
        ax.set_title(metric.capitalize())
        ax.bar_label(bars, fmt="%.3f", padding=3)
    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/model_comparison.png", dpi=150)
    plt.close()

    # Training time comparison
    if "train_time_sec" in df.columns and df["train_time_sec"].notna().any():
        plt.figure(figsize=(10, 6))
        bars = plt.barh(df["model"], df["train_time_sec"], color="#16a085")
        plt.title("Training Time by Model")
        plt.xlabel("Seconds")
        plt.bar_label(bars, fmt="%.1f", padding=3)
        plt.tight_layout()
        plt.savefig(f"{RESULTS_DIR}/training_time_comparison.png", dpi=150)
        plt.close()

    # FPS vs Accuracy (trade-off)
    plt.figure(figsize=(8, 6))
    for _, row in df.iterrows():
        plt.scatter(row["fps"], row["accuracy"],
                    s=row["model_size_mb"] * 20, alpha=0.8, label=row["model"])
        plt.annotate(row["model"], (row["fps"], row["accuracy"]),
                     textcoords="offset points", xytext=(8, 4), fontsize=9)
    plt.xlabel("FPS (samples/giây)")
    plt.ylabel("Accuracy")
    plt.title("Trade-off: Tốc độ vs Độ chính xác\n(Kích thước bong bóng = Model size)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/fps_vs_accuracy.png", dpi=150)
    plt.close()

    return df

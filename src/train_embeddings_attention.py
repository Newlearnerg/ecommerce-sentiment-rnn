import os
import argparse
import time
import pandas as pd
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

from models_all import build_model
from evaluation_full import evaluate_model, compare_all_models
from word_embeddings import (
    build_tokenizer,
    texts_to_sequences,
    get_random_embedding,
    get_word2vec_embedding,
    get_fasttext_freeze,
    get_fasttext_finetune,
)

TRAIN_DATA_PATH = "data/data_main_train_balanced.csv"
TEST_DATA_PATH = "data/data_main_test.csv"
VALID_LABELS = ["negative", "neutral", "positive", "other"]
LABEL_TO_ID = {label: idx for idx, label in enumerate(VALID_LABELS)}

# ============================================================================
# EASY CONFIG: Comment/uncomment model combinations below
# Format: (embedding_id, model_type)
# Embeddings: 1=Random, 2=Word2Vec, 3=FastText-freeze, 4=FastText-finetune
# Models (explicit attention):
#   RNN, LSTM, GRU, BiLSTM, BiGRU, CNN_BiLSTM, CNN_BiGRU
#   BiLSTM_DotAttention, CNN_BiLSTM_DotAttention
#   TransformerEncoder, CNN_TransformerEncoder
# ============================================================================
USE_CONFIG_MODE = True  # One-person full run mode by default

FULL_EMBEDDINGS = [1, 2, 3, 4]
FULL_MODELS = [
    "RNN",
    "LSTM",
    "GRU",
    "BiLSTM",
    "BiGRU",
    "CNN_BiLSTM",
    "CNN_BiGRU",
    "BiLSTM_DotAttention",
    "CNN_BiLSTM_DotAttention",
    "TransformerEncoder",
    "CNN_TransformerEncoder",
]

# Single user runs all embeddings x all models.
TRAINING_CONFIG = [(emb_id, model_type) for emb_id in FULL_EMBEDDINGS for model_type in FULL_MODELS]
# ============================================================================


def normalize_text(text):
    return str(text).strip().lower()


def load_dataset(path):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found at {path}. Run src/prepare_main_dataset.py first."
        )

    df = pd.read_csv(path, encoding="utf-8-sig")
    required = ["review", "label"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df[df["label"].isin(VALID_LABELS)].copy()
    df["text"] = df["review"].apply(normalize_text)
    df["y"] = df["label"].map(LABEL_TO_ID)
    return df


def build_embedding_by_id(embedding_id, X_train_text, tokenizer, pretrained_path):
    word_index = tokenizer.word_index

    if embedding_id == "1":
        return get_random_embedding(), "E1_Random"

    if embedding_id == "2":
        emb, _ = get_word2vec_embedding(X_train_text, word_index)
        return emb, "E2_Word2Vec"

    if embedding_id == "3":
        if not pretrained_path:
            raise ValueError("Embedding 3 requires --fasttext_path")
        emb = get_fasttext_freeze(pretrained_path, word_index)
        return emb, "E3_FastTextFreeze"

    if embedding_id == "4":
        if not pretrained_path:
            raise ValueError("Embedding 4 requires --fasttext_path")
        emb = get_fasttext_finetune(pretrained_path, word_index)
        return emb, "E4_FastTextFinetune"

    raise ValueError(f"Unknown embedding id: {embedding_id}")


def main():
    parser = argparse.ArgumentParser(description="Train models with embeddings 1-4 and attention")
    parser.add_argument(
        "--train_data",
        default=TRAIN_DATA_PATH,
        help="Path to balanced train dataset",
    )
    parser.add_argument(
        "--test_data",
        default=TEST_DATA_PATH,
        help="Path to original test dataset",
    )
    parser.add_argument("--epochs", type=int, default=3, help="Training epochs")
    parser.add_argument("--batch_size", type=int, default=64, help="Batch size")
    parser.add_argument(
        "--models",
        default=(
            "RNN,LSTM,GRU,BiLSTM,BiGRU,CNN_BiLSTM,CNN_BiGRU,"
            "BiLSTM_DotAttention,CNN_BiLSTM_DotAttention,"
            "TransformerEncoder,CNN_TransformerEncoder"
        ),
        help="Comma-separated model types",
    )
    parser.add_argument(
        "--embeddings",
        default="1,2,3,4",
        help="Comma-separated embedding ids to retrain",
    )
    parser.add_argument(
        "--fasttext_path",
        default="",
        help="Path to cc.vi.300.bin for embeddings 3 and 4",
    )
    args = parser.parse_args()

    # Use config mode or command-line arguments
    if USE_CONFIG_MODE:
        print("=" * 70)
        print("USING CONFIG MODE (TRAINING_CONFIG)")
        print("=" * 70)
        print(f"Training {len(TRAINING_CONFIG)} model combinations:")
        for emb_id, model_type in TRAINING_CONFIG:
            print(f"  - Embedding {emb_id} + {model_type}")
        print()
    else:
        print("=" * 70)
        print("USING COMMAND-LINE MODE (--embeddings & --models)")
        print("=" * 70)
        print()

    df_train = load_dataset(args.train_data)
    df_test = load_dataset(args.test_data)

    print("Loaded train rows:", len(df_train))
    print("Train label counts:\n", df_train["label"].value_counts().reindex(VALID_LABELS, fill_value=0))
    print("Loaded test rows:", len(df_test))
    print("Test label counts:\n", df_test["label"].value_counts().reindex(VALID_LABELS, fill_value=0))

    X_train_text = df_train["text"].values
    y_train = df_train["y"].values
    X_test_text = df_test["text"].values
    y_test = df_test["y"].values

    tokenizer = build_tokenizer(X_train_text)
    X_train = texts_to_sequences(tokenizer, X_train_text)
    X_test = texts_to_sequences(tokenizer, X_test_text)

    all_results = []
    
    # Determine which combinations to train
    if USE_CONFIG_MODE:
        training_pairs = TRAINING_CONFIG
    else:
        model_types = [m.strip() for m in args.models.split(",") if m.strip()]
        embedding_ids = [e.strip() for e in args.embeddings.split(",") if e.strip()]
        training_pairs = [(int(e), m) for e in embedding_ids for m in model_types]

    for emb_id, model_type in training_pairs:
        try:
            embedding_layer, emb_name = build_embedding_by_id(
                str(emb_id),
                X_train_text,
                tokenizer,
                args.fasttext_path,
            )
        except Exception as exc:
            print(f"Skip embedding {emb_id} + {model_type}: {exc}")
            continue
        
        run_name = f"{model_type}_{emb_name}"
        print(f"\n=== Training {run_name} ===")

        model = build_model(model_type, embedding_layer, num_classes=len(VALID_LABELS))
        
        # Compile with gradient clipping & better optimizer
        model.compile(
            optimizer=__import__('tensorflow').keras.optimizers.Adam(
                learning_rate=0.001,
                clipvalue=1.0,  # Gradient clipping
            ),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )

        # Ensure model is built before counting parameters on newer Keras versions.
        model.build(input_shape=(None, X_train.shape[1]))
        
        t0 = time.time()

        run_model_dir = os.path.join("models", run_name)
        os.makedirs(run_model_dir, exist_ok=True)
        
        # Callbacks for better training
        checkpoint = ModelCheckpoint(
            os.path.join(run_model_dir, "best_checkpoint.keras"),
            monitor='val_loss',
            save_best_only=True,
            verbose=0
        )
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=3,
            restore_best_weights=True,
            verbose=1
        )
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=2,
            min_lr=1e-7,
            verbose=1
        )
        
        print(f"Model parameters: {model.count_params():,}")
        
        history = model.fit(
            X_train,
            y_train,
            validation_split=0.1,
            epochs=args.epochs,
            batch_size=args.batch_size,
            callbacks=[checkpoint, early_stop, reduce_lr],
            verbose=1,
        )
        train_time_sec = time.time() - t0

        result = evaluate_model(
            model,
            X_test,
            y_test,
            run_name,
            history=history,
            train_time_sec=train_time_sec,
            train_samples=len(X_train) * args.epochs,
            train_epochs=args.epochs,
        )
        all_results.append(result)

    if not all_results:
        raise RuntimeError("No model was trained. Check embedding settings.")

    summary_df = compare_all_models(all_results)
    print("\nTop results:")
    print(summary_df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    SimpleRNN, LSTM, GRU, Bidirectional,
    Conv1D, MaxPooling1D,
    Dense, Dropout
)


def build_model(model_type, embedding_layer, num_classes=3):
    """
    Xây dựng model theo loại.
    model_type: 'RNN' | 'LSTM' | 'GRU' | 'BiLSTM' | 'CNN_BiLSTM'
    """
    model = Sequential(name=model_type)
    model.add(embedding_layer)

    if model_type == "RNN":
        model.add(SimpleRNN(64, return_sequences=True))
        model.add(SimpleRNN(32))

    elif model_type == "LSTM":
        model.add(LSTM(64, return_sequences=True, dropout=0.2, recurrent_dropout=0.2))
        model.add(LSTM(32, dropout=0.2))

    elif model_type == "GRU":
        model.add(GRU(64, return_sequences=True, dropout=0.2, recurrent_dropout=0.2))
        model.add(GRU(32, dropout=0.2))

    elif model_type == "BiLSTM":
        model.add(Bidirectional(LSTM(64, return_sequences=True, dropout=0.2, recurrent_dropout=0.2)))
        model.add(Bidirectional(LSTM(32, dropout=0.2)))

    elif model_type == "CNN_BiLSTM":
        model.add(Conv1D(64, kernel_size=3, activation="relu", padding="same"))
        model.add(MaxPooling1D(pool_size=2))
        model.add(Bidirectional(LSTM(64, return_sequences=True, dropout=0.2)))
        model.add(Bidirectional(LSTM(32, dropout=0.2)))

    else:
        raise ValueError(f"Unknown model_type: {model_type}. Valid options: {MODEL_TYPES}")

    model.add(Dense(64, activation="relu"))
    model.add(Dropout(0.4))
    model.add(Dense(num_classes, activation="softmax"))

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


MODEL_TYPES = ["RNN", "LSTM", "GRU", "BiLSTM", "CNN_BiLSTM"]

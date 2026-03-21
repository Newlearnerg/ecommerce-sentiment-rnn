from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import (
    SimpleRNN, LSTM, GRU, Bidirectional,
    Conv1D, MaxPooling1D,
    Dense, Dropout, Input,
    Attention, GlobalAveragePooling1D,
    MultiHeadAttention, LayerNormalization, Add
)


ATTENTION_ALIASES = {
    "BiLSTM_Attention": "BiLSTM_DotAttention",
    "CNN_BiLSTM_Attention": "CNN_BiLSTM_DotAttention",
}


def build_model(model_type, embedding_layer, num_classes=4):
    """
    Xây dựng model theo loại.
    model_type: hỗ trợ nhiều kiến trúc cơ bản + attention (DotAttention).
    """
    model_type = ATTENTION_ALIASES.get(model_type, model_type)

    if model_type in {"BiLSTM_DotAttention", "CNN_BiLSTM_DotAttention"}:
        return _build_attention_model(model_type, embedding_layer, num_classes)

    if model_type in {"TransformerEncoder", "CNN_TransformerEncoder"}:
        return _build_transformer_model(model_type, embedding_layer, num_classes)

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

    elif model_type == "BiGRU":
        model.add(Bidirectional(GRU(64, return_sequences=True, dropout=0.2, recurrent_dropout=0.2)))
        model.add(Bidirectional(GRU(32, dropout=0.2)))

    elif model_type == "CNN_BiLSTM":
        model.add(Conv1D(64, kernel_size=3, activation="relu", padding="same"))
        model.add(MaxPooling1D(pool_size=2))
        model.add(Bidirectional(LSTM(64, return_sequences=True, dropout=0.2)))
        model.add(Bidirectional(LSTM(32, dropout=0.2)))

    elif model_type == "CNN_BiGRU":
        model.add(Conv1D(64, kernel_size=3, activation="relu", padding="same"))
        model.add(MaxPooling1D(pool_size=2))
        model.add(Bidirectional(GRU(64, return_sequences=True, dropout=0.2)))
        model.add(Bidirectional(GRU(32, dropout=0.2)))

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


def _build_attention_model(model_type, embedding_layer, num_classes):
    inputs = Input(shape=(None,), dtype="int32")
    x = embedding_layer(inputs)

    if model_type == "BiLSTM_DotAttention":
        x = Bidirectional(LSTM(64, return_sequences=True, dropout=0.2))(x)

    elif model_type == "CNN_BiLSTM_DotAttention":
        x = Conv1D(64, kernel_size=3, activation="relu", padding="same")(x)
        x = MaxPooling1D(pool_size=2)(x)
        x = Bidirectional(LSTM(64, return_sequences=True, dropout=0.2))(x)

    else:
        raise ValueError(f"Unknown attention model_type: {model_type}")

    attn = Attention()([x, x])
    x = GlobalAveragePooling1D()(attn)
    x = Dense(64, activation="relu")(x)
    x = Dropout(0.4)(x)
    outputs = Dense(num_classes, activation="softmax")(x)

    model = Model(inputs=inputs, outputs=outputs, name=model_type)
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def _transformer_block(x, num_heads=4, key_dim=32, ff_dim=128, dropout_rate=0.2):
    attn_output = MultiHeadAttention(num_heads=num_heads, key_dim=key_dim, dropout=dropout_rate)(x, x)
    x = Add()([x, attn_output])
    x = LayerNormalization(epsilon=1e-6)(x)

    ff = Dense(ff_dim, activation="relu")(x)
    ff = Dropout(dropout_rate)(ff)
    ff = Dense(x.shape[-1])(ff)
    x = Add()([x, ff])
    x = LayerNormalization(epsilon=1e-6)(x)
    return x


def _build_transformer_model(model_type, embedding_layer, num_classes):
    inputs = Input(shape=(None,), dtype="int32")
    x = embedding_layer(inputs)

    if model_type == "CNN_TransformerEncoder":
        x = Conv1D(128, kernel_size=3, activation="relu", padding="same")(x)
        x = MaxPooling1D(pool_size=2)(x)

    x = _transformer_block(x, num_heads=4, key_dim=32, ff_dim=128, dropout_rate=0.2)
    x = _transformer_block(x, num_heads=4, key_dim=32, ff_dim=128, dropout_rate=0.2)
    x = GlobalAveragePooling1D()(x)
    x = Dense(64, activation="relu")(x)
    x = Dropout(0.4)(x)
    outputs = Dense(num_classes, activation="softmax")(x)

    model = Model(inputs=inputs, outputs=outputs, name=model_type)
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


MODEL_TYPES = [
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

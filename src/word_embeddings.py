import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from gensim.models.fasttext import load_facebook_model
from tensorflow.keras.layers import Embedding
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

VOCAB_SIZE = 15000
EMBED_DIM  = 128
MAX_LEN    = 100


def build_tokenizer(texts, num_words=VOCAB_SIZE):
    tokenizer = Tokenizer(num_words=num_words, oov_token="<OOV>")
    tokenizer.fit_on_texts(texts)
    return tokenizer


def texts_to_sequences(tokenizer, texts, maxlen=MAX_LEN):
    seqs = tokenizer.texts_to_sequences(texts)
    return pad_sequences(seqs, maxlen=maxlen, padding="post", truncating="post")


def build_embedding_matrix(word_index, gensim_model, embed_dim, vocab_size=VOCAB_SIZE):
    matrix = np.zeros((vocab_size, embed_dim))
    for word, idx in word_index.items():
        if idx < vocab_size:
            try:
                matrix[idx] = gensim_model.wv[word]
            except KeyError:
                pass
    return matrix


# ── Embedding 1: Random (Baseline) ────────────────────────────
def get_random_embedding(vocab_size=VOCAB_SIZE, embed_dim=EMBED_DIM, max_len=MAX_LEN):
    return Embedding(
        input_dim=vocab_size, output_dim=embed_dim,
        trainable=True, name="random_embedding"
    )


# ── Embedding 2: Word2Vec tự train ────────────────────────────
def get_word2vec_embedding(texts, word_index,
                            vocab_size=VOCAB_SIZE, embed_dim=EMBED_DIM, max_len=MAX_LEN):
    sentences = [t.split() for t in texts]
    w2v = Word2Vec(sentences, vector_size=embed_dim, window=5,
                   min_count=2, workers=4, epochs=10)
    matrix = build_embedding_matrix(word_index, w2v, embed_dim, vocab_size)
    return Embedding(vocab_size, embed_dim, weights=[matrix],
                     trainable=True, name="word2vec_embedding"), w2v


# ── Embedding 3: FastText Pretrained (Freeze) ─────────────────
def get_fasttext_freeze(pretrained_path, word_index,
                         embed_dim=300, vocab_size=VOCAB_SIZE, max_len=MAX_LEN):
    """
    Download FastText tiếng Việt:
    https://fasttext.cc/docs/en/crawl-vectors.html (cc.vi.300.bin)
    """
    ft = load_facebook_model(pretrained_path)
    matrix = build_embedding_matrix(word_index, ft, embed_dim, vocab_size)
    return Embedding(vocab_size, embed_dim, weights=[matrix],
                     trainable=False, name="fasttext_freeze")


# ── Embedding 4: FastText Fine-tune ───────────────────────────
def get_fasttext_finetune(pretrained_path, word_index,
                           embed_dim=300, vocab_size=VOCAB_SIZE, max_len=MAX_LEN):
    ft = load_facebook_model(pretrained_path)
    matrix = build_embedding_matrix(word_index, ft, embed_dim, vocab_size)
    return Embedding(vocab_size, embed_dim, weights=[matrix],
                     trainable=True, name="fasttext_finetune")

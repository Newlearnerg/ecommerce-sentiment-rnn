import re
import emoji
import unicodedata
import pandas as pd
from underthesea import word_tokenize

from teencode_dict import TEENCODE_DICT
from emoji_dict import EMOJI_SENTIMENT_MAP

# Stopwords tiếng Việt
STOPWORDS = {
    "và", "của", "là", "có", "được", "cho", "trong", "với",
    "này", "đó", "các", "một", "những", "thì", "mà",
    "hay", "hoặc", "để", "từ", "theo", "về", "như", "khi",
    "tôi", "bạn", "họ", "chúng", "nó", "ta",
    "rất", "cũng", "đã", "sẽ", "đang", "vẫn", "lại", "nên",
    "thôi", "vậy", "nhé", "nha", "ạ", "ơi", "à", "ừ", "uh",
}

# Từ phủ định - KHÔNG xóa
NEGATION_WORDS = {"không", "chưa", "chẳng", "chớ", "đừng"}


def normalize_unicode(text):
    """Chuẩn hóa Unicode - Fix lỗi font Unikey"""
    return unicodedata.normalize("NFC", str(text))


def convert_emoji_to_text(text):
    """Chuyển emoji → text có nghĩa, emoji không có trong dict thì xóa"""
    result = []
    for char in text:
        if char in EMOJI_SENTIMENT_MAP:
            # Add padding spaces so mapped emoji words do not stick to neighbors.
            result.append(f" {EMOJI_SENTIMENT_MAP[char]} ")
        elif char in emoji.EMOJI_DATA:
            pass  # Bỏ emoji không có trong dict
        else:
            result.append(char)
    return "".join(result)


def decode_teencode(text):
    """Giải mã teencode theo từ điển"""
    words = text.split()
    result = []
    for word in words:
        w_clean = re.sub(r"[^\w]", "", word)
        if w_clean in TEENCODE_DICT:
            suffix = word[len(w_clean):]
            result.append(TEENCODE_DICT[w_clean] + suffix)
        else:
            result.append(word)
    return " ".join(result)


def normalize_repeated_chars(text):
    """Chuẩn hóa ký tự lặp quá mức: 'nhaaaanh' → 'nhanh'"""
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)
    text = re.sub(r"[!]{2,}", "!", text)
    text = re.sub(r"[?]{2,}", "?", text)
    text = re.sub(r"[.]{2,}", "...", text)
    return text


def normalize_punctuation(text):
    """Chuẩn hóa dấu câu và khoảng trắng"""
    text = re.sub(
        r"[^\w\sàáạảãăắặẳẵặâấậẩẫđèéẹẻẽêếệểễìíịỉĩòóọỏõôốộổỗơớợởỡùúụủũưứựửữỳýỵỷỹ!?.,]",
        " ", text
    )
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_stopwords(text):
    """Xóa stopwords, giữ lại từ phủ định"""
    words = text.split()
    filtered = [w for w in words if w not in STOPWORDS or w in NEGATION_WORDS]
    return " ".join(filtered)


def tokenize_vietnamese(text):
    """Tách từ ghép tiếng Việt bằng Underthesea"""
    return word_tokenize(text, format="text")


def preprocess(text, tokenize=True, remove_sw=True):
    """Pipeline tiền xử lý hoàn chỉnh"""
    text = normalize_unicode(text)
    text = text.lower()
    text = convert_emoji_to_text(text)
    text = decode_teencode(text)
    text = normalize_repeated_chars(text)
    text = normalize_punctuation(text)
    if remove_sw:
        text = remove_stopwords(text)
    if tokenize:
        text = tokenize_vietnamese(text)
    return text.strip()


if __name__ == "__main__":
    # Demo
    test_cases = [
        "sp ok, ship nhanh, k bị lỗi gì dc, mik rất thik",
        "hàng giả 🤬👎 đặt 5 lần đều vậy, tệ vl!!!!!!",
        "app mượt 👍, order dc liền, nv tư vấn pro 😍",
        "nhaaaanh lắmmmmm, chất lượnggggg, thích quáaaaa!!!",
        "ko tệ lắm, cũng được, bt thôi k có gì đặc biệt",
    ]
    print(f"{'='*60}")
    for text in test_cases:
        cleaned = preprocess(text, tokenize=False)
        print(f"IN : {text}")
        print(f"OUT: {cleaned}")
        print(f"{'-'*60}")

# 🛒 Ecommerce Sentiment RNN

> Phân tích cảm xúc review ứng dụng Thương mại điện tử Việt Nam sử dụng RNN/LSTM

## 📌 Giới thiệu

Đề tài nghiên cứu bài toán **Sentiment Analysis** trên các review của người dùng về ứng dụng mua sắm trực tuyến tại Việt Nam (Shopee, Tiki, Lazada, Sendo), sử dụng các mô hình Deep Learning như RNN, LSTM, GRU, BiLSTM, CNN-BiLSTM.

## 🗂️ Cấu trúc thư mục

```
ecommerce-sentiment-rnn/
├── data/                        ← Dữ liệu (raw, annotated, processed)
├── models/                      ← Mô hình đã train
├── results/                     ← Biểu đồ, kết quả đánh giá
├── notebooks/                   ← Jupyter notebooks
├── src/
│   ├── crawler_chplay.py        ← Crawl reviews từ CH Play
│   ├── teencode_dict.py         ← Từ điển teencode tiếng Việt
│   ├── emoji_dict.py            ← Map emoji → text
│   ├── preprocessing_full.py    ← Pipeline tiền xử lý
│   ├── export_for_annotation.py ← Xuất CSV để dán nhãn tay
│   ├── validate_annotation.py   ← Kiểm tra file CSV đã dán nhãn
│   ├── word_embeddings.py       ← 4 chiến lược Word Embedding
│   ├── models_all.py            ← Các kiến trúc model (RNN/LSTM/GRU/Attention/Transformer)
│   ├── train_embeddings_attention.py ← Script train full embeddings x models
│   ├── evaluation_full.py       ← Đánh giá toàn diện + lưu theo folder từng model
│   └── prepare_main_dataset.py  ← Clean/split/balance dữ liệu chính
├── ANNOTATION_GUIDELINE.md      ← Hướng dẫn dán nhãn tay
├── requirements.txt
└── README.md
```

## 🚀 Hướng dẫn sử dụng

### 1. Cài đặt
```bash
pip install -r requirements.txt
```

### 2. Thu thập dữ liệu
```bash
python src/crawler_chplay.py
```

### 3. Xuất file để dán nhãn tay
```bash
python src/export_for_annotation.py
```
> Mở file `data/annotation_todo.csv` bằng Excel/Google Sheets
> Xem `ANNOTATION_GUIDELINE.md` để biết quy tắc dán nhãn

### 4. Tiền xử lý dữ liệu
```bash
python src/preprocessing_full.py
```

### 5. Chuẩn hóa dữ liệu chính
```bash
python src/prepare_main_dataset.py
```
> Hiển thị dữ liệu trước cân bằng, cân bằng 4 lớp, lưu:
> - `data/data_main_clean.csv`
> - `data/data_main_train.csv`
> - `data/data_main_test.csv`
> - `data/data_main_train_balanced.csv`
> - `results/balance_before_after_counts.png`
> - `results/balance_before_after_word_count.png`
> Quy trình: split train/test trước, chỉ cân bằng tập train

### 6. EDA trước khi train
```bash
python src/eda_sentiment_4class.py
```
> Script sẽ tạo biểu đồ phân bố nhãn, độ dài câu, app x label, rating x label vào thư mục `results/`

### 7. Train & Đánh giá mô hình
```bash
python src/train_embeddings_attention.py --epochs 10 --fasttext_path /path/to/cc.vi.300.bin
```
> Mặc định script đang ở chế độ **1 người chạy toàn bộ**: chạy full embeddings (1,2,3,4) x full models.
> Nếu chưa có FastText, có thể chỉ chạy embeddings 1,2:
>
> `python src/train_embeddings_attention.py --embeddings 1,2 --epochs 10`

### 8. Kết quả đầu ra
- Mỗi run model được lưu riêng:
`results/<run_name>/` (metrics, report, plots)
`models/<run_name>/` (checkpoint/model)
- Kết quả tổng hợp toàn bộ model:
`results/model_comparison.csv`
`results/model_comparison.png`
`results/fps_vs_accuracy.png`
`results/training_time_comparison.png`

## 📊 Chiến lược dán nhãn

| Nhãn | Ý nghĩa | Ví dụ |
|------|---------|-------|
| `positive` | Hài lòng, khen ngợi | "App mượt, giao hàng nhanh 👍" |
| `negative` | Không hài lòng, phàn nàn | "Hàng giả, thất vọng 🤬" |
| `neutral`  | Vừa khen vừa chê, không khen không chê, câu hỏi/off-topic | "Tốt nhưng giao hơi chậm", "Bao giờ có mã giảm giá?" |
| `other`    | Spam, quảng cáo, nội dung vô nghĩa/khó hiểu | "ib zalo 09xx", "asdfgh", "🔥🔥🔥" |

> ⚠️ Dán nhãn **dựa trên nội dung văn bản**, KHÔNG phụ thuộc vào số sao rating

## 🧠 Các mô hình so sánh

| Model | Đặc điểm |
|-------|----------|
| RNN | Baseline đơn giản |
| LSTM | Xử lý long-range dependency |
| GRU | Nhẹ hơn LSTM, nhanh hơn |
| BiLSTM | Đọc 2 chiều với LSTM |
| BiGRU | Đọc 2 chiều với GRU |
| CNN_BiLSTM | CNN + BiLSTM |
| CNN_BiGRU | CNN + BiGRU |
| BiLSTM_DotAttention | BiLSTM + Dot Attention |
| CNN_BiLSTM_DotAttention | CNN + BiLSTM + Dot Attention |
| TransformerEncoder | Encoder Transformer |
| CNN_TransformerEncoder | CNN + Transformer Encoder |

## 📦 Word Embeddings

| # | Phương pháp | Retrain |
|---|-------------|---------|
| 1 | Random Embedding | ✅ Full train |
| 2 | Word2Vec (tự train) | ✅ Full train |
| 3 | FastText Pretrained | ❌ Freeze |
| 4 | FastText Fine-tune | ✅ Fine-tune |

## 📋 Nguồn dữ liệu

| App | CH Play |
|-----|---------|
| Shopee | https://play.google.com/store/apps/details?id=com.shopee.vn |
| Tiki | https://play.google.com/store/apps/details?id=vn.tiki.app.tikiandroid |
| Lazada | https://play.google.com/store/apps/details?id=com.lazada.android |
| Sendo | https://play.google.com/store/apps/details?id=com.sendo |

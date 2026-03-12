# 📖 HƯỚNG DẪN DÁN NHÃN CẢM XÚC

## Thông tin chung
- **Mục tiêu:** Dán nhãn cảm xúc cho review ứng dụng mua sắm tiếng Việt
- **File làm việc:** `data/annotation_todo.csv`
- **Công cụ:** Excel hoặc Google Sheets

## Quy tắc chung
- Đọc KỸ nội dung cột `review` — **KHÔNG phụ thuộc vào cột `rating`**
- Chỉ điền đúng 1 trong 3 giá trị vào cột `label`:
  - `positive`
  - `negative`
  - `neutral`
- Nếu khó phân loại → ghi vào cột `note` để thảo luận
- Nếu không phải tiếng Việt / spam / vô nghĩa → ghi `skip` vào cột `note`

---

## ✅ POSITIVE — Tích cực
> Review thể hiện sự hài lòng, khen ngợi, trải nghiệm tốt

| Review | Label |
|--------|-------|
| "App rất mượt, giao hàng siêu nhanh, mình rất thích" | positive |
| "Chất lượng tốt, đóng gói cẩn thận, sẽ ủng hộ tiếp" | positive |
| "Tuyệt vời, dùng mấy năm chưa gặp vấn đề gì" | positive |
| "ship nhanh 👍, hàng đúng mô tả, thích lắm 😍" | positive |

---

## ❌ NEGATIVE — Tiêu cực
> Review thể hiện sự không hài lòng, phàn nàn, trải nghiệm tệ

| Review | Label |
|--------|-------|
| "App cứ bị crash, không dùng được, rất bực" | negative |
| "Hàng giả, không đúng mô tả, thất vọng hoàn toàn" | negative |
| "Giao hàng chậm, liên hệ CSKH không ai trả lời" | negative |
| "mất tiền oan, lừa đảo 🤬👎" | negative |

---

## 😐 NEUTRAL — Trung lập
> Review nhận xét khách quan, nửa khen nửa chê, không rõ cảm xúc

| Review | Label |
|--------|-------|
| "App ổn, dùng được nhưng còn nhiều lỗi nhỏ" | neutral |
| "Bình thường, không có gì đặc biệt" | neutral |
| "Tốt nhưng giao hàng hơi chậm so với trước" | neutral |
| "ok v, bt thôi" | neutral |

---

## ⚠️ CÁC TRƯỜNG HỢP KHÓ

### 1. Phủ định đảo nghĩa
| Review | Label | Giải thích |
|--------|-------|------------|
| "Không tệ, dùng ổn" | positive | "không tệ" = tích cực |
| "Không tốt lắm" | negative | "không tốt" = tiêu cực |
| "Cũng không đến nỗi" | neutral | Mơ hồ |

### 2. Review 2 chiều (khen + chê)
> → Nhìn vào **cảm xúc chủ đạo**, phần nào được nhấn mạnh hơn

| Review | Label | Giải thích |
|--------|-------|------------|
| "App đẹp nhưng **hàng giả, mất tiền oan**" | negative | Vế tiêu cực mạnh hơn |
| "Có vài lỗi nhỏ nhưng **nhìn chung rất tốt**" | positive | Vế tích cực mạnh hơn |
| "Tốt có, xấu có, tùy người dùng" | neutral | Không rõ chiều |

### 3. Teencode & Emoji
| Review | Label |
|--------|-------|
| "Tuyệt vời 🔥❤️" | positive |
| "Rác 🤮👎" | negative |
| "ok v, ko có j dc khen" | neutral |
| "thik lém, mn dùng thử đi nha 😍" | positive |

---

---

## 🆕 TỪ VIẾT TẮT CHƯA CÓ TRONG TỪ ĐIỂN

> Nếu gặp từ viết tắt lạ mà bạn hiểu nghĩa, **đọc theo nghĩa đó để gán nhãn** — KHÔNG sửa nội dung review.
> Ghi từ đó và nghĩa vào cột `note` để bổ sung sau.

**Quy trình:**
1. Gán nhãn theo nghĩa bạn hiểu.
2. Ghi vào cột `note`: ví dụ `từ lạ: "đhvn" = đơn hàng về nhà`.
3. Sau annotation, bổ sung thủ công vào `src/teencode_dict.py`.

---

## 🤬 TỪ CHỬI THỀ & TỪ NHẤN MẠNH

### Nhóm 1 — Chửi thề trực tiếp → luôn là tín hiệu **NEGATIVE**
> Review chứa những từ này gần như luôn thể hiện sự tức giận, phẫn nộ mạnh.

| Từ gốc | Dạng viết tắt | Quy về label |
|--------|--------------|---------------|
| đ\*\* mẹ | dm, đm, dmm, đmm, đcm | **negative** |
| v\*\* | vkl, cc, cặc | **negative** |

**Ví dụ:**
| Review | Label |
|--------|-------|
| "dm cái app này tệ vl, mất tiền oan" | **negative** |
| "đmm giao hàng cả tháng vẫn chưa tới" | **negative** |

### Nhóm 2 — Từ nhấn mạnh cường điệu (vl, vcl, vch) → theo từ được bổ nghĩa
> Những từ này chỉ là cách nói cường điệu, bản thân chúng không quyết định sentiment.

| Review | Label | Giải thích |
|--------|-------|------------|
| "xịn vl, giao nhanh vl" | **positive** | vl bổ nghĩa cho tích cực |
| "lag vl, chậm vl" | **negative** | vl bổ nghĩa cho tiêu cực |
| "bt thôi, cũng vl" | **neutral** | không rõ |

---

## 🚫 LOẠI BỎ — Ghi "skip" vào cột note
- Không phải tiếng Việt
- Chỉ có emoji, không có chữ
- Nội dung không liên quan đến app
- Spam / quảng cáo
- Review chỉ có 1-2 từ không rõ nghĩa

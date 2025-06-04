# Hướng Dẫn
---

## 🗂️ Cấu trúc thư mục

```plaintext
├── app_test.py                  # File chính chạy giao diện chatbot Streamlit
├── QA_Chain.py             # Class xử lý tạo vector DB và hỏi đáp
├── prepare_vector_db.py       # Tạo FAISS vector DB từ tài liệu PDF hoặc văn bản
├── save_history.py         # Hàm lưu lịch sử hội thoại
├── embedding_model.py         # Dùng để Embedding text
└── config.py               # Cấu hình mô hình

## RUN APP

'''sh
streamlit run models/app_test
'''
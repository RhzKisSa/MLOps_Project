# React Chatbot Q&A PDF

Ứng dụng React Vite giao tiếp với backend FastAPI để hỏi đáp tài liệu PDF.

## Tính năng
- Upload file PDF lên backend
- Nhập câu hỏi, nhận câu trả lời từ tài liệu
- Hiển thị lịch sử chat
- Giao diện hiện đại, hỗ trợ tiếng Việt

## Khởi động
```bash
npm install
npm run dev
```

## Kết nối backend
- Mặc định API backend là `http://localhost:8081` (sửa trong `src/App.jsx` nếu cần)
- Backend cần chạy trước với các endpoint `/upload_pdf/` và `/ask/`

## Tuỳ chỉnh
- Sửa giao diện trong `src/App.jsx` và `src/App.css`

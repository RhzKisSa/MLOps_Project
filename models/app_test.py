import streamlit as st
import uuid
import os
import tempfile
from QA_Chain import QAChain
from save_history import *
from config import *

# Giao diện
st.set_page_config(page_title="Chatbot Q&A", layout="centered")

# Tiêu đề chính
st.title("🤖 Chatbot Q&A")

# Tạo session ID và khởi tạo QAChain
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "qa" not in st.session_state:
    st.session_state.qa = None
if "history" not in st.session_state:
    st.session_state.history = []

# Upload PDF
uploaded_files = st.file_uploader("📄 Tải lên file PDF:", type="pdf", accept_multiple_files=True)

# Chỉ xử lý nếu có file upload và QA chưa được tạo
def create_qa_chain(uploaded_files):
    # Lấy tên file hiện tại
    current_file_names = sorted([file.name for file in uploaded_files])

    # Kiểm tra nếu chưa có hoặc file khác với lần trước
    if (
        "last_uploaded_files" not in st.session_state
        or st.session_state.last_uploaded_files != current_file_names
    ):
        with st.spinner("🔄 Đang xử lý và tạo vector DB..."):
            with tempfile.TemporaryDirectory() as tmpdirname:
                for pdf_file in uploaded_files:
                    pdf_path = os.path.join(tmpdirname, pdf_file.name)
                    with open(pdf_path, "wb") as f:
                        f.write(pdf_file.getbuffer())

                # Tạo lại QAChain
                qa = QAChain(llm=llm)
                qa.create_chain(tmpdirname)
                st.session_state.qa = qa
                st.session_state.history = []
                st.session_state.last_uploaded_files = current_file_names  # Lưu tên file
                st.success("✅ Tạo vector DB thành công!")
                return qa
    else:
        st.info("⚠️ Bạn đã tải lên cùng những file trước đó — vector DB không cần tạo lại.")

if uploaded_files :
    st.session_state.qa = create_qa_chain(uploaded_files)

# Load vector DB mặc định nếu chưa có
if st.session_state.qa is None:
    qa = QAChain(llm=llm)
    qa.load_vector_db()
    st.session_state.qa = qa

# Giao diện hội thoại
st.divider()
st.header("💬 Hỏi đáp với tài liệu của bạn")

# Hiển thị lịch sử hội thoại kiểu chat
for msg in st.session_state.history:
    with st.chat_message("user"):
        st.markdown(msg["question"])
    with st.chat_message("assistant"):
        st.markdown(msg["answer"])

# Chat input
question = st.chat_input("Nhập câu hỏi tại đây...")  # hoặc st.text_input(...)
if question:
    if question.lower().strip() in ["exit", "bye"]:
        st.success("👋 Tạm biệt! Đang làm mới phiên làm việc...")

        # Xoá toàn bộ session_state để làm mới
        for key in list(st.session_state.keys()):
            del st.session_state[key]

    else:
        with st.chat_message("user"):
            st.markdown(question)

        with st.spinner("🤔 Đang tìm câu trả lời..."):
            answer = st.session_state.qa.query(question)

        with st.chat_message("assistant"):
            st.markdown(answer)

        # Lưu lịch sử
        if "history" not in st.session_state:
            st.session_state.history = []
        st.session_state.history.append({
            "question": question,
            "answer": answer
        })
        save_history(st.session_state.session_id, st.session_state.history)

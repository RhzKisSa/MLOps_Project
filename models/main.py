from QA_Chain import QAChain
from config import llm  # Import LLM từ config
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import shutil
import os
from save_history import save_history, load_history, delete_history
import logging
import sys
import io
from logging.handlers import RotatingFileHandler
from prometheus_fastapi_instrumentator import Instrumentator

# Cấu hình logging
LOG_DIR = "/app/logs"  # Sử dụng đường dẫn tuyệt đối trong container
os.makedirs(LOG_DIR, exist_ok=True)
os.chmod(LOG_DIR, 0o777)

# Xóa các handler cũ
logger = logging.getLogger()
for h in list(logger.handlers):
    logger.removeHandler(h)
logger.setLevel(logging.DEBUG)

fmt = logging.Formatter('ts="%(asctime)s" level="%(levelname)s" name="%(name)s" msg="%(message)s"')

# 1. fastapi_app.log: log ứng dụng (DEBUG+)
app_file = os.path.join(LOG_DIR, "fastapi_app.log")
app_handler = RotatingFileHandler(app_file, maxBytes=10*1024*1024, backupCount=5, mode='a')
app_handler.setLevel(logging.DEBUG)
app_handler.setFormatter(fmt)
logger.addHandler(app_handler)

# 2. syslog.log: log hệ thống (INFO+)
syslog_file = os.path.join(LOG_DIR, "syslog.log")
syslog_handler = RotatingFileHandler(syslog_file, maxBytes=5*1024*1024, backupCount=3, mode='a')
syslog_handler.setLevel(logging.INFO)
syslog_handler.setFormatter(fmt)
logger.addHandler(syslog_handler)

# 3. stdout.log: chỉ log ra stdout (INFO+)
stdout_file = os.path.join(LOG_DIR, "stdout.log")
stdout_handler = RotatingFileHandler(stdout_file, maxBytes=5*1024*1024, backupCount=3, mode='a')
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(fmt)
stdout_handler.stream = sys.stdout
logger.addHandler(stdout_handler)

# 4. stderr.log: chỉ log ra stderr (ERROR+)
stderr_file = os.path.join(LOG_DIR, "stderr.log")
stderr_handler = RotatingFileHandler(stderr_file, maxBytes=5*1024*1024, backupCount=3, mode='a')
stderr_handler.setLevel(logging.ERROR)
stderr_handler.setFormatter(fmt)
stderr_handler.stream = sys.stderr
logger.addHandler(stderr_handler)

# Đảm bảo file log có quyền ghi
for f in [app_file, syslog_file, stdout_file, stderr_file]:
    try:
        os.chmod(f, 0o666)
    except Exception as e:
        print(f"Error setting log file permissions: {e}")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Instrumentator().instrument(app).expose(app)  # expose /metrics

# Khởi tạo global QAChain
qa_chain = QAChain(llm=llm)
active_db_loaded = False  # Cờ để kiểm tra đã upload PDF hay chưa

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    global active_db_loaded

    # Tạo thư mục tạm và lưu file
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmp_pdf_path = os.path.join(tmpdirname, file.filename)

        with open(tmp_pdf_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        try:
            qa_chain.create_chain(tmpdirname)
            active_db_loaded = True
            return {"message": f"Đã xử lý PDF: {file.filename}"}
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/ask/")
async def ask_question(question: str = Form(...)):
    if not active_db_loaded:
        return JSONResponse(status_code=400, content={"error": "Chưa upload file PDF nào."})

    try:
        answer = qa_chain.query(question)
        return {"question": question, "answer": answer}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/save_history/")
async def save_chat_history(request: Request):
    data = await request.json()
    session_id = data.get("session_id")
    history = data.get("history", [])
    session_name = data.get("session_name")
    if not session_id:
        return JSONResponse(status_code=400, content={"error": "Thiếu session_id"})
    try:
        save_history(session_id, history, session_name)
        return {"message": "Lưu lịch sử thành công"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    try:
        history = load_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.delete("/history/{session_id}")
async def delete_chat_history(session_id: str):
    try:
        deleted = delete_history(session_id)
        if deleted:
            return {"message": f"Đã xoá lịch sử chat với session_id: {session_id}"}
        else:
            return JSONResponse(status_code=404, content={"error": "Không tìm thấy session_id"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/list_sessions/")
def list_sessions():
    try:
        session_dir = os.path.join("./data", "chat_sessions")
        files = os.listdir(session_dir)
        # Sắp xếp theo thời gian sửa đổi, mới nhất lên đầu
        files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(session_dir, f)), reverse=True)
        sessions = []
        for f in files:
            if f.endswith('.json'):
                sid = f.replace('.json','')
                # Đọc tên đoạn chat nếu có
                try:
                    with open(os.path.join(session_dir, f), encoding='utf-8') as file:
                        data = file.read()
                        import json
                        obj = json.loads(data)
                        name = obj.get('session_name', sid)
                except Exception:
                    name = sid
                sessions.append({'id': sid, 'name': name})
        return {"sessions": sessions}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


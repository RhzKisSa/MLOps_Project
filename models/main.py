from QA_Chain import QAChain
from config import llm  # Import LLM từ config
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import shutil
import os
from save_history import save_history, load_history

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# run main 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)
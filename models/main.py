from QA_Chain import QAChain
from config import llm  # Import LLM từ config
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import tempfile
import shutil
import os

app = FastAPI()

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

# run main 
if __name__ == "__main__":
    app.run(port = 8081)
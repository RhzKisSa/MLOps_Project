from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import FAISS
from config import *
import os

class VectorDBCreator:
    def __init__(self, vector_db_path='./data/vector_db_path'):
        self.vector_db_path = vector_db_path
        self.embedding_model = embeddings

    def create_db_from_text(self, raw_text: str):
        # Chia nhỏ text
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=512,
            chunk_overlap=50,
            length_function=len
        )
        chunks = text_splitter.split_text(raw_text)

        # Tạo FAISS vectorstore
        db = FAISS.from_texts(texts=chunks, embedding=self.embedding_model)

        # Lưu vectorstore
        os.makedirs(self.vector_db_path, exist_ok=True)
        db.save_local(self.vector_db_path)

        return db

    def create_db_from_pdfs(self, pdf_dir_path: str):
        # Loader quét toàn bộ file pdf trong thư mục
        loader = DirectoryLoader(pdf_dir_path, glob="*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load()

        # Chia nhỏ tài liệu
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)

        # Tạo FAISS vectorstore
        db = FAISS.from_documents(chunks, embedding=self.embedding_model)

        # Lưu vectorstore
        os.makedirs(self.vector_db_path, exist_ok=True)
        db.save_local(self.vector_db_path)

        return db

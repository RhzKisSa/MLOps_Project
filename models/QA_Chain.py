from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from embedding_model import *
from config import *
from prepare_vector_db import *

class QAChain:
    def __init__(self, llm, vector_db_path='./data/vector_db_path', k=3, max_tokens_limit=1024):
        os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
        self.vector_db_path = vector_db_path
        self.embedding_model = PhoBERTEmbeddings()
        self.llm = llm
        self.k = k
        self.max_tokens_limit = max_tokens_limit
        self.db = None
        self.chain = None
        self.prompt = None
        self.vector_creator = VectorDBCreator(vector_db_path=self.vector_db_path)

    def create_prompt(self, template=None):
        if template is None:
            template = """<|im_start|>system Sử dụng thông tin sau đây để trả lời câu hỏi. Nếu bạn không biết câu trả lời, hãy nói không biết, đừng cố tạo ra câu trả lời{context}
                    <|im_end|><|im_start|>user{question}<|im_end|><|im_start|>assistant"""
        self.prompt = PromptTemplate(template=template, input_variables=["context", "question"])
        return self.prompt

    def create_chain(self, pdf_dir_path: str):
        print(f"Tạo vector DB từ thư mục PDF: {pdf_dir_path} ...")
        self.db = self.vector_creator.create_db_from_pdfs(pdf_dir_path)
        print("Đã tạo vector DB từ PDF và lưu tại:", self.vector_db_path)
        if self.db is None:
            raise ValueError("Vector DB chưa được tạo hoặc load. Vui lòng gọi create_db_from_text/pdf hoặc load_vector_db trước.")
        if self.llm is None:
            raise ValueError("Bạn chưa truyền LLM khi khởi tạo class.")
        if self.prompt is None:
            self.create_prompt()
        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.db.as_retriever(search_kwargs={"k": self.k}, max_tokens_limit=self.max_tokens_limit),
            return_source_documents=False,
            chain_type_kwargs={'prompt': self.prompt}
        )
        return self.chain
       
    def load_vector_db(self):
        print("Đang load vector DB từ:", self.vector_db_path)
        self.db = FAISS.load_local(self.vector_db_path, self.embedding_model, allow_dangerous_deserialization=True)
        print("Load vector DB thành công")
        if self.db is None:
            raise ValueError("Vector DB chưa được tạo hoặc load. Vui lòng gọi create_db_from_text/pdf hoặc load_vector_db trước.")
        if self.llm is None:
            raise ValueError("Bạn chưa truyền LLM khi khởi tạo class.")
        if self.prompt is None:
            self.create_prompt()
        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.db.as_retriever(search_kwargs={"k": self.k}, max_tokens_limit=self.max_tokens_limit),
            return_source_documents=False,
            chain_type_kwargs={'prompt': self.prompt}
        )
        return self.chain

    def query(self, question: str):
        if self.chain is None:
            raise ValueError("Chain chưa được tạo. Vui lòng gọi create_chain() hoặc tạo/load DB trước.")
        return self.chain.invoke({"query": question})
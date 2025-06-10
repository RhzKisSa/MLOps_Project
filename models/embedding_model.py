import torch
from langchain.embeddings.base import Embeddings
from transformers import AutoTokenizer, AutoModel


class PhoBERTEmbeddings(Embeddings):
    def __init__(self, model_name="vinai/phobert-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
    
    def embed_documents(self, texts):
        """Nhận list văn bản, trả về list embedding dạng list float"""
        return [self._embed(text) for text in texts]
    
    def embed_query(self, text):
        """Nhận 1 câu truy vấn, trả về embedding dạng list float"""
        return self._embed(text)
    
    def _embed(self, text):
        """Hàm lấy embedding mean pooling"""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
        last_hidden_state = outputs.last_hidden_state  # shape: (1, seq_len, hidden_size)
        embedding = torch.mean(last_hidden_state, dim=1).squeeze()  # mean pooling
        return embedding.cpu().numpy().tolist()

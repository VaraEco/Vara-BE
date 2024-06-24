from langchain_huggingface import HuggingFaceEmbeddings

class EmbeddingService:
    def get_embedding():
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        return embeddings
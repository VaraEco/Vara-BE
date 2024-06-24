from langchain_pinecone import PineconeVectorStore
from services.embedding_service import EmbeddingService
import logging

class Vectorstore:
    logger = logging.getLogger('vara-backend')

    @staticmethod
    def get_vectorstore(index_name):
        embeddings = EmbeddingService.get_embedding()
        Vectorstore.logger.info(f'Collection accessed: {index_name}')
        vector_store = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embeddings)
        return vector_store
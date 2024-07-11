from langchain_community.embeddings import BedrockEmbeddings
import boto3


class EmbeddingService:
    def get_embedding():
        bedrock_client = boto3.client(service_name='bedrock-runtime', 
                              region_name='us-east-1')
        embeddings = BedrockEmbeddings(
            model_id="cohere.embed-english-v3",
                                       client=bedrock_client
        )
        return embeddings
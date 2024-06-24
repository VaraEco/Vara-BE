import os

class Config:
    MODEL_ID = os.getenv('MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')

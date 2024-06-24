import threading
import logging
from langchain_aws import BedrockLLM
from langchain_aws import ChatBedrock
from flask import current_app


class Model:
    model = None
    logger = logging.getLogger('vara-backend')
    lock = threading.Lock()

    @classmethod
    def get_model(cls):
        model_id = current_app.config['MODEL_ID']
        if cls.model is None:
            with cls.lock:
                cls.model = ChatBedrock(model_id=model_id)
        cls.logger.info(f'Model being used: {model_id}')
        return cls.model
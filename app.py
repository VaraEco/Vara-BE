# app.py
from flask import Flask, request, jsonify
from config import Config
from logging_config import Logging
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
logger = Logging.set_logging()
logger.info(f'Initial Config MODEL_ID: {app.config["MODEL_ID"]}')

from api.routes.chatbot import chatbot_bp
from api.routes.document_analyzer import document_analyzer_bp
from api.routes.document_upload import document_upload_bp
app.register_blueprint(chatbot_bp, url_prefix='/api')
app.register_blueprint(document_analyzer_bp, url_prefix='/api')
app.register_blueprint(document_upload_bp, url_prefix='/api')

@app.route('/')
def compute():
    return jsonify({'result': "Success"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)

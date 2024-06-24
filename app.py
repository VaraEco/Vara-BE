# app.py
from flask import Flask, request, jsonify
from config import Config
from logging_config import Logging

app = Flask(__name__)
app.config.from_object(Config)
logger = Logging.set_logging()
logger.info(f'Initial Config MODEL_ID: {app.config["MODEL_ID"]}')

from api.routes.chatbot import chatbot_bp
app.register_blueprint(chatbot_bp, url_prefix='/api')

@app.route('/compute', methods=['GET '])
def compute():
    data = request.get_json()
    query = data.get('query', '')

   
    result = perform_computation(query)

    return jsonify({'result': result})

def perform_computation(query):
    
    return query[::-1].upper()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)

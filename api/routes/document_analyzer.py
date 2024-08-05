from flask import Blueprint, request, jsonify
from flask_cors import CORS
import logging
from services.textract_services import Textract

document_analyzer_bp = Blueprint('document_analyzer', __name__)
CORS(document_analyzer_bp, resources={r"/document/analyze":{"origins":"*"}}, methods=['POST'])

logger = logging.getLogger('vara-backend')

@document_analyzer_bp.route('/document/analyze', methods=['POST'])
def get_document_analysis():
    data = request.get_json()
    s3_bucket_name = data['bucketName']
    document_name = data['documentName']
    textract = Textract()
    response = textract.get_analysis(s3_bucket_name, document_name)
    return jsonify(response)

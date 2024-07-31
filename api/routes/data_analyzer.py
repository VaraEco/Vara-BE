from flask import Blueprint, request, jsonify
import logging

data_analyzer_bp = Blueprint('data_analyzer', __name__)
logger = logging.getLogger('vara-backend')

@data_analyzer_bp.route('/data/analyze', methods=['POST'])
def get_data_analysis():
    data = request.get_json()
    supabase_bucket_name = data['bucketName']
    document_name = data['documentName']
    return jsonify({'bucketName':supabase_bucket_name, 'documentName':document_name})
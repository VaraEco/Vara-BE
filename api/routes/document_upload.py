from flask import Blueprint, request, jsonify
from flask_cors import CORS
import logging
import boto3
from botocore.exceptions import ClientError
import json
from io import BytesIO

document_upload_bp = Blueprint('document_upload', __name__)
CORS(document_upload_bp, resources={r"/upload/document/analysis":{"origins":"*"}}, methods=['POST'])
logger = logging.getLogger('vara-backend')

@document_upload_bp.route('/upload/document/analysis', methods=['POST'])
def upload_document():
    bucket_name = "compliance-document-bucket"
    data = None
    if request.content_type == 'application/octet-stream':
        byte_array = request.data
        try:
            byte_string = byte_array.decode('utf-8')
            data = json.loads(byte_string)
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
                return jsonify({'error': str(e)}), 400
    else:
        data = request.get_json()
    file_name = data['fileName']
    file = data['file']
    temp_file = BytesIO()
    temp_file.write(file.encode('utf-8'))
    temp_file.seek(0)
    s3_client = boto3.client('s3')
    response = True
    try:
        response = s3_client.upload_file(temp_file, bucket_name, file_name)
    except ClientError as e:
         logger.error(e)
    return jsonify({'upload':response})

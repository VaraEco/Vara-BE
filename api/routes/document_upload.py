from flask import Blueprint, request, jsonify
from flask_cors import CORS
import logging
import boto3
from botocore.exceptions import ClientError
import json
from services.textract_services import Textract
from utils.general_utils import GeneralUtils

document_upload_bp = Blueprint('document_upload', __name__)
CORS(document_upload_bp, resources={r"/upload/document/analysis":{"origins":"*"}, r"/upload/document/data/analysis":{"origins":"*"}}, methods=['POST'])
logger = logging.getLogger('vara-backend')

@document_upload_bp.route('/upload/document/analysis', methods=['POST'])
def upload_document():
    bucket_name = "compliance-document-bucket"

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files.get('file', '')

    fileName = str(request.form.get('fileName', ''))
    print(fileName)

    # Upload the file to S3
    s3_client = boto3.client('s3')
    response = True
    try:
        s3_client.upload_fileobj(file, bucket_name, fileName)
    except ClientError as e:
        logger.error(e)

    # Add code for getting value from TextRact
    textract = Textract()
    response = textract.get_analysis(bucket_name, fileName)
    print(response)

    return jsonify(response)

@document_upload_bp.route('/upload/document/data/analysis', methods=['POST'])
def upload_document_analysis():
    bucket_name = "compliance-document-bucket"

    if 'filepond' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files.get('filepond', '')

    file_name = file.filename
    chat_id = GeneralUtils.get_uuid(file_name)
    file_name = chat_id+'.csv'
    

    # Upload the file to S3
    s3_client = boto3.client('s3')
    response = True
    try:
        response = s3_client.upload_fileobj(file, bucket_name, file_name)
    except ClientError as e:
        response = False
        logger.error(e)

    # Add code for getting value from TextRact
    #textract = Textract()
    #response = textract.get_analysis(bucket_name, fileName)
    #print(response)

    return jsonify(response)

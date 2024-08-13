from flask import Blueprint, request, jsonify
import logging
from services.textract_services import Textract
from services.summary_services import DocumentSummarizer

document_summarizer_bp = Blueprint('document_summarizer', __name__)
logger = logging.getLogger('vara-backend')

@document_summarizer_bp.route('/document/summarize', methods=['POST'])
def summarize_document():
    data = request.get_json()
    s3_bucket_name = data['bucketName']
    document_name = data['documentName']
    textract = Textract()
    
    # Extract text from the document
    document_text = textract.get_analysis(s3_bucket_name, document_name)
    
    # Summarize the extracted text
    summarizer = DocumentSummarizer()
    summary = summarizer.summarize(document_text)
    
    return jsonify({'summary': summary})

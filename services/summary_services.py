from flask import Blueprint, request, jsonify
import logging
import PyPDF2
import requests
import os

document_summarizer_bp = Blueprint('document_summarizer', __name__)
logger = logging.getLogger('vara-backend')

# Set up OpenAI API key as an environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
API_URL = "https://api.openai.com/v1/chat/completions"

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return None

# Function to summarize text using OpenAI
def summarize_text(text):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "Summarize the following text."},
            {"role": "user", "content": text}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }

    response = requests.post(API_URL, json=data, headers=headers)

    if response.status_code == 200:
        summary = response.json().get('choices')[0].get('message').get('content')
        return summary
    else:
        logger.error(f"Failed to summarize text: {response.status_code}, {response.text}")
        return None

@document_summarizer_bp.route('/document/summarize', methods=['POST'])
def summarize_document():
    data = request.get_json()
    s3_bucket_name = data['bucketName']
    document_name = data['documentName']
    pdf_path = f"/path/to/s3/{s3_bucket_name}/{document_name}"  # Modify this to match your S3 file path setup

    # Extract text from the document
    document_text = extract_text_from_pdf(pdf_path)

    if not document_text:
        return jsonify({'error': 'Failed to extract text from PDF'}), 500

    # Summarize the extracted text
    summary = summarize_text(document_text)

    if not summary:
        return jsonify({'error': 'Failed to summarize the document'}), 500

    return jsonify({'summary': summary})

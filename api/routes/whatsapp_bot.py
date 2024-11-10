from flask import Blueprint, request, jsonify
from services.whatsapp_bot_service import setup_whatsapp_service, process_whatsapp_message, send_whatsapp_message
import logging
import re

# Initialize Flask Blueprint
whatsapp_bot_bp = Blueprint('whatsapp_bot', __name__)

# Logging configuration
log_handler = logging.FileHandler('whatsapp_bot.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
log_handler.setFormatter(formatter)
logging.getLogger().addHandler(log_handler)
logging.getLogger().setLevel(logging.INFO)

# Dictionary to hold user sessions data
user_sessions = {}

# Function to reset a specific user session
def reset_user_session(phone_number):
    if phone_number in user_sessions:
        del user_sessions[phone_number]
    logging.info(f"User session reset for {phone_number}")

# API route to start WhatsApp interaction when a user provides their phone number
@whatsapp_bot_bp.route('/setup_whatsapp', methods=['POST'])
def setup_whatsapp():
    try:
        data = request.json
        user_phone = data.get('phone_number')
        process_id = data.get('process_id')
        para_id = data.get('para_id')
        data_collection_id = data.get('data_collection_id')

        # Validate inputs
        if not user_phone:
            logging.error("Phone number not provided")
            return jsonify({'status': 'error', 'message': 'Phone number is required'}), 400
        
        # Store phone number in session with a proper format
        user_phone_formatted = f'+{user_phone}'
        user_sessions[user_phone_formatted] = {
            'phone_number': user_phone_formatted,
            'status': 'waiting_for_join_code',
            'process_id': process_id,
            'para_id': para_id,
            'data_collection_id': data_collection_id
        }

        # Set up WhatsApp service
        response = setup_whatsapp_service(user_phone_formatted, process_id, para_id, data_collection_id)
        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Error in setup_whatsapp: {str(e)}")
        return jsonify({'status': 'error', 'message': 'An error occurred while setting up WhatsApp.'}), 500


@whatsapp_bot_bp.route('/webhooks', methods=['POST'])
def webhooks():
    try:
        incoming_msg = request.form.get('Body').strip().lower()
        from_number = request.form.get('From')
        
        logging.info(f"Received message from {from_number}: {incoming_msg}")

        # Extract phone number from 'whatsapp:' format
        match = re.match(r"whatsapp:(\+?\d+)", from_number)
        if match:
            from_number_cleaned = match.group(1)
            logging.info(f"Cleaned phone number: {from_number_cleaned}")
        else:
            logging.error("Invalid phone number format")
            return jsonify({'status': 'error', 'message': 'Invalid phone number format'}), 400

        # Check if the phone number is authorized
        if from_number_cleaned not in user_sessions or user_sessions[from_number_cleaned]['phone_number'] != from_number_cleaned:
            logging.info(f"Unauthorized message from {from_number_cleaned}. Ignoring.")
            send_whatsapp_message(from_number_cleaned, "This number is unauthorized to interact with this bot.")
            return jsonify({'status': 'error', 'message': 'This number is not authorized to interact with the bot.'}), 400


        
        # Process the message
        response = process_whatsapp_message(from_number_cleaned, incoming_msg)
        
        # If data collection is complete, reset user session
        if response.get('status') == 'complete':
            reset_user_session(from_number_cleaned)

        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Error in webhooks: {str(e)}")
        return jsonify({'status': 'error', 'message': 'An error occurred while processing the message.'}), 500

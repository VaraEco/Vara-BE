from flask import Blueprint, request, jsonify
from services.whatsapp_bot_service import setup_whatsapp_service, process_whatsapp_message
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

# API route to start WhatsApp interaction when a user provides their phone number
@whatsapp_bot_bp.route('/setup_whatsapp', methods=['POST'])
def setup_whatsapp():
    try:
        data = request.json
        user_phone = data.get('phone_number')
        process_id = data.get('process_id')
        para_id = data.get('para_id')
        data_collection_id = data.get('data_collection_id')

        if not user_phone:
            logging.error("Phone number not provided")
            return jsonify({'status': 'error', 'message': 'Phone number is required'}), 400

        # Store the phone number in the session
        user_sessions[user_phone] = {
            'phone_number': f'+{user_phone}',
            'status': 'waiting_for_join_code',
            'process_id': process_id,
            'para_id': para_id,
            'data_collection_id': data_collection_id
        }
        # Set up WhatsApp service
        response = setup_whatsapp_service(user_phone, process_id, para_id, data_collection_id)
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

        # Extract phone number from 'whatsapp:' format (if present)
        match = re.match(r"whatsapp:(\+?\d+)", from_number)
        if match:
            from_number_cleaned = match.group(1)  # Extracted phone number without 'whatsapp:'
            logging.info(f"Cleaned phone number: {from_number_cleaned}")
        else:
            logging.error("Invalid phone number format")
            return jsonify({'status': 'error', 'message': 'Invalid phone number format'}), 400
        # Check if the cleaned incoming phone number matches the stored phone number in user_sessions
        if from_number_cleaned not in user_sessions or user_sessions[from_number_cleaned]['phone_number'] != from_number_cleaned:
            logging.info(f"Unauthorized message from {from_number_cleaned}. Ignoring.")
            return jsonify({'status': 'error', 'message': 'This number is not authorized to interact with the bot.'}), 400

        # Pass the message and phone number to service for processing
        response = process_whatsapp_message(from_number_cleaned, incoming_msg)
        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Error in webhooks: {str(e)}")
        return jsonify({'status': 'error', 'message': 'An error occurred while processing the message.'}), 500

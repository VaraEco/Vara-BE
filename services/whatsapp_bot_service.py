from datetime import datetime
import re
from supabase import create_client, Client
from twilio_config import client, TWILIO_WHATSAPP_NUM
import logging
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Load environment variables
load_dotenv()

# Constants for message intervals
COLLECT_DATA_INTERVAL_HOURS = 24  # 24 hours

# Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
join_code = os.getenv('WHATSAPP_JOIN_CODE')

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# A dictionary to hold temporary user sessions for WhatsApp interaction
user_sessions = {}

# Schema for the fields we expect from users (order matters)
schema_fields = ['value', 'log_unit', 'log_date', 'evidence_url', 'evidence_name']

# Initialize APScheduler
scheduler = BackgroundScheduler()
scheduler.start()

def reset_user_session(phone_number):
    if phone_number not in user_sessions:
        user_sessions[phone_number] = {}

    persistent_data = user_sessions[phone_number].get('persistent_data', {})

    user_sessions[phone_number] = {
        'field_index': 0,
        'data': {},
        'status': 'waiting_for_join_code',
        'persistent_data': persistent_data  # Retain process_id, para_id, data_collection_id
    }

    logging.info(f"User session reset for {phone_number}. IDs retained: {bool(persistent_data)}")


print(user_sessions)


def send_whatsapp_message(to_number, message):
    client.messages.create(
        body=message,
        from_=TWILIO_WHATSAPP_NUM,
        to=f'whatsapp:{to_number}'
    )

# Check if the user is joined (static logic)
def is_user_joined(phone_number):
    # This should be replaced with actual logic for checking user status
    return True  # Set to True if the user is joined, False otherwise

def setup_whatsapp_service(user_phone, process_id, para_id, data_collection_id):
    # Check if there's an existing user session with the same IDs
    for phone_number, session in user_sessions.items():
        persistent_data = session.get('persistent_data', {})
        if (persistent_data.get('process_id') == process_id and
            persistent_data.get('para_id') == para_id and
            persistent_data.get('data_collection_id') == data_collection_id):
            # If we find a matching session, send a message to the old user
            # Notify old user that they are no longer able to submit data
            client.messages.create(
                body=f"Your session for process {process_id} has been taken over by a new user. You are no longer able to submit data.",
                from_=TWILIO_WHATSAPP_NUM,
                to=f"whatsapp:{phone_number}"
            )
            # Set the old user status to "inactive" before deleting the session
            user_sessions[phone_number]['status'] = 'inactive'
            logging.info(f"Old session marked as inactive for {phone_number} with process_id: {process_id}, para_id: {para_id}, data_collection_id: {data_collection_id}")
            break  # Exit after deleting the first match

    # Now, setup the new user session
    user_sessions[user_phone] = {
        'field_index': 0,
        'data': {},
        'status': 'waiting_for_join_code',
        'persistent_data': {
            'process_id': process_id,
            'para_id': para_id,
            'data_collection_id': data_collection_id
        }
    }

    try:
        if is_user_joined(user_phone):
            client.messages.create(
                body="Welcome! Let's start by collecting some information. Please say hello.",
                from_=TWILIO_WHATSAPP_NUM,
                to=f"whatsapp:{user_phone}"
            )
            return {'status': 'success', 'message': f"Join code sent to {TWILIO_WHATSAPP_NUM} with {join_code}. Please follow the instructions to join WhatsApp bot, and say Hello!"}
        else:
            client.messages.create(
                body=f"Please send the message '{join_code}' to join the sandbox.",
                from_=TWILIO_WHATSAPP_NUM,
                to=f"whatsapp:{user_phone}"
            )
            reset_user_session(user_phone)
            return {'status': 'success', 'message': f"Join code sent. Please follow the instructions to join WhatsApp bot and say Hello!"}

    except Exception as e:
        logging.error(f"Error setting up WhatsApp service for {user_phone}: {e}")
        return {'status': 'error', 'message': 'Failed to send join instructions.'}



def process_whatsapp_message(from_number, incoming_msg):
    try:
        if from_number not in user_sessions:
            reset_user_session(from_number)

        user_session = user_sessions[from_number]

        # If user session is inactive, ignore their messages
        if user_session['status'] == 'inactive':
            logging.info(f"Ignoring message from inactive user {from_number}.")
            return {'status': 'inactive', 'message': 'Your session is no longer active.'}

        if user_session['status'] == 'waiting_for_join_code':
            if is_user_joined(from_number):
                user_session['status'] = 'collecting_data'
                client.messages.create(
                    body="Welcome! Let's start by collecting some information. Please provide the value.",
                    from_=TWILIO_WHATSAPP_NUM,
                    to=f"whatsapp:{from_number}"
                )
                return {'status': 'welcome sent, collecting data'}
            else:
                client.messages.create(
                    body="Please join the sandbox by sending the join code.",
                    from_=TWILIO_WHATSAPP_NUM,
                    to=f"whatsapp:{from_number}"
                )
                return {'status': 'waiting for join code'}

        if user_session['status'] == 'collecting_data':
            return handle_data_collection(from_number, incoming_msg)
    except Exception as e:
        logging.error(f"Error processing message from {from_number}: {e}")
        return {'status': 'error'}


# Handle the data collection process
def handle_data_collection(from_number, incoming_msg):
    user_session = user_sessions[from_number]
    field_index = user_session['field_index']
    current_field = schema_fields[field_index]

    try:
        # Process value
        if current_field == 'value':
            if not re.search(r'\d+', incoming_msg):
                return request_field(from_number, 'Invalid value. Please provide a numeric value.', 'value')
            user_session['data']['value'] = incoming_msg
        # Process log_unit
        elif current_field == 'log_unit':
            user_session['data']['log_unit'] = incoming_msg
        # Process log_date
        elif current_field == 'log_date':
            log_date = validate_date(incoming_msg)
            if not log_date:
                return request_field(from_number, 'Invalid date format. Please provide the log date in YYYY-MM-DD format.', 'log_date')
            user_session['data']['log_date'] = log_date
        # Process evidence_url
        elif current_field == 'evidence_url':
            if incoming_msg.lower() == 'no evidence':
                user_session['data']['evidence_url'] = None
                user_session['field_index'] += 2  # Skip evidence_name
            elif incoming_msg.startswith('http'):
                user_session['data']['evidence_url'] = incoming_msg
            else:
                return request_field(from_number, 'Invalid URL. Please provide a valid URL or type "No evidence".', 'evidence_url')
        # Process evidence_name only if there is an evidence URL
        elif current_field == 'evidence_name':
            user_session['data']['evidence_name'] = incoming_msg

        # Proceed to the next field
        user_session['field_index'] += 1
        if user_session['field_index'] < len(schema_fields):
            next_field = schema_fields[user_session['field_index']]
            return request_field(f"whatsapp:{from_number}", f"Please provide {next_field.replace('_', ' ')}.", next_field)
        
        # All fields collected
        save_user_data_to_db(from_number, user_session['data'], user_sessions[from_number])
        reset_user_session(from_number)

    except Exception as e:
        logging.error(f"Error collecting data from {from_number}: {e}")
        client.messages.create(
            body="An unexpected error occurred. Please try again later.",
            from_=TWILIO_WHATSAPP_NUM,
            to=f"whatsapp:{from_number}"
        )
        return {'status': 'error'}

# Validate date format
def validate_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
    except ValueError:
        return None

# Request a specific field from the user
def request_field(phone_number, message, field):
    client.messages.create(
        body=message,
        from_=TWILIO_WHATSAPP_NUM,
        to=phone_number
    )
    logging.info(f"Requested {field} from {phone_number}")
    return {'status': 'waiting for correct data'}

def save_user_data_to_db(from_number, data, user_session):
    try:
        # Retrieve persistent IDs from session
        persistent_data = user_session.get('persistent_data', {})
        process_id = persistent_data.get('process_id')
        para_id = persistent_data.get('para_id')
        data_collection_id = persistent_data.get('data_collection_id')

        if not process_id or not para_id or not data_collection_id:
            logging.error("Missing process_id, para_id, or data_collection_id for saving data.")
            return {'status': 'error', 'message': 'Missing required IDs for saving data.'}

        # Insert data into Supabase
        supabase.table('parameter_log').insert({
            'log_date': data['log_date'],
            'value': data['value'],
            'log_unit': data['log_unit'],
            'evidence_url': data.get('evidence_url'),
            'evidence_name': data.get('evidence_name'),
            'process_id': process_id,
            'para_id': para_id,
            'data_collection_id': data_collection_id
        }).execute()

        client.messages.create(
            body="Data saved successfully! We'll ask for new data in 24 hours.",
            from_=TWILIO_WHATSAPP_NUM,
            to=f"whatsapp:{from_number}"
        )
        logging.info(f"Data saved for {from_number} with process_id: {process_id}, para_id: {para_id}, data_collection_id: {data_collection_id}")
        
        # Schedule the next data request
        schedule_next_data_request(f"whatsapp:{from_number}")

        # Reset user session but retain persistent IDs
        reset_user_session(from_number)

    except Exception as e:
        logging.error(f"Error saving data: {e}")
        client.messages.create(
            body="Error saving data. Please try again later.",
            from_=TWILIO_WHATSAPP_NUM,
            to=f"whatsapp:{from_number}"
        )


# Schedule next data request
def schedule_next_data_request(phone_number):
    def ask_for_data():
        # Retain the IDs while resetting the session for a new data collection
        reset_user_session(phone_number, keep_ids=True)
        client.messages.create(
            body="Let's collect new information. Please say hello and provide the value.",
            from_=TWILIO_WHATSAPP_NUM,
            to=phone_number
        )
        logging.info(f"Next data request sent to {phone_number}")

    # Schedule the job to run every 24 hours
    scheduler.add_job(
        ask_for_data,
        'interval',
        hours=COLLECT_DATA_INTERVAL_HOURS,
        id=f"data_request_{phone_number}",
        replace_existing=True
    )
    logging.info(f"Scheduled next data request for {phone_number} in 24 hours.")


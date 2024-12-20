from flask import Blueprint, request, jsonify
import logging
from services.chat_agent_services import CreateAgent


chatbot_bp = Blueprint('chatbot', __name__)
logger = logging.getLogger('vara-backend')

@chatbot_bp.route('/chatbot/message/query', methods=['POST'])
def get_chatbot_response():
    data = request.get_json()
    if not data or 'message' not in data or 'userId' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    user_message = data['message']
    user_id = data['userId']
    logger.info(f'Request received from userId: {user_id}')
    chain = CreateAgent.get_conversational_chain()
    response = chain.invoke(
    {"input": user_message},
    config={
        "configurable": {"session_id": user_id}
    },
    )
    res = response['answer']
    CreateAgent.check_message_history(user_id)
    logger.info(f'Request served for userId: {user_id}')
    return jsonify({'response':res})
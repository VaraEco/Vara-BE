from flask import Blueprint, request, jsonify
import logging
from services.chat_agent_services import CreateAgent
import traceback


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

@chatbot_bp.route('/chatbot/summarize', methods=['POST'])
def summarize_text():
    try:
        logger.info("Entering summarize_text function")
        data = request.get_json()
        logger.info(f"Received data: {data}")
        
        if not data or 'text' not in data or 'userId' not in data:
            logger.error("Invalid request data")
            return jsonify({'error': 'Invalid request'}), 400

        text_to_summarize = data['text']
        user_id = data['userId']
        logger.info(f'Summarization request received from userId: {user_id}')

        logger.info("Getting summary chain")
        summary_chain = CreateAgent.get_summary_chain()
        logger.info("Invoking summary chain")
        response = summary_chain.invoke({"text": text_to_summarize})
        logger.info(f"Summary chain response: {response}")

        logger.info(f'Summarization request served for userId: {user_id}')
        return jsonify({'summary': response})
    
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"An error occurred during summarization: {str(e)}")
        logger.error(error_traceback)
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500
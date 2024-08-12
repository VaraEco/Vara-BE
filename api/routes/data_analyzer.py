from flask import Blueprint, request, jsonify
import logging
from services.agent_services import AgentServices
from utils.data_analyzer_utils import DataAnalyzerUtils

data_analyzer_bp = Blueprint('data_analyzer', __name__)
logger = logging.getLogger('vara-backend')

@data_analyzer_bp.route('/data/analyze', methods=['POST'])
def get_data_analysis():
    if request.content_type == 'application/octet-stream':
        byte_array = request.data
    data = request.get_json()
    query = data['query']
    chat_id = data['chatId']
    file_name = chat_id+'.csv'
    agent_services = AgentServices()
    type_of_response_chain = agent_services.get_type_of_response_chain()
    type_of_response = type_of_response_chain.invoke({'query':query})
    first_level_chain = agent_services.get_first_level_chain()
    transformed_query = first_level_chain.invoke({'query':query})
    instruction_agent_executor = agent_services.get_instruction_generation_agent_executor(file_name)
    data_analyzer_utils = DataAnalyzerUtils(file_name)
    instructions = data_analyzer_utils.get_instructions(instruction_agent_executor, transformed_query)
    code_agent_executor = agent_services.get_code_generation_agent_executor(file_name)
    x_axis, y_axis, x_label, y_label = data_analyzer_utils.get_data(code_agent_executor, instructions)
    if type(x_axis) is not list:
        x_axis = x_axis.tolist()
    if type(y_axis) is not list:
        y_axis = y_axis.tolist()
    return jsonify({'type':type_of_response, 'x':x_axis, 'y':y_axis, 'x_label':x_label, 'y_label':y_label})
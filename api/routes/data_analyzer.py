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
    agent_services = AgentServices()
    first_level_chain = agent_services.get_first_level_chain()
    transformed_query = first_level_chain.invoke({'query':query})
    instruction_agent_executor = agent_services.get_instruction_generation_agent_executor()
    data_analyzer_utils = DataAnalyzerUtils('df_small.csv')
    instructions = data_analyzer_utils.get_instructions(instruction_agent_executor, transformed_query)
    code_agent_executor = agent_services.get_code_generation_agent_executor()
    x_axis, y_axis = data_analyzer_utils.get_data(code_agent_executor, instructions)
    return jsonify({'x':x_axis.tolist(), 'y':y_axis.tolist()})
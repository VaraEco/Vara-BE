from flask import Blueprint, request, jsonify
import logging
from services.agent_services import AgentServices
from utils.data_analyzer_utils import DataAnalyzerUtils
import pandas as pd

data_analyzer_bp = Blueprint('data_analyzer', __name__)
logger = logging.getLogger('vara-backend')

@data_analyzer_bp.route('/data/analyze', methods=['POST'])
def get_data_analysis():
    MAX_RETRIES = 3
    if request.content_type == 'application/octet-stream':
        byte_array = request.data
    data = request.get_json()
    query = data['query']
    chat_id = data['chatId']
    file_name = chat_id+'.csv'
    agent_services = AgentServices()
    data_analyzer_utils = DataAnalyzerUtils(file_name)
    data_analyzer_utils.create_csv()
    verification_agent = agent_services.get_verification_agent(file_name)
   
    verification_response = verification_agent.invoke({'input':query})
    if verification_response['output'].lower()!='okay':
        data_analyzer_utils.remove_file(file_name)
        return jsonify({'type':'retry', 'message':verification_response['output']})
    type_of_response_chain = agent_services.get_type_of_response_chain()
    type_of_response = type_of_response_chain.invoke({'query':query})

    first_level_chain = agent_services.get_first_level_chain()
    transformed_query = first_level_chain.invoke({'query':query})
    instruction_agent_executor = agent_services.get_instruction_generation_agent_executor(file_name)
    
    instructions = data_analyzer_utils.get_instructions(instruction_agent_executor, transformed_query)
    
    if type_of_response.lower()=='data':
        code_agent_executor = agent_services.get_data_code_generation_agent_executor(file_name)
        try:
            for attempt in range(MAX_RETRIES):
                try:
                    data_return, label = data_analyzer_utils.get_data(code_agent_executor, instructions)
                    break
                except Exception as e:
                    if attempt == MAX_RETRIES - 1:
                        logger.error(e)
                        return jsonify(e)
                    else:
                        continue  
        finally:
            data_analyzer_utils.remove_file(file_name)
        if type(data_return) is not int and type(data_return) is not str and type(data_return) is not list:
            data_return = data_return.tolist()
        return jsonify({'type':type_of_response, 'data':data_return, 'label':label})
    else:
        code_agent_executor = agent_services.get_graph_code_generation_agent_executor(file_name)
        try:
            for attempt in range(MAX_RETRIES):
                try:
                    x_axis, y_axis, x_label, y_label = data_analyzer_utils.get_graph_data(code_agent_executor, instructions)
                    break
                except Exception as e:
                    if attempt == MAX_RETRIES - 1:
                        logger.error(e)
                        return jsonify(e)
                    else:
                        continue
        finally:
            data_analyzer_utils.remove_file(file_name)
        y_label = str(y_label)
        x_label = str(x_label)
        if type(x_axis) is not list:
            x_axis = x_axis.tolist()
        if type(y_axis) is not list:
            y_axis = y_axis.tolist()
        return jsonify({'type':type_of_response, 'x':x_axis, 'y':y_axis, 'x_label':x_label, 'y_label':y_label})
    



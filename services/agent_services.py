from langchain.agents import AgentExecutor
from langchain_experimental.tools import PythonREPLTool
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import create_react_agent
from services.template_services import Template
from services.chatbot_services import Model

class AgentServices:

    def __init__(self) -> None:
        self.code_generation_tools = [PythonREPLTool()]
        self.instruction_generation_tools = [PythonREPLTool()]
    
    def get_instruction_generation_agent_executor(self, file):
        instruction_prompt = Template.get_code_instruction_prompt(file)
        model = Model.get_model()
        agent = create_react_agent(model, self.instruction_generation_tools, instruction_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.instruction_generation_tools, verbose=True, handle_parsing_errors=True)
        return agent_executor
    
    def get_graph_code_generation_agent_executor(self, file):
        code_generation_prompt = Template.last_level_instruction_prompt(file)
        model = Model.get_model()
        agent = create_react_agent(model, self.code_generation_tools, code_generation_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.code_generation_tools, verbose=True, handle_parsing_errors=True)
        return agent_executor
    
    def get_data_code_generation_agent_executor(self, file):
        code_generation_prompt = Template.last_level_data_instruction_prompt(file)
        model = Model.get_model()
        agent = create_react_agent(model, self.code_generation_tools, code_generation_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.code_generation_tools, verbose=True, handle_parsing_errors=True)
        return agent_executor


    def get_first_level_chain(self):
        first_level_prompt = Template.get_first_step_prompt()
        model = Model.get_model()
        first_level_chain = first_level_prompt | model | StrOutputParser()
        return first_level_chain

    def get_type_of_response_chain(self):
        type_of_response_prompt = Template.get_type_of_response_prompt()
        model = Model.get_model()
        type_of_response_chain = type_of_response_prompt | model | StrOutputParser()
        return type_of_response_chain
    
    def get_verification_agent(self, file):
        verification_prompt = Template.get_verification_prompt(file)
        model = Model.get_model()
        agent = create_react_agent(model, self.code_generation_tools, verification_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.code_generation_tools, verbose=True, handle_parsing_errors=True)
        return agent_executor
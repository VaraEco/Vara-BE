import pandas as pd
import awswrangler as wr
import re
import os

class DataAnalyzerUtils:
    def __init__(self, file_name) -> None:
        self.file_name = file_name
    
    def get_instructions(self, instruction_agent_executor, query):
        instructions = instruction_agent_executor.invoke({'input':query})
        return instructions
    
    def get_graph_data(self, code_agent_executor, query):
        code_string = code_agent_executor.invoke({'input':query})
        code = self.extract_code(code_string['output'])
        x_axis, y_axis, x_label, y_label = self.execute_graph_code(code)
        return x_axis, y_axis, x_label, y_label
    
    def get_data(self, code_agent_executor, query):
        code_string = code_agent_executor.invoke({'input':query})
        code = self.extract_code(code_string['output'])
        data, label = self.execute_data_code(code)
        return data,label


    def execute_graph_code(self, code):
        
    
        locals = {}
       
        exec(code, locals)
        return locals['x_axis'], locals['y_axis'], locals['x_label'], locals['y_label']
    
    def execute_data_code(self, code):
        
        locals = {}
       
        exec(code, locals) 
        return locals['return_value'], locals['label']
    
    def extract_code(self, code_string):
        code_block = re.search(r'```python\n(.*?)\n```', code_string, re.DOTALL).group(1)
        return code_block
    
    def get_file_url(self):
        base = 's3://compliance-document-bucket/{name}'
        url = base.format(name=self.file_name)
        return url
    
    def create_csv(self):
        csv_url = self.get_file_url()
        df = wr.s3.read_csv(csv_url)
        df.to_csv(self.file_name)

    def remove_file(self, file_name):
        if os.path.isfile(file_name):
            os.remove(file_name)
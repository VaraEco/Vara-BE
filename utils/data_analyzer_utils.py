import pandas as pd
import awswrangler as wr
import re
import os

class DataAnalyzerUtils:
    FILENAME = 'code_exec.py'
    def __init__(self, file_name) -> None:
        self.file_name = file_name
    
    def get_instructions(self, instruction_agent_executor, query):
        self.create_csv()
        instructions = instruction_agent_executor.invoke({'input':query})
        return instructions
    
    def get_data(self, code_agent_executor, query):
        code_string = code_agent_executor.invoke({'input':query})
        code = self.extract_code(code_string['output'])
        x_axis, y_axis, x_label, y_label = self.execute_code(code)
        return x_axis, y_axis, x_label, y_label


    def execute_code(self, code):
        
        if os.path.isfile(self.FILENAME):
            os.remove(self.FILENAME)
        with open(self.FILENAME, 'w') as file:
            file.write(code)
        locals = {}
       
        exec(open(self.FILENAME).read(), locals)
        os.remove(self.FILENAME)
        os.remove(self.file_name)
        return locals['x_axis'], locals['y_axis'], locals['x_label'], locals['y_label']
    
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
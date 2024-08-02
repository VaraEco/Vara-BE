import pandas as pd
import re
import os

class DataAnalyzerUtils:
    FILENAME = 'code_exec.py'
    def __init__(self, file_name) -> None:
        self.file_name = file_name
    
    def get_instructions(self, instruction_agent_executor, query):
        df = pd.read_csv(self.file_name)
        instructions = instruction_agent_executor.invoke({'input':query, 'schema':df.columns, 'sample':df.iloc[0]})
        return instructions
    
    def get_data(self, code_agent_executor, query):
        df = pd.read_csv(self.file_name)
        code_string = code_agent_executor.invoke({'input':query, 'schema':df.columns, 'sample':df.iloc[0]})
        code = self.extract_code(code_string['output'])
        self.execute_code(code)
        return x_axis.copy(), y_axis.copy()


    def execute_code(self, code):
        if os.path.isfile(self.FILENAME):
            os.remove(self.FILENAME)
        with open(self.FILENAME, 'w') as file:
            file.write(code)
        execfile(self.FILENAME)
        os.remove(self.FILENAME)

    
    def extract_code(self, code_string):
        code_block = re.search(r'```python\n(.*?)\n```', code_string, re.DOTALL).group(1)

        return code_block
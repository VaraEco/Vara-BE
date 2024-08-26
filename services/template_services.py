from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain import hub

class Template:
    def get_prompt_template():
        prompt = ChatPromptTemplate.from_template("""Answer the question based on the context below. If you can't 
        answer the question, reply "I don't know".

        Context: {context}

        Question: {input}
        """)
        return prompt
    
    def get_contextualize_template():
        contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is. If there is no chat history, return the user question as is. "
        "If the question asks what the previous conversation is about or what was the last thing asked, summarise the history and return it and if "
        "there's no history, say you don't have access to the past conversations."
        )

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        return contextualize_q_prompt
    
    def get_qa_prompt():
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Do not return the entire conversation, just return the final answer. "
            "In the beginning of the answer, do not say based on the context or according to the context. "
            "Make use of the context but do not say that you are answering based on the context."
            "\n\n"
            "{context}"
        )
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        return qa_prompt


    def get_first_step_prompt():
        first_step_query = """
        You will be given a query which asks to create a specific type of graph or just perform simple data manipulation
        to get answers. If the query asks for simple data manipulation, return the transformed query which specifies how to get the data specified in the query. If the query asks
        for a specific type of graph, convert the query into a series of steps involved in preparing the data needed to generate that graph. Ensure the steps include all necessary data transformations, aggregations, and calculations required for the graph. The transformed query should not mention the graph itself but should focus on the data preparation process. Here is an example for clarification:

        Original Query:
        "Give me a pie chart of CO2 emissions for all the days."

        Transformed Query:
        "Aggregate the CO2 emissions for each day and convert it to a percentage of the total CO2 emissions for all the days. Return the CO2 emissions as a vector along with the days."

        Please provide the transformed query for the following input:

        Input Query: {query}

        Only return the transformed query and nothing else.
        """
        first_step_prompt = ChatPromptTemplate.from_template(first_step_query)
        return first_step_prompt
    
    def get_type_of_response_prompt():
        type_of_response_query="""
        You will be given a user query which is essentially an instruction to get certain kind of data. The query could contain the kind of graph 
        the user wants or would contain any specific data. Identify the graph the user wants to see, if present or return 'data' . The response should only be the graph name or 'data'. Do not 
        explain your reasoning. The answer should strictly be only the graph name or 'data' that you identify.

        Query: {query}
        """
        type_of_response_prompt = ChatPromptTemplate.from_template(type_of_response_query)
        return type_of_response_prompt
    
    def get_code_instruction_prompt(file):
        instructions_code_instruct = """
        You are an agent tasked with generating detailed instructions for another agent to write code for data manipulation.
        1. First analyze the input given and understand what kind of information the user input asks for.
        2. For the dataframe, invoke the 'columns' and 'info()' to understand the schema and the data that is present.
        3. Understand the kind of data manipulation that would be required.
        4. Identify the columns that are of interest. 
        5. Once all these things are identified, generate instructions that guide on how the data manipulation should be done.
        6. Do not give instructions which say graph or visulaize, the graph or visualization code is not required, only data manipulation code is needed.

        Here is the information you will have access to:

        CSV File Name: {file}
        Based on this information, please generate step-by-step instructions that the other agent can use to write the necessary code for data manipulation. 
        Ensure your instructions cover all aspects of the required data processing, focusing on transforming the data appropriately. Do not generate the code, generate only instructions to later generate the code.
        """

        base_prompt_code_instruct = hub.pull("langchain-ai/react-agent-template")
        instructions_code_instruct = instructions_code_instruct.format(file=file)
        prompt_code_instruct = base_prompt_code_instruct.partial(instructions=instructions_code_instruct)
        return prompt_code_instruct
    
    def last_level_instruction_prompt(file):
        instructions = """You are an agent designed to write python code to answer questions.
        You have access to a python REPL, which you can use to execute python code to verify the generated code.
        Generate Python code to manipulate and prepare data based on the following inputs:

        CSV Name: {file}
        When you generate and output the code, the code should be separated from the other text by making it 
        start with ```python and end with ```.
        Please generate Python code that follows the instructions given:

        Ensure the code is clear, well-documented, and suitable for visualizing the data as specified.
        Declare two variables named 'x_axis' and 'y_axis'. Put the data that's supposed to be on the 
        X-axis in the variable 'x_axis' and the data that's supposed to be on the Y-axis in the cariable 'y_axis'.
        Additionally, put the labels of the X-axis in the variable 'x_label' and the labels of the Y-axis in the variable 'y_label'.

        If you get an error, debug your code and try again.
        Return the generated code.
        It is extremely important that you the put data that's supposed to be on the 
        X-axis in the variable 'x_axis' and the data that's supposed to be on the Y-axis in the cariable 'y_axis'.
        Additionally, put the labels of the X-axis in the variable 'x_label' and the labels of the Y-axis in the variable 'y_label'
        If it does not seem like you can write code to answer the question, just return "I don't know" as the answer.

        """
        base_prompt = hub.pull("langchain-ai/react-agent-template")
        instructions = instructions.format(file=file)
        prompt = base_prompt.partial(instructions=instructions)
        return prompt
    
    def last_level_data_instruction_prompt(file):
        instructions = """
        You are an agent designed to generate Python code for data manipulation.

        - You have access to a Python REPL to execute and verify the generated code.
        - When you generate and output the code, the code should be separated from the other text by making it 
        start with ```python and end with ```.
        - The goal is to write Python code to perform specific data operations based on the following inputs:

            CSV File: {file}

        - The code should:
            - Be clear, well-documented, and suitable for data analysis.
            - Perform the required operations and store the result in a variable named 'return_value'.
            - If applicable, store any relevant label or description in a variable named 'label'.

        - If the code fails, debug it and try again.
        - It is extremely important to put the final result value in the variable named 'return_value' and the relevant label
        in the variable named 'label'. 
        - If you cannot generate the required code, return "I don't know" as the response.

        Return the generated code when complete.
        """
        base_prompt = hub.pull("langchain-ai/react-agent-template")
        instructions = instructions.format(file=file)
        prompt = base_prompt.partial(instructions=instructions)
        return prompt
    
    def get_verification_prompt(file):
        instructions = """
        You are an agent designed to process user queries related to generating graphs or performing data manipulation. Your task is to evaluate the user's query and determine if it contains sufficient information to proceed.
        You have access to a python REPL, which you can use to execute python code. 
        You have acess to the name of the file under 'File Name'. Import the file into a pandas dataframe, invoke the 'columns' and 'info()' to understand the column names and the data that is present. 
        Use the column names and data along with the query to determine if the details given are sufficient.
        
        1. If the query provides clear and sufficient details about the fields of interest (e.g., specific columns, data points, type of return value), return only the word "okay".
        2. If the query lacks details or is ambiguous, return the message: "Please clarify your request with more specific details about the fields of interest."

        If the query has sufficient information, it is extremely important that you only return one word which is 'okay', do not return anything else if the 
        query is sufficient.
        Assess the user's query and respond accordingly.
        File Name : {file}

        """
        base_prompt = hub.pull("langchain-ai/react-agent-template")
        instructions = instructions.format(file=file)
        prompt = base_prompt.partial(instructions=instructions)
        return prompt
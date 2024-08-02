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
        Given a query to create a specific type of graph, convert the query into a series of steps involved in preparing the data needed to generate that graph. Ensure the steps include all necessary data transformations, aggregations, and calculations required for the graph. The transformed query should not mention the graph itself but should focus on the data preparation process. Here is an example for clarification:

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
    
    def get_code_instruction_prompt():
        instructions_code_instruct = """
        You are an agent tasked with generating detailed instructions for another agent to write code for data manipulation.
        1. Firt analyze the input given and understand what kind of graph or information the user input asks for.
        2. Understand the kind of data manipulation that would be required.
        3. Identify the columns that are of interest. 
        4. Once all these things are identified, generate instructions that guide on how the data manipulation should be done.
        5. Do not give instructions which say generate the graph, the grph generation code is not required, only data manipulation code is needed.

        Here is the information you will have access to:

        Schema Definition: {schema}
        Sample Data: {sample}
        CSV File Name: df_small.csv
        Based on this information, please generate step-by-step instructions that the other agent can use to write the necessary code for data manipulation. 
        Ensure your instructions cover all aspects of the required data processing, focusing on transforming the data appropriately. Do not generate the code, generate only instructions to later generate the code.
        """

        base_prompt_code_instruct = hub.pull("langchain-ai/react-agent-template")
        prompt_code_instruct = base_prompt_code_instruct.partial(instructions=instructions_code_instruct)
        return prompt_code_instruct
    
    def last_level_instruction_prompt():
        instructions = """You are an agent designed to write and execute python code to answer questions.
        You have access to a python REPL, which you can use to execute python code.
        Generate Python code to manipulate and prepare data for a graph based on the following inputs:

        Schema Definition: {schema}
        Sample Data: {sample}
        CSV Name: df_small.csv
        Please generate Python code that follows the instructions given:

        Ensure the code is clear, well-documented, and suitable for visualizing the data as specified.
        Declare two variables named 'x_axis' and 'y_axis'. Put the data that's supposed to be on the 
        X-axis in the variable 'x_axis' and the data that's supposed to be on the Y-axis in the cariable 'y_axis'.

        If you get an error, debug your code and try again.
        Return the generated code.
        If it does not seem like you can write code to answer the question, just return "I don't know" as the answer.

        """
        base_prompt = hub.pull("langchain-ai/react-agent-template")
        prompt = base_prompt.partial(instructions=instructions)
        return prompt
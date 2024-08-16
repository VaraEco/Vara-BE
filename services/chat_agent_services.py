from venv import logger
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever
from langchain.agents import Tool
from langchain.agents import initialize_agent
from services.chatbot_services import Model
from services.template_services import Template
from services.vectorstore_services import Vectorstore
from services.chat_history_services import ChatHistory
from langchain_core.output_parsers import StrOutputParser
import logging


class CreateAgent:
    
    history = None

    @staticmethod
    def get_stuff_document_chain():
        llm = Model.get_model()
        prompt = Template.get_qa_prompt()
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        return question_answer_chain
    
    @staticmethod
    def get_retrieval_chain():
        qa_chain = CreateAgent.get_stuff_document_chain()
        history_aware_retriever = CreateAgent.get_history_aware_retriever()
        retriever_chain = create_retrieval_chain(history_aware_retriever, qa_chain)
        return retriever_chain

    @staticmethod
    def get_memory_model():
        conversational_memory = ConversationBufferWindowMemory(memory_key='chat_history', k=5, return_messages=True)
        return conversational_memory
    
    @staticmethod
    def get_history_aware_retriever():
        llm = Model.get_model()
        retriever = Vectorstore.get_vectorstore('vara-doc-index')
        context_prompt = Template.get_contextualize_template()
        history_aware_retriever = create_history_aware_retriever(llm,retriever.as_retriever(search_kwargs={'k':6}),context_prompt)
        return history_aware_retriever
    
    @staticmethod
    def get_message_history():
        if CreateAgent.history is None:
            CreateAgent.history = ChatHistory()
        
    @staticmethod
    def get_conversational_chain():
        rag_chain = CreateAgent.get_retrieval_chain()
        CreateAgent.get_message_history()
        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            CreateAgent.history.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
        return conversational_rag_chain
    
    @staticmethod
    def check_message_history(session_id):
        CreateAgent.get_message_history()
        CreateAgent.history.check_and_delete(session_id)


    
    
    """def get_tool(self):
        retrieval_chain = self.get_retrieval_chain()

        tools = [
            Tool(
                name='Knowledge Base',
                func=retrieval_chain.invoke,
                description=(
                    'use this tool when answering knowledge queries to get '
                    'more information about the topic'
                )
            )
        ]
        return tools"""

    """def get_agent(self):
        tools = self.get_tool()
        
        memory = self.get_memory_model()
        agent = initialize_agent(
            agent='chat-conversational-react-description',
            tools=tools,
            llm=llm,
            verbose=True,
            max_iterations=3,
            early_stopping_method='generate',
            memory=memory
        )
        return agent"""

    @staticmethod
    def get_summary_chain():
        try:
            llm = Model.get_model()
            summary_prompt = Template.get_summary_prompt()
            summary_chain = summary_prompt | llm | StrOutputParser()
            return summary_chain
        except Exception as e:
            logger.error(f"Error in get_summary_chain: {str(e)}")
            raise
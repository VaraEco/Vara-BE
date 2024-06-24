from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder

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

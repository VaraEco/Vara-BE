from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

class ChatHistory:
    store = {}
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]
    
    def check_and_delete(self, session_id):
        if len(self.store[session_id].messages) >= 12:
            self.store[session_id].clear()
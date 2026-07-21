from .BaseDataModel import BaseDataModel
from .db_schemes import ChatHistory
from bson.objectid import ObjectId
from sqlalchemy.future import select
from sqlalchemy import delete
from typing import List


class ChatHistoryModel(BaseDataModel):
    
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance


    async def insert_chat_history(self, chat_history: ChatHistory):
        async with self.db_client() as session:
            async with session.begin():
                session.add(chat_history)
            await session.commit()
            await session.refresh(chat_history)
        return chat_history

        
    async def get_chat_history(self, project_id: int):
        
        async with self.db_client() as session:
            stmt = select(ChatHistory).where(ChatHistory.chat_project_id == project_id)
            result = await session.execute(stmt)
            records = result.scalars().all()
        return records


    @staticmethod
    def get_conversation_history(previous_chat_history: List[ChatHistory], generation_client=None):
        
        if generation_client is None or previous_chat_history is None:
            return None
        
        user_messages = [
            message.query
            for message in previous_chat_history
        ]
         
        assistant_messages = [
            message.answer
            for message in previous_chat_history
        ]
            
        conversation_history = []
        for user_message, assistant_message in zip(user_messages, assistant_messages):
            
            user_constructed_msg = generation_client.construct_prompt(
                role=generation_client.enums.USER.value, prompt=user_message
            )
            assistant_constructed_msg = generation_client.construct_prompt(
                role=generation_client.enums.ASSISTANT.value, prompt=assistant_message
            )
            
            conversation_history.append(user_constructed_msg)
            conversation_history.append(assistant_constructed_msg)       
                
        return conversation_history
    
    
    async def clear_chat_history(self, project_id: int):
        
        async with self.db_client() as session:
            stmt = delete(ChatHistory).where(ChatHistory.chat_project_id == project_id)
            result = await session.execute(stmt)
            await session.commit()
        return result.rowcount
    
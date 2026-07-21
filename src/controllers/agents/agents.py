from crewai import Agent, LLM
from .tools import search_engine_tool, web_scraping_tool
import logging
from helpers import get_settings


class CreateAgents:
    
    def __init__(self, model_id: str = None, api_key: str = None):
        
        self.model_id = model_id
        self.api_key = api_key
        
        settings = get_settings()
        
        self.basic_llm = self.get_llm(
            model_id=settings.GEMINI_MODEL_ID,
            api_key=settings.GEMENI_API_KEY,
            temperature=0.0
        )
        
        self.search_engine_tool = search_engine_tool
        self.web_scraping_tool = web_scraping_tool
        
        self.logger = logging.getLogger(__name__)
 
 
    def get_llm(self, model_id: str, api_key: str, temperature: float=0.0):
        
        agent_model_id, model_api_key = None, None
            
        if model_id and api_key:
            agent_model_id, model_api_key = model_id, api_key
            
        elif self.model_id and self.api_key:
            agent_model_id, model_api_key = self.model_id, self.api_key
        
        else:
            self.logger.error("Wrong agent Model ID or API key. Default Model will be used used.")
            return self.basic_llm
        
        return LLM(
                model=agent_model_id,
                api_key=model_api_key,
                temperature=temperature
            )
        
 
    def create_query_planning_agent(self, model_id: str = None, api_key: str = None, temperature: float=0.0):
    
        llm = self.get_llm(
            model_id=model_id,
            api_key=api_key,
            temperature=temperature
        )
                    
        return Agent(
            role='Query planning agent that decompose user query into sub-queries',
            goal='\n'.join([
                'Given a complex user query, your goal is to decompose the user query into sub-queries.',
                'Each sub-query will be converted into vector and we will search for this vector in our vector database to get relevant chunks.'
            ]),
            backstory='\n'.join([
                'This agent is used to decompose a complex user query into sub-queries to search for them in our vector database',
                'The user can ask a simple query that contains only a single requirement and also can ask a complex query that contains multiple tasks.',
                'Your job is to understand the user query and decompose it into a list of a single or multiple queries based on the meaning.'
            ]),
            llm=llm,
            verbose=False
        )
        
        
    def create_supervisor_agent(self, model_id: str = None, api_key: str = None, temperature: float=0.0):
    
        llm = self.get_llm(
            model_id=model_id,
            api_key=api_key,
            temperature=temperature
        )
        
        return Agent(
            role='Supervisor agent, that determines the source of data from 3 options.',
            goal='\n'.join([
                "Given a user query and relevant text chunks from my database. Your goal is to determine the suitable source of data among 3 options.",
                "You have to determine the source of data based on chunk relevance to the user's query based on semantic meaning, we have 3 options of data source."
            ]),
            backstory='\n'.join([
                "You are an expert in determining the best source of data and we have 3 options to get the data from.",
                "You will be provided with user query and relevant text chunks from my database.",
                "According to the user query and text chunks, you have to determine the suitable source of the data.",
                "You should make decision based on semantic meaning of user's query and text chunk.",
                "",
                "The 3 options are the following:",
                "1. Getting answer from my database.",
                "2. Getting answer from Web search.",
                "3. Getting answer from both my database and web search.",
            ]),
            llm=llm,
            verbose=False
        )
        
 
    def create_structured_agent(self, model_id: str = None, api_key: str = None, temperature: float=0.0, search_tool=None):
    
        llm = self.get_llm(
            model_id=model_id,
            api_key=api_key,
            temperature=temperature
        )
        
        if search_tool:
            self.search_engine_tool = search_tool
            

        return Agent(
            role='Structured agent, tries to find most relevant data to the user query.',
            goal='\n'.join([
                'Given a user query, your goal is to search the web for data that are related to this query.',
            ]),
            backstory='\n'.join([
                "I am trying to get the most relevant data to user's query on the web.",
                "Use the web search tool to search the web for the required data.",
            ]),
            llm=llm,
            tools=[self.search_engine_tool],
            verbose=False
        )
        
    def create_retrieval_agent(self, model_id: str = None, api_key: str = None, temperature: float=0.0, web_scraping_tool=None):
    
        llm = self.get_llm(
            model_id=model_id,
            api_key=api_key,
            temperature=temperature
        )
        
        if web_scraping_tool:
            self.web_scraping_tool = web_scraping_tool
            

        return Agent(
            role='Retrieval agent, tries to extract most relevant text chunks to the user query.',
            goal='\n'.join([
                'Given a user query and web results, your goal is to return a list of text chunks that are related to the query.',
            ]),
            backstory='\n'.join([
                "I need to get the most relevant text chunks to the user's query from the given web pages.",
                "You have to get the relevant text chunks based on the semantic meaning not just exact matching."
                "Use the web scraping tool to extract the web pages for the text chunks.",
            ]),
            llm=llm,
            tools=[self.web_scraping_tool],
            verbose=False
        )

 
    def create_verification_agent(self, model_id: str = None, api_key: str = None, temperature: float=0.0):
    
        llm = self.get_llm(
            model_id=model_id, # use rerank model
            api_key=api_key,
            temperature=temperature
        )
        
    
        return Agent(
            role="Verification agent, check how similar a user's query to the given text chunks.",
            goal='\n'.join([
                'Given a user query and relevant text chunks. Your goal is to rerank the chunks from the most relevant chunk to the lower relevant chunk.',
            ]),
            backstory='\n'.join([
                'I am building a RAG application, I want to rerank my text chunks to know the most relevant and similar chunks.',
                'You will be provided with user query and relevant text chunks from my database.',
                'You have to give a score for each text chunks by how relevant it to the user query, based on semantic meaning of text.',
            ]),
            llm=llm,
            verbose=False
        )
        
    def create_citation_agent(self, model_id: str = None, api_key: str = None, temperature: float=0.0):
        pass
        # llm = self.get_llm(
        #     model_id=model_id, # use rerank model
        #     api_key=api_key,
        #     temperature=temperature
        # )
        #           # modify  
        # return Agent(
        #     role='',
        #     goal='\n'.join([
        #         'Given a user query and relevant text chunks. Your goal is to rerank the chunks from the most relevant chunk to the lower relevant chunk.',
        #     ]),
        #     backstory='\n'.join([
        #         'I am building a RAG application, I want to rerank my text chunks to know the most relevant and similar chunks.',
        #         'You will be provided with user query and relevant text chunks from my database.',
        #         'According to the user query and text chunks, you have to determine the suitable source of the data.',
        #     ]),
        #     llm=llm,
        #     verbose=False
        # )
        
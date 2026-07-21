from crewai import Task
import os
import logging
from .pydantic_schemes import SubTasks, DataSource, AllSearchResults, TextChunks, RerankedOutput


class CreateTasks:
    
    def __init__(self, output_dir: str="controllers/agents/ai-agent-output"):
        
        self.output_dir = output_dir
        
        if output_dir is None:
            self.output_dir = "controllers/agents/ai-agent-output"
        
                
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
    
    def create_query_planning_task(self, query_planning_agent):
        
        return Task(
            description='\n'.join([
                'I am building a RAG system, so I have a vector database that contains text chunks from the user documents.',
                'When user ask a question about his documents, I need to divide this question into concise sub-queries based on his question meaning.',
                "I will the sub-queries to search in the vector database.",
                "The user's question can be just one query or multiple queries, you have to determine this depening on the meaning of the question.",
                "",
                'I will provide you with user query delimited by triple backticks.',
                'User query is ``` {query} ```.'
            ]),
            expected_output='A Python list of a single sub-query or multiple sub-queries',
            output_pydantic=SubTasks,
            output_file=os.path.join(self.output_dir, "step_1_subtasks.json"),
            agent=query_planning_agent
        )
        
        
    def create_supervisor_task(self, supervisor_agent):
        
        return Task(
            description='\n'.join([
                "You have 2 main inputs, which are the user query and a list of multiple relevant text chunks.",
                "Your task is to determine whether if these text chunks contain enough data to answer the user query or I need to search on the web to get more data.",
                "You have 3 options which are:",
                "1. Getting answer from my database.",
                "2. Getting answer from Web search.",
                "3. Getting answer from both my database and web search.",
                "",
                "If the text chunks contain the answer of the user's query , then return number 1",
                "If the text chunks don't contain the answer of the user's query , then return number 2",
                "If I don't provide you with text chunks or text chunks are None or empty list or empty string, then return number 2",
                "If the text chunks contain part of the answer or an incomplete answer of the user's query, then return number 3",
                "You should make decision based on the semantic meaning of the query and text chunks.",
                "",
                "The user query is delimited by triple backticks.",
                "``` {query} ```",
                "",
                "The text chunks are a list of strings and all of them are delimited by triple backticks. If there are no chunks provided, return number 2.",
                "``` {chunks} ```"
            ]),
            expected_output='An integer from 1 to 3',
            output_pydantic=DataSource,
            output_file=os.path.join(self.output_dir, "step_2_datasource.json"),
            agent=supervisor_agent
        )
        
    def create_structured_task(self, structured_agent):
        
        return Task(
            description='\n'.join([
                "You have given a user's query.",
                "You should use the web search tool to search for web pages that are related the user's query.",
                "You should decide which web page contain relevant data based on semantic meaning of the page content.",
                "",
                "I will give you the input query delimited by triple backticks as the following:",
                "User query: ``` {query} ```",
            ]),
            expected_output='A JSON object containing the search results as given in the Pydantic Schema.',
            output_json=AllSearchResults,
            output_file=os.path.join(self.output_dir, "step_3_supervisor.json"),
            agent=structured_agent
        )
        
        
    def create_retrieval_task(self, retrieval_agent):
        
        return Task(
            description='\n'.join([
                "You will be given user's query and web pages urls.",
                "The task is to extract relevant text chunks to user's query from different web pages urls.",
                "I want you to give me a list of text chunks that are relevant to the given use's query.",
                "",
                "I will give you the input query delimited by triple backticks as the following:",
                "User query: ``` {query} ```",
            ]),
            expected_output='A Python list of text chunks',
            output_pydantic=TextChunks,
            output_file=os.path.join(self.output_dir, "step_4_retrieval.json"),
            agent=retrieval_agent
        )
        
    def create_verification_task(self, verification_agent):
        
        return Task(
            description='\n'.join([
                "You will be given user's query and relevant text chunks.",
                "The task is to rerank these chunks by giving them a score of they are relevant to the query.",
                "Reranking is based on if each chunk contains the answer of the query or not, you have to check this based on the semantic meaning.",
                "The highest value of the reranking score is 5, and higher is better, so 5 is the best value.",
                "I will give you the inputs delimited by triple backticks as the following:",
                "User query: ``` {query} ```",
                "",
                "Relevant text chunks are the following list: ``` {chunks} ```",
            ]),
            expected_output='JSON object containing each chunk and its score',
            output_json=RerankedOutput,
            output_file=os.path.join(self.output_dir, "step_5_verification.json"),
            agent=verification_agent
        )
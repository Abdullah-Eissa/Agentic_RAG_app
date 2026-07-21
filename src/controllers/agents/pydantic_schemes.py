from pydantic import BaseModel, Field
from typing import List

class SubTasks(BaseModel):
    subtasks: List[str] = Field(..., title='Decomposed user query',
                                description='User query decomposed into a list of sub-tasks, and apply vector search on each sub-task on our vector database'
                          )
    
    
    
class DataSource(BaseModel):
    data_source: int = Field(..., title='Data source',
                                description='\n'.join([
                                    'Output should be one of the 3 numbers from 1 to 3 that indicates the following.',
                                    '1. Our database chunks.',
                                    '2. Web search.',
                                    '3. Both our database chunks and web search.'
                                    ])
                                )
    
class SearchResult(BaseModel):
    title: str = Field(..., title="Page title", description="This is the title of the searched web page.")
    
    search_query: str = Field(..., title="User's search query", description="This is the query that given from the user.")
    
    url: str = Field(..., title='URL of the web page',
        description="This is the URL of the web page that related to the user's query.")
    
    content: str = Field(..., title="Content of the searched web page", 
                         description="After applying web search, this is the contnet of the search results that is relevant to the user's query.")
    
    score: int = Field(..., title="Similarity score", 
                         description="\n".join([
                             "After applying web search, this should tell me how similar the web page to the query.",
                             "The score is from 1 to 5, the higher value means that web page is more relevant to the user's query."
                         ]))
    
class AllSearchResults(BaseModel):
    results: List[SearchResult] = Field(..., min_length=1, max_length=4, title="All search results",
                                        description="\n".join([
                                            "This is a list of all search results.",
                                            "Each record in this list is a single search result that follow specific Pydantic Schema."
                                        ]))
    
    
class TextChunks(BaseModel):
    chunks: List[str] = Field(..., title="List of Text chunks",
                                description='\n'.join([
                                    "Output is a list of text chunks that are relevant to the user's query.",
                                ]))
    
class SingleVerificationOutput(BaseModel):
    chunk: str = Field(..., title="Single Text chunk",
                                description='\n'.join([
                                    "Single text chunk that are relevant to the user's query.",
                                ]))
    score: float = Field(..., title="Similarity score",
                             description="\n".join([
                                 "This is the reranking score to determine how a text chunk relevant to the user query.",
                                 "The higher score value the more similarity between text chunk and query, and 5 is the highest value."
                             ]))
    
class RerankedOutput(BaseModel):
    reranked_output: List[SingleVerificationOutput]
from crewai import Crew, Process
from .agents import CreateAgents
from .tasks import CreateTasks

class GetCrews:
    
    def __init__(self, model_id: str = None, api_key: str = None, output_dir="controllers/agents/ai-agent-output"):
        
        self.create_agents = CreateAgents(model_id=model_id, api_key=api_key)
        self.create_tasks = CreateTasks(output_dir=output_dir)
        
        # Define Agents
        self.query_planning_agent = None
        self.supervisor_agent = None
        self.structured_agent = None
        self.retrieval_agent = None
        self.verification_agent = None
        
        
    # Set Agents
    def set_query_planning_agent(self, model_id: str=None, api_key: str=None, temperature: float = 0.0):
        
        self.query_planning_agent = self.create_agents.create_query_planning_agent(
            model_id=model_id,
            api_key=api_key,
            temperature=temperature
        )
        
    def set_supervisor_agent(self, model_id: str=None, api_key: str=None, temperature: float = 0.0):
        
        self.supervisor_agent = self.create_agents.create_supervisor_agent(
            model_id=model_id,
            api_key=api_key,
            temperature=temperature
        )
        
    def set_structured_agent(self, model_id: str=None, api_key: str=None, temperature: float = 0.0, search_tool = None):
        
        self.structured_agent = self.create_agents.create_structured_agent(
            model_id=model_id,
            api_key=api_key,
            temperature=temperature,
            search_tool=search_tool
        )
        
    def set_retrieval_agent(self, model_id: str=None, api_key: str=None, temperature: float = 0.0, web_scraping_tool = None):
        
        self.retrieval_agent = self.create_agents.create_retrieval_agent(
            model_id=model_id,
            api_key=api_key,
            temperature=temperature,
            web_scraping_tool=web_scraping_tool
        )
        
    def set_verification_agent(self, model_id: str=None, api_key: str=None, temperature: float = 0.0):
        
        self.verification_agent = self.create_agents.create_verification_agent(
            model_id=model_id,
            api_key=api_key,
            temperature=temperature,
        )
        
    
    def query_planning_crew(self):
        
        if self.query_planning_agent is None:
            self.set_query_planning_agent() # if the agent is not set, then set it to the default model (gemini)
            
        self.query_planning_task = self.create_tasks.create_query_planning_task(query_planning_agent=self.query_planning_agent)
        
        
        return Crew(
            agents=[self.query_planning_agent,],
            tasks=[self.query_planning_task,],
            process=Process.sequential
        )
        
    def data_source_crew(self):
        
        if self.supervisor_agent is None:
            self.set_supervisor_agent()
            
        self.supervisor_task = self.create_tasks.create_supervisor_task(supervisor_agent=self.supervisor_agent)
        
        return Crew(
            agents=[self.supervisor_agent],
            tasks=[self.supervisor_task],
            process=Process.sequential
        )
        
        
    def getting_chunks_crew(self):
        
        if self.structured_agent is None:
            self.set_structured_agent()
            
        if self.retrieval_agent is None:
            self.set_retrieval_agent()
        
        self.structured_task = self.create_tasks.create_structured_task(structured_agent=self.structured_agent)
        self.retrieval_task = self.create_tasks.create_retrieval_task(retrieval_agent=self.retrieval_agent)
        
        return Crew(
            agents=[self.structured_agent, self.retrieval_agent],
            tasks=[self.structured_task, self.retrieval_task],
            process=Process.sequential
        )
        
    
    def getting_verification_crew(self):
        
        if self.verification_agent is None:
            self.set_verification_agent()
            
        self.verification_task = self.create_tasks.create_verification_task(verification_agent=self.verification_agent)
        
        return Crew(
            agents=[self.verification_agent],
            tasks=[self.verification_task],
            process=Process.sequential
        )
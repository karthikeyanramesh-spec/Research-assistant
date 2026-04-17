from sys import implementation
from tabnanny import verbose
from crewai import Agent, Crew, Process, Task
from crewai import tools
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import tool
import mcp
from autogen_validation import autogen_pipeline
from tools import autogen_modifier



@CrewBase
class Reportwriter():
    """Report writer crew"""

    agents_config='agent.yaml'
    tasks_config= 'tasks.yaml'

   

    
    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['analyst'], verbose=True
        )
    
    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config['writer'], verbose=True
        )
    
     

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'],
        )
    
    @task
    def writing_task(self) -> Task:
        return Task(
            config=self.tasks_config['writing_task'],
            tools = [autogen_modifier], 
            context=[self.analysis_task()]
        )

   



    @crew
    def crew(self) -> Crew:
        """Creates the Report Generation Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,

        )
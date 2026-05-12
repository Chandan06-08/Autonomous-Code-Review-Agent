from crewai import Agent

class PlannerAgent:
    def __init__(self, llm):
        self.llm = llm

    def create(self):
        return Agent(
            role='Lead Software Planner',
            goal='Analyze GitHub issues and create a step-by-step repair strategy',
            backstory="""You are an expert software architect with deep experience in debugging complex systems. 
            You can read an issue description and immediately identify the likely cause and which files are involved.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

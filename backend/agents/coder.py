from crewai import Agent

class CoderAgent:
    def __init__(self, llm):
        self.llm = llm

    def create(self):
        return Agent(
            role='Senior Software Engineer',
            goal='Write clean, efficient, and bug-free code fixes based on the plan',
            backstory="""You are a coding prodigy. You write minimal, elegant code that 
            solves the problem perfectly. You follow all best practices and ensure 
            your changes don't break existing functionality.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

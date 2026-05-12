from crewai import Agent

class TesterAgent:
    def __init__(self, llm):
        self.llm = llm

    def create(self):
        return Agent(
            role='QA Automation Engineer',
            goal='Run tests, analyze failures, and provide detailed stack trace feedback',
            backstory="""You are a testing expert. You know how to trigger edge cases 
            and your feedback is so detailed that it makes fixing bugs easy for the coder. 
            You are relentless in ensuring code quality.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

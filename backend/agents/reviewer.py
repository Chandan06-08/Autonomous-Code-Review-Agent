from crewai import Agent

class ReviewerAgent:
    def __init__(self, llm):
        self.llm = llm

    def create(self):
        return Agent(
            role='Senior Code Reviewer',
            goal='Review the final patch for logic, security, and hallucinations',
            backstory="""You are the final gatekeeper. You have an eye for detail and 
            can spot a potential bug from a mile away. You ensure that the fix 
            truly addresses the issue and meets production standards.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=True
        )

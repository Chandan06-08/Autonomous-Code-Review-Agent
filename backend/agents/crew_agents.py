from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    if os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model_name="gpt-4o")
    elif os.getenv("GEMINI_API_KEY"):
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro")
    else:
        raise ValueError("No LLM API key found")

class CodeReviewAgents:
    def __init__(self):
        self.llm = get_llm()

    def planner_agent(self):
        return Agent(
            role='Lead Software Planner',
            goal='Analyze GitHub issues and create a step-by-step repair strategy',
            backstory="""You are an expert software architect with deep experience in debugging complex systems. 
            You can read an issue description and immediately identify the likely cause and which files are involved.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def coder_agent(self):
        return Agent(
            role='Senior Software Engineer',
            goal='Write clean, efficient code fixes for the identified bug',
            backstory="""You are a coding prodigy. You write bug-free code and follow best practices. 
            You focus on minimal changes that solve the problem without introducing side effects.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def tester_agent(self):
        return Agent(
            role='QA Engineer',
            goal='Run tests and provide detailed feedback on failures',
            backstory="""You are meticulous and thorough. You don't just run tests; you analyze stack traces 
            and explain exactly why a test failed to help the coder fix it.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def reviewer_agent(self):
        return Agent(
            role='Code Reviewer',
            goal='Review the final patch for quality, security, and logic',
            backstory="""You are the final gatekeeper. You ensure that the code is production-ready, 
            secure, and truly solves the issue described.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=True
        )

import os
import uuid
from crewai import Agent, Task, Crew, LLM
from ..agents.planner import PlannerAgent
from ..agents.coder import CoderAgent
from ..agents.tester import TesterAgent
from ..agents.reviewer import ReviewerAgent
from ..tools.github_tool import GitHubTool
from ..tools.all_tools import clone_repository, search_codebase, run_tests, create_pull_request
from .retry_loop import AutoGenRetryLoop

class Orchestrator:
    def __init__(self, workspace_root: str = "./workspaces"):
        self.workspace_root = workspace_root
        os.makedirs(workspace_root, exist_ok=True)
        self.github = GitHubTool()
        self.logs = []
        # Use CrewAI's native LLM class
        self.llm = LLM(model="openai/gpt-4o")
        
        # Initialize agents
        self.planner = PlannerAgent(self.llm).create()
        self.coder = CoderAgent(self.llm).create()
        self.tester = TesterAgent(self.llm).create()
        self.reviewer = ReviewerAgent(self.llm).create()

    def log(self, message: str, agent: str = "System"):
        entry = {"message": message, "agent": agent, "timestamp": str(uuid.uuid4())}
        self.logs.append(entry)
        print(f"[{agent}] {message}")

    async def run(self, issue_url: str):
        session_id = str(uuid.uuid4())[:8]
        repo_path = os.path.normpath(os.path.join(os.getcwd(), self.workspace_root, session_id))
        
        try:
            # 1. Parse GitHub Issue
            self.log(f"Fetching issue details: {issue_url}")
            issue_info = self.github.get_issue_details(issue_url)

            # 2. Clone Repository
            self.log(f"Cloning {issue_info['repo']}...")
            clone_repository.invoke({"repo_url": issue_info['clone_url'], "dest_path": repo_path})

            # 3. Index & Search
            self.log("Indexing codebase and searching for context...")
            context = search_codebase.invoke({"query": f"{issue_info['title']} {issue_info['body']}"})

            # 4. Planning & Coding Loop (Max 3 retries)
            attempts = 0
            success = False
            current_plan = ""

            while attempts < 3 and not success:
                attempts += 1
                self.log(f"Execution Attempt {attempts}/3...", agent="Planner")
                
                # Plan
                plan_task = Task(
                    description=f"Issue: {issue_info['title']}\nContext: {context}",
                    expected_output="A repair strategy.",
                    agent=self.planner
                )
                current_plan = Crew(agents=[self.planner], tasks=[plan_task]).kickoff()
                self.log(f"Plan generated: {current_plan[:100]}...", agent="Planner")

                # Code
                self.log("Applying code changes...", agent="Coder")
                code_task = Task(
                    description=f"Apply fix based on: {current_plan}",
                    expected_output="Code applied to files.",
                    agent=self.coder
                )
                Crew(agents=[self.coder], tasks=[code_task]).kickoff()

                # Test
                self.log("Verifying with pytest...", agent="Tester")
                test_results = run_tests.invoke({"repo_path": repo_path})
                
                if "FAILED" not in test_results:
                    success = True
                    self.log("Tests passed!", agent="Tester")
                else:
                    self.log(f"Tests failed. Initiating reflection loop...", agent="System")
                    # AutoGen Debate
                    retry_loop = AutoGenRetryLoop({"config_list": [{"model": "gpt-4o", "api_key": os.getenv("OPENAI_API_KEY")}]})
                    current_plan = retry_loop.run_debate(current_plan, test_results)
                    self.log("Strategy refined through debate.", agent="Reviewer")

            if success:
                # 5. Finalize PR
                self.log("Reviewing and opening Pull Request...", agent="Reviewer")
                pr_url = create_pull_request.invoke({
                    "repo_name": f"{issue_info['owner']}/{issue_info['repo']}",
                    "title": f"Fix: {issue_info['title']}",
                    "body": "This PR was generated autonomously by AURA.",
                    "head": f"aura-fix-{session_id}"
                })
                self.log(f"PR Opened: {pr_url}", agent="Reviewer")
                return {"status": "success", "pr_url": pr_url}
            else:
                self.log("Maximum retry attempts reached. Workflow failed.", agent="System")
                return {"status": "failed", "message": "Max retries reached"}

        except Exception as e:
            self.log(f"Error: {str(e)}", agent="System")
            return {"status": "error", "message": str(e)}

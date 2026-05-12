import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

class GitHubTool:
    def __init__(self, token: str = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN not found in environment variables")
        self.g = Github(self.token)

    def get_issue_details(self, issue_url: str):
        """Extracts owner, repo, and issue number from URL and fetches details."""
        # Example URL: https://github.com/owner/repo/issues/1
        parts = issue_url.strip("/").split("/")
        owner = parts[-4]
        repo_name = parts[-3]
        
        # Handle URLs with fragments (e.g., #issue-123) or query params
        issue_number_str = parts[-1].split("#")[0].split("?")[0]
        issue_number = int(issue_number_str)

        repo = self.g.get_repo(f"{owner}/{repo_name}")
        issue = repo.get_issue(number=issue_number)

        return {
            "title": issue.title,
            "body": issue.body,
            "owner": owner,
            "repo": repo_name,
            "clone_url": repo.clone_url
        }

    def create_pull_request(self, repo_full_name: str, title: str, body: str, head_branch: str, base_branch: str = "main"):
        """Creates a pull request."""
        repo = self.g.get_repo(repo_full_name)
        pr = repo.create_pull(title=title, body=body, head=head_branch, base=base_branch)
        return pr.html_url

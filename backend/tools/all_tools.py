import os
import subprocess
from langchain.tools import tool
from git import Repo
from github import Github
from ..vectorstore.chroma_manager import ChromaManager

# Initialize ChromaManager for the search tool
chroma = ChromaManager()

@tool
def read_file(file_path: str) -> str:
    """Reads the content of a file from the local repository."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool
def write_file(file_path: str, content: str) -> str:
    """Writes or updates content in a specific file."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@tool
def run_tests(repo_path: str) -> str:
    """Runs pytest in the repository and returns the output."""
    try:
        result = subprocess.run(
            ["pytest", "--tb=short"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        return f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
    except Exception as e:
        return f"Error running tests: {str(e)}"

@tool
def search_codebase(query: str) -> str:
    """Performs a semantic search over the codebase to find relevant snippets."""
    results = chroma.search(query, n_results=5)
    formatted = ""
    for i, doc in enumerate(results['documents'][0]):
        path = results['metadatas'][0][i]['path']
        formatted += f"--- File: {path} ---\n{doc}\n\n"
    return formatted

@tool
def create_pull_request(repo_name: str, title: str, body: str, head: str, base: str = "main") -> str:
    """Creates a Pull Request on GitHub."""
    try:
        g = Github(os.getenv("GITHUB_TOKEN"))
        repo = g.get_repo(repo_name)
        pr = repo.create_pull(title=title, body=body, head=head, base=base)
        return f"Pull Request created: {pr.html_url}"
    except Exception as e:
        return f"Error creating PR: {str(e)}"

@tool
def clone_repository(repo_url: str, dest_path: str) -> str:
    """Clones a remote repository to a local path."""
    try:
        if os.path.exists(dest_path):
            import shutil
            shutil.rmtree(dest_path)
        Repo.clone_from(repo_url, dest_path)
        return f"Successfully cloned into {dest_path}"
    except Exception as e:
        return f"Error cloning repository: {str(e)}"

@tool
def generate_diff(repo_path: str) -> str:
    """Generates the git diff of the current changes."""
    try:
        repo = Repo(repo_path)
        return repo.git.diff()
    except Exception as e:
        return f"Error generating diff: {str(e)}"

@tool
def install_dependencies(repo_path: str) -> str:
    """Installs dependencies from requirements.txt if it exists."""
    req_file = os.path.join(repo_path, "requirements.txt")
    if os.path.exists(req_file):
        try:
            subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=repo_path, check=True)
            return "Dependencies installed successfully."
        except Exception as e:
            return f"Error installing dependencies: {str(e)}"
    return "No requirements.txt found."

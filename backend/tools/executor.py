import subprocess
import os

class CodeExecutor:
    @staticmethod
    def run_tests(repo_path: str):
        """Runs pytest in the given directory and captures output."""
        try:
            # We run pytest and capture stdout and stderr
            result = subprocess.run(
                ["pytest", "--tb=short"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=60  # Timeout after 60 seconds
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Tests timed out after 60 seconds."
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e)
            }

    @staticmethod
    def apply_patch(repo_path: str, file_path: str, content: str):
        """Writes content to a file."""
        full_path = os.path.join(repo_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully updated {file_path}"

import io
import sys
import traceback
from typing import Dict, Any, Optional

class Sandbox:
    """
    An interactive sandbox for executing Python code safely (in terms of state persistence,
    not necessarily security-wise).
    """
    def __init__(self):
        # Initialize persistent state for the sandbox
        self.globals = {"__builtins__": __builtins__}
        self.locals = {}

    def execute(self, code: str) -> Dict[str, Any]:
        """
        Executes the given Python code and returns the results.
        
        Args:
            code (str): The Python code to execute.
            
        Returns:
            Dict[str, Any]: A dictionary containing stdout, stderr, and error (if any).
        """
        stdout = io.StringIO()
        stderr = io.StringIO()
        
        # Save current stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        error = None
        try:
            # Redirect stdout and stderr
            sys.stdout = stdout
            sys.stderr = stderr
            
            # Execute the code with persistent globals and locals
            exec(code, self.globals, self.locals)
        except Exception:
            # Capture the full traceback if an exception occurs
            error = traceback.format_exc()
        finally:
            # Restore original stdout and stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
        return {
            "stdout": stdout.getvalue(),
            "stderr": stderr.getvalue(),
            "error": error
        }

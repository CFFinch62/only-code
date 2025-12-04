# Only Code Editor - Python Scripting Engine
# Python script execution with restricted environment

from typing import Optional, Dict, Any
from pathlib import Path

from .editor_api import EditorAPI


class PythonEngine:
    """
    Python script execution engine with sandboxing.
    
    Provides a restricted environment for running Python scripts with
    access to the editor API but limited builtins and no imports.
    """

    # Safe builtins to expose
    SAFE_BUILTINS = {
        # Types
        'bool': bool,
        'int': int,
        'float': float,
        'str': str,
        'list': list,
        'dict': dict,
        'tuple': tuple,
        'set': set,
        'frozenset': frozenset,
        'bytes': bytes,
        'bytearray': bytearray,
        
        # Functions
        'abs': abs,
        'all': all,
        'any': any,
        'ascii': ascii,
        'bin': bin,
        'chr': chr,
        'divmod': divmod,
        'enumerate': enumerate,
        'filter': filter,
        'format': format,
        'hash': hash,
        'hex': hex,
        'isinstance': isinstance,
        'issubclass': issubclass,
        'iter': iter,
        'len': len,
        'map': map,
        'max': max,
        'min': min,
        'next': next,
        'oct': oct,
        'ord': ord,
        'pow': pow,
        'print': print,
        'range': range,
        'repr': repr,
        'reversed': reversed,
        'round': round,
        'slice': slice,
        'sorted': sorted,
        'sum': sum,
        'zip': zip,
        
        # Exceptions (for error handling)
        'Exception': Exception,
        'ValueError': ValueError,
        'TypeError': TypeError,
        'KeyError': KeyError,
        'IndexError': IndexError,
        'AttributeError': AttributeError,
        
        # Constants
        'True': True,
        'False': False,
        'None': None,
    }

    def __init__(self, editor_api: EditorAPI):
        """
        Initialize the Python engine.
        
        Args:
            editor_api: EditorAPI instance for editor interaction
        """
        self.editor_api = editor_api
        self._last_error: Optional[str] = None

    def _create_restricted_globals(self) -> Dict[str, Any]:
        """Create a restricted globals dictionary for script execution."""
        # Start with safe builtins
        restricted = {
            '__builtins__': self.SAFE_BUILTINS.copy(),
            '__name__': '__main__',
            '__doc__': None,
        }
        
        # Add editor API
        restricted['editor'] = self.editor_api
        
        return restricted

    def execute_file(self, file_path: Path, entry_point: str = None) -> bool:
        """
        Execute a Python script file.
        
        Args:
            file_path: Path to the Python script
            entry_point: Optional function name to call after loading
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not file_path.exists():
                self._last_error = f"Script file not found: {file_path}"
                return False
            
            code = file_path.read_text(encoding='utf-8')
            return self.execute_string(code, entry_point, str(file_path))
            
        except Exception as e:
            self._last_error = f"Failed to read script: {e}"
            return False

    def execute_string(self, code: str, entry_point: str = None, 
                       filename: str = "<script>") -> bool:
        """
        Execute Python code from a string.
        
        Args:
            code: Python code to execute
            entry_point: Optional function name to call after loading
            filename: Filename for error messages
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create fresh restricted environment
            restricted_globals = self._create_restricted_globals()
            
            # Compile and execute
            compiled = compile(code, filename, 'exec')
            exec(compiled, restricted_globals)
            
            # Call entry point if specified
            if entry_point:
                if entry_point not in restricted_globals:
                    self._last_error = f"Entry point '{entry_point}' not found"
                    return False
                func = restricted_globals[entry_point]
                if not callable(func):
                    self._last_error = f"Entry point '{entry_point}' is not callable"
                    return False
                func()
            
            self._last_error = None
            return True
            
        except Exception as e:
            self._last_error = str(e)
            return False

    def get_last_error(self) -> Optional[str]:
        """Get the last error message, if any."""
        return self._last_error


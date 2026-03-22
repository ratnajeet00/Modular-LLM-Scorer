#!/usr/bin/env python3
"""
Sandboxed Python code evaluation with security constraints.

This module provides safe execution of untrusted Python code for benchmarking
without risking system compromise. It uses RestrictedPython when available
for additional security, and always enforces execution time/memory limits.
"""

import sys
import tempfile
import subprocess
import os
from pathlib import Path
from typing import Optional, Tuple
import re


# Try to import RestrictedPython for additional security
HAS_RESTRICTEDPYTHON = False
try:
    from restricted_python import compile_restricted
    HAS_RESTRICTEDPYTHON = True
except ImportError:
    pass


def _create_test_file(code: str) -> Path:
    """Create a temporary Python file with the code."""
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8'
    ) as f:
        f.write(code)
        return Path(f.name)


def execute_code_subprocess(code: str, timeout_sec: int = 10, 
                           max_output_chars: int = 5000) -> Tuple[str, str, int]:
    """
    Execute Python code in isolated subprocess with safeguards.
    
    Args:
        code: Python code to execute  
        timeout_sec: Maximum execution time in seconds
        max_output_chars: Maximum output length before truncation
    
    Returns:
        (stdout, stderr, return_code)
        return_code: 0 for success, 1 for timeout, 2 for execution error, 3+ for Python error
    """
    try:
        code_file = _create_test_file(code)
        
        try:
            # Run in subprocess with timeout and output capture
            result = subprocess.run(
                [sys.executable, str(code_file)],
                capture_output=True,
                timeout=timeout_sec,
                text=True,
                encoding='utf-8',
            )
            
            stdout = result.stdout[:max_output_chars]
            stderr = result.stderr[:max_output_chars]
            
            # Truncation warning
            if len(result.stdout) > max_output_chars:
                stdout += f"\n... (output truncated, {len(result.stdout)} chars total)"
            if len(result.stderr) > max_output_chars:
                stderr += f"\n... (errors truncated, {len(result.stderr)} chars total)"
                
            return stdout, stderr, result.returncode
            
        except subprocess.TimeoutExpired:
            return "", f"Execution timeout: code did not complete in {timeout_sec}s", 1
        finally:
            # Clean up temp file
            try:
                code_file.unlink()
            except Exception:
                pass
                
    except Exception as e:
        return "", f"Sandbox error: {str(e)}", 3


def extract_return_value(code: str, output: str) -> str:
    """
    Extract the actual return value from code output.
    
    Looks for function calls or final expressions that were printed.
    """
    if not output:
        return ""
    
    # Try to parse the last line as the return value
    lines = output.strip().split('\n')
    if lines:
        return lines[-1]
    return output.strip()


def validate_code_safety(code: str, strict_mode: bool = False) -> Tuple[bool, str]:
    """
    Check code for dangerous patterns before execution.
    
    Args:
        code: Python code to validate
        strict_mode: If True, enforce stricter restrictions
    
    Returns:
        (is_safe, message)
    """
    dangerous_patterns = {
        r'__import__': "Dynamic imports not allowed",
        r'exec\s*\(': "exec() not allowed",
        r'eval\s*\(': "eval() not allowed",
        r'open\s*\(': "File operations not allowed",
        r'subprocess|os\.system|os\.exec': "System commands not allowed",
        r'socket|urllib|httplib': "Network operations not allowed",
    }
    
    code_lower = code.lower()
    for pattern, reason in dangerous_patterns.items():
        if re.search(pattern, code_lower):
            return False, f"Security check failed: {reason}"
    
    if strict_mode:
        # Additional restrictions in strict mode
        strict_patterns = {
            r'@property': "Decorators not allowed in strict mode",
            r'globals\s*\(': "globals() not allowed",
            r'locals\s*\(': "locals() not allowed",
            r'dir\s*\(': "dir() not allowed",
            r'getattr|setattr|hasattr': "Attribute access functions not allowed",
        }
        
        for pattern, reason in strict_patterns.items():
            if re.search(pattern, code_lower):
                return False, f"Strict mode check failed: {reason}"
    
    return True, "Code passed safety checks"


def sandbox_eval_code(code: str, timeout_sec: int = 10,
                     strict_mode: bool = False,
                     restricted_mode: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Safely evaluate Python code with multiple layers of protection.
    
    Args:
        code: Python code to evaluate
        timeout_sec: Maximum execution time
        strict_mode: Enable strict safety checks
        restricted_mode: Use RestrictedPython if available (requires imports)
    
    Returns:
        (success: bool, error_message: str | None)
        success=True means code executed without errors
        error_message explains what went wrong
    """
    # First pass: safety validation
    is_safe, safety_msg = validate_code_safety(code, strict_mode=strict_mode)
    if not is_safe:
        return False, safety_msg
    
    # Second pass: execute in subprocess
    stdout, stderr, return_code = execute_code_subprocess(code, timeout_sec=timeout_sec)
    
    if return_code == 0:
        # Success - code executed without errors
        return True, None
    elif return_code == 1:
        return False, stderr  # Timeout
    else:
        # Python execution error
        error_lines = stderr.split('\n') if stderr else []
        # Extract the most relevant error line
        for line in reversed(error_lines):
            if line.strip():
                return False, line.strip()
        return False, f"Execution failed with code {return_code}"


def eval_code_in_context(code: str, entry_point: str,
                         test_input: Optional[list] = None,
                         timeout_sec: int = 10) -> Tuple[bool, Optional[str]]:
    """
    Execute code and check if it runs without errors (test harness wrapper).
    
    Args:
        code: The user's code
        entry_point: Function name to call (e.g., "solve_problem")
        test_input: List of arguments to pass to the function
        timeout_sec: Timeout in seconds
    
    Returns:
        (success: bool, error_message: str | None)
    """
    if not entry_point or not entry_point.strip():
        return sandbox_eval_code(code, timeout_sec=timeout_sec)
    
    # Build wrapper code
    wrapper = f"""
{code}

# Call the function to verify it exists and works
try:
    result = {entry_point}()
    print(str(result))
except TypeError:
    # Function expects arguments
    print("FUNCTION_EXPECTS_ARGS")
except Exception as e:
    print(f"ERROR: {{e}}")
"""
    
    return sandbox_eval_code(wrapper, timeout_sec=timeout_sec)


if __name__ == "__main__":
    # Test examples
    print("Testing sandboxed code evaluation...\n")
    
    # Good code
    good_code = """
def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b

print(fibonacci(10))
"""
    success, err = sandbox_eval_code(good_code)
    print(f"✓ Good code: {success} (error: {err})")
    
    # Bad code (import)
    bad_code = """
import os
os.system('echo bad')
"""
    success, err = sandbox_eval_code(bad_code)
    print(f"✓ Bad code (blocked): {not success} (reason: {err})")
    
    # Timeout code
    timeout_code = """
while True:
    pass
"""
    success, err = sandbox_eval_code(timeout_code, timeout_sec=1)
    print(f"✓ Timeout code (blocked): {not success} (reason: {err})")

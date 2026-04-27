import pytest
from openharness.src.framework.sandbox import Sandbox

def test_sandbox_execution_and_persistence():
    sandbox = Sandbox()
    
    # First execution: define a variable
    result1 = sandbox.execute("x = 10")
    assert result1["error"] is None
    
    # Second execution: use the variable and print it
    result2 = sandbox.execute("print(x)")
    assert result2["stdout"].strip() == "10"
    assert result2["error"] is None
    
    # Third execution: modify variable
    sandbox.execute("x += 5")
    result3 = sandbox.execute("print(x)")
    assert result3["stdout"].strip() == "15"

def test_sandbox_stdout_capture():
    sandbox = Sandbox()
    result = sandbox.execute("print('Hello, World!')")
    assert result["stdout"] == "Hello, World!\n"
    assert result["stderr"] == ""
    assert result["error"] is None

def test_sandbox_exception_capture():
    sandbox = Sandbox()
    result = sandbox.execute("1 / 0")
    assert "ZeroDivisionError" in result["error"]
    assert result["stdout"] == ""

def test_sandbox_function_definition_and_access():
    sandbox = Sandbox()
    sandbox.execute("x = 5")
    sandbox.execute("def multiply_by_x(y): return x * y")
    # If locals and globals are different, multiply_by_x will look in globals for x.
    # We should see if our current implementation handles this.
    result = sandbox.execute("print(multiply_by_x(10))")
    if result["error"]:
        print(f"Error encountered: {result['error']}")
    assert result["error"] is None
    assert result["stdout"].strip() == "50"

def test_sandbox_stderr_capture():
    sandbox = Sandbox()
    # Using sys.stderr directly might be tricky depending on implementation, 
    # but let's see if we can capture it.
    result = sandbox.execute("import sys; print('error message', file=sys.stderr)")
    assert result["stderr"].strip() == "error message"
    assert result["error"] is None

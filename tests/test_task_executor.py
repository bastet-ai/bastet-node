"""Tests for task executor"""

from bastet_node.task_executor import TaskExecutor


def test_execute_command():
    """Test command execution"""
    executor = TaskExecutor()
    
    task = {
        "id": "test-1",
        "type": "command",
        "command": "echo 'Hello, World!'"
    }
    
    result = executor.execute(task)
    
    assert result["success"] is True
    assert "Hello, World!" in result["stdout"]
    assert result["return_code"] == 0


def test_execute_command_failure():
    """Test command execution failure"""
    executor = TaskExecutor()
    
    task = {
        "id": "test-2",
        "type": "command",
        "command": "exit 1"
    }
    
    result = executor.execute(task)
    
    assert result["success"] is False
    assert result["return_code"] == 1


def test_execute_scan():
    """Test scan execution"""
    executor = TaskExecutor()
    
    task = {
        "id": "test-3",
        "type": "scan",
        "scan_type": "port",
        "target": "localhost"
    }
    
    result = executor.execute(task)
    
    assert result["success"] is True
    assert result["scan_type"] == "port"
    assert result["target"] == "localhost"


def test_execute_test():
    """Test security test execution"""
    executor = TaskExecutor()
    
    task = {
        "id": "test-4",
        "type": "test",
        "test_name": "sql_injection",
        "parameters": {"url": "http://example.com"}
    }
    
    result = executor.execute(task)
    
    assert result["success"] is True
    assert result["test_name"] == "sql_injection"


def test_unknown_task_type():
    """Test handling of unknown task type"""
    executor = TaskExecutor()
    
    task = {
        "id": "test-5",
        "type": "unknown"
    }
    
    result = executor.execute(task)
    
    assert result["success"] is False
    assert "Unknown task type" in result["error"]

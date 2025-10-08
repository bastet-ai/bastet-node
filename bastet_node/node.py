"""
Main Bastet Node implementation
"""

import logging
import time
import uuid
import signal
import sys
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .config import Config
from .logger import setup_logger
from .client import BastetClient
from .task_executor import TaskExecutor


class BastetNode:
    """Main node for running security tests and reporting to console server"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Bastet Node
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = Config(config_path)
        
        # Setup logging
        self.logger = setup_logger(
            level=self.config.get("logging.level", "INFO"),
            log_file=self.config.get("logging.file"),
            max_size_mb=self.config.get("logging.max_size_mb", 10),
            backup_count=self.config.get("logging.backup_count", 5)
        )
        
        # Generate or load node ID
        self.node_id = self.config.get("node.id") or str(uuid.uuid4())
        self.node_name = self.config.get("node.name", "bastet-node")
        
        # Initialize client
        self.client = BastetClient(
            server_url=self.config.get("server.url"),
            api_key=self.config.get("authentication.api_key"),
            bearer_token=self.config.get("authentication.bearer_token"),
            timeout=self.config.get("server.timeout", 30),
            verify_ssl=self.config.get("security.verify_ssl", True),
            ca_cert=self.config.get("security.ca_cert")
        )
        
        # Initialize task executor
        self.executor = TaskExecutor()
        
        # Thread pool for concurrent task execution
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.config.get("node.max_concurrent_tasks", 5)
        )
        
        # Running flag
        self.running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info(f"Bastet Node initialized: {self.node_id}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def start(self):
        """Start the node and begin check-in loop"""
        self.logger.info("Starting Bastet Node")
        self.running = True
        
        checkin_interval = self.config.get("node.checkin_interval", 60)
        
        while self.running:
            try:
                # Perform check-in
                self._checkin()
                
                # Wait for next check-in interval
                time.sleep(checkin_interval)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(checkin_interval)
    
    def stop(self):
        """Stop the node"""
        self.logger.info("Stopping Bastet Node")
        self.running = False
        self.thread_pool.shutdown(wait=True)
    
    def _checkin(self):
        """Perform check-in with console server"""
        self.logger.debug("Performing check-in")
        
        # Get metadata about this node
        metadata = {
            "version": "1.0.0",
            "capabilities": ["command", "scan", "test"]
        }
        
        # Check in with server
        response = self.client.checkin(
            node_id=self.node_id,
            node_name=self.node_name,
            status="active",
            metadata=metadata
        )
        
        # Process received tasks
        tasks = response.get("tasks", [])
        if tasks:
            self.logger.info(f"Received {len(tasks)} tasks")
            self._process_tasks(tasks)
        else:
            self.logger.debug("No tasks received")
    
    def _process_tasks(self, tasks):
        """
        Process tasks received from server
        
        Args:
            tasks: List of tasks to execute
        """
        # Submit tasks to thread pool
        futures = {}
        for task in tasks:
            future = self.thread_pool.submit(self._execute_task, task)
            futures[future] = task
        
        # Wait for tasks to complete and submit results
        for future in as_completed(futures):
            task = futures[future]
            try:
                result = future.result()
                self._submit_result(task, result)
            except Exception as e:
                self.logger.error(f"Task {task.get('id')} raised exception: {e}")
                self._submit_result(task, {
                    "success": False,
                    "error": str(e)
                })
    
    def _execute_task(self, task):
        """
        Execute a single task
        
        Args:
            task: Task to execute
            
        Returns:
            Task execution result
        """
        task_id = task.get("id", "unknown")
        self.logger.info(f"Executing task: {task_id}")
        
        result = self.executor.execute(task)
        return result
    
    def _submit_result(self, task, result):
        """
        Submit task result to console server
        
        Args:
            task: Original task
            result: Task execution result
        """
        task_id = task.get("id", "unknown")
        
        status = "completed" if result.get("success") else "failed"
        error = result.get("error")
        
        success = self.client.submit_results(
            node_id=self.node_id,
            task_id=task_id,
            status=status,
            results=result,
            error=error
        )
        
        if not success:
            self.logger.warning(f"Failed to submit results for task {task_id}")

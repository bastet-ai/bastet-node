"""
Client for communicating with Bastet console server
"""

import requests
import logging
from typing import Dict, Any, Optional, List


class BastetClient:
    """Client for Bastet console server communication"""
    
    def __init__(
        self,
        server_url: str,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        timeout: int = 30,
        verify_ssl: bool = True,
        ca_cert: Optional[str] = None
    ):
        """
        Initialize Bastet client
        
        Args:
            server_url: URL of the console server
            api_key: API key for authentication
            bearer_token: Bearer token for authentication
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            ca_cert: Path to custom CA certificate
        """
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.bearer_token = bearer_token
        self.timeout = timeout
        self.verify_ssl = ca_cert if ca_cert else verify_ssl
        self.logger = logging.getLogger("bastet-node.client")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Bastet-Node/1.0.0"
        }
        
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        elif self.api_key:
            headers["X-API-Key"] = self.api_key
        
        return headers
    
    def checkin(
        self,
        node_id: str,
        node_name: str,
        status: str = "active",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check in with console server
        
        Args:
            node_id: Node identifier
            node_name: Node name
            status: Node status
            metadata: Additional metadata
            
        Returns:
            Server response with tasks to execute
        """
        endpoint = f"{self.server_url}/api/v1/node/checkin"
        
        payload = {
            "node_id": node_id,
            "node_name": node_name,
            "status": status,
            "metadata": metadata or {}
        }
        
        try:
            self.logger.debug(f"Checking in to {endpoint}")
            response = requests.post(
                endpoint,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f"Check-in successful. Received {len(data.get('tasks', []))} tasks")
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Check-in failed: {e}")
            return {"tasks": [], "error": str(e)}
    
    def submit_results(
        self,
        node_id: str,
        task_id: str,
        status: str,
        results: Dict[str, Any],
        error: Optional[str] = None
    ) -> bool:
        """
        Submit task results to console server
        
        Args:
            node_id: Node identifier
            task_id: Task identifier
            status: Task status (completed, failed, etc.)
            results: Task results
            error: Error message if task failed
            
        Returns:
            True if submission successful
        """
        endpoint = f"{self.server_url}/api/v1/node/results"
        
        payload = {
            "node_id": node_id,
            "task_id": task_id,
            "status": status,
            "results": results,
            "error": error
        }
        
        try:
            self.logger.debug(f"Submitting results for task {task_id}")
            response = requests.post(
                endpoint,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            
            self.logger.info(f"Results submitted successfully for task {task_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to submit results for task {task_id}: {e}")
            return False

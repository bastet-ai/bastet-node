#!/usr/bin/env python3
"""
Example simulation of Bastet console server for testing purposes
This is NOT part of the production code - just for demonstration
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock-server")


class BastetMockHandler(BaseHTTPRequestHandler):
    """Mock handler for Bastet console server API"""
    
    def log_message(self, format, *args):
        """Override to use logger"""
        logger.info("%s - %s" % (self.address_string(), format % args))
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body) if body else {}
            
            if self.path == '/api/v1/node/checkin':
                self._handle_checkin(data)
            elif self.path == '/api/v1/node/results':
                self._handle_results(data)
            else:
                self._send_error(404, "Endpoint not found")
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self._send_error(500, str(e))
    
    def _handle_checkin(self, data):
        """Handle node check-in"""
        node_id = data.get('node_id')
        node_name = data.get('node_name')
        status = data.get('status')
        
        logger.info(f"Check-in from node: {node_name} ({node_id}) - Status: {status}")
        
        # Return sample tasks
        response = {
            "tasks": [
                {
                    "id": "task-001",
                    "type": "command",
                    "command": "echo 'Hello from mock server!'",
                    "timeout": 30
                },
                {
                    "id": "task-002",
                    "type": "scan",
                    "scan_type": "vulnerability",
                    "target": "localhost"
                }
            ]
        }
        
        self._send_json_response(200, response)
    
    def _handle_results(self, data):
        """Handle task results submission"""
        task_id = data.get('task_id')
        status = data.get('status')
        node_id = data.get('node_id')
        
        logger.info(f"Results from node {node_id} for task {task_id}: {status}")
        
        # Acknowledge receipt
        response = {"status": "received", "task_id": task_id}
        self._send_json_response(200, response)
    
    def _send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error(self, status_code, message):
        """Send error response"""
        self._send_json_response(status_code, {"error": message})


def run_mock_server(port=8000):
    """Run mock console server"""
    server = HTTPServer(('localhost', port), BastetMockHandler)
    logger.info(f"Mock Bastet console server running on http://localhost:{port}")
    logger.info("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\nShutting down mock server...")
        server.shutdown()


if __name__ == '__main__':
    run_mock_server()

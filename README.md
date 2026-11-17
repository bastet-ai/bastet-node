# bastet-node

Tool runner for the Bastet security scanning ecosystem. The command-line node runs in Python and connects to the Bastet console server, which hands down security-related tasks to perform. It then hands scan results back to the console server. The node checks in at regular intervals to report any new information or receive new commands for tools to run.

## Features

- **Console Server Integration**: Connects to Bastet console server for task management
- **Periodic Check-ins**: Regular status reporting and task retrieval
- **Task Execution Framework**: Supports multiple types of security tests
  - Command execution
  - Security scans
  - Security tests
- **Result Reporting**: Automatic submission of scan results to console server
- **Concurrent Execution**: Run multiple tasks in parallel
- **Flexible Configuration**: YAML-based config with environment variable support
- **Comprehensive Logging**: Console and file-based logging with rotation

## Installation

### From Source

```bash
git clone https://github.com/bastet-ai/bastet-node.git
cd bastet-node
pip install -r requirements.txt
pip install -e .
```

### Using pip

```bash
pip install bastet-node
```

## Configuration

Create a configuration file by copying the example:

```bash
cp config.yaml.example config.yaml
```

Edit `config.yaml` with your settings:

```yaml
server:
  url: "https://console.bastet.example.com"
  timeout: 30

node:
  name: "bastet-node-1"
  checkin_interval: 60
  max_concurrent_tasks: 5

authentication:
  api_key: "your-api-key-here"

logging:
  level: "INFO"
  file: "logs/bastet-node.log"
```

### Environment Variables

Configuration can also be provided via environment variables:

- `BASTET_SERVER_URL`: Console server URL
- `BASTET_NODE_ID`: Node unique identifier
- `BASTET_NODE_NAME`: Node name
- `BASTET_CHECKIN_INTERVAL`: Check-in interval in seconds
- `BASTET_API_KEY`: API key for authentication
- `BASTET_BEARER_TOKEN`: Bearer token for authentication
- `BASTET_LOG_LEVEL`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `BASTET_LOG_FILE`: Path to log file
- `BASTET_VERIFY_SSL`: Verify SSL certificates (true/false)
- `BASTET_CA_CERT`: Path to custom CA certificate

## Usage

### Basic Usage

```bash
bastet-node
```

### With Custom Configuration

```bash
bastet-node --config /path/to/config.yaml
```

### Show Version

```bash
bastet-node --version
```

### Running as Python Module

```bash
python -m bastet_node
```

## Architecture

### Components

1. **Node**: Main orchestrator that manages the check-in loop and task processing
2. **Client**: HTTP client for communicating with the console server
3. **Task Executor**: Executes security testing tasks
4. **Config Manager**: Handles configuration from files and environment
5. **Logger**: Provides structured logging with rotation

### Task Flow

1. Node checks in with console server at regular intervals
2. Server responds with tasks to execute
3. Node executes tasks concurrently using thread pool
4. Results are submitted back to console server
5. Process repeats at next check-in interval

### Task Types

- **command**: Execute shell commands
- **scan**: Run security scans on targets
- **test**: Execute security tests with parameters

## API

### Check-in Request

```json
{
  "node_id": "uuid",
  "node_name": "bastet-node-1",
  "status": "active",
  "metadata": {
    "version": "1.0.0",
    "capabilities": ["command", "scan", "test"]
  }
}
```

### Check-in Response

```json
{
  "tasks": [
    {
      "id": "task-uuid",
      "type": "command",
      "command": "nmap -sV target.example.com",
      "timeout": 300
    }
  ]
}
```

### Results Submission

```json
{
  "node_id": "uuid",
  "task_id": "task-uuid",
  "status": "completed",
  "results": {
    "success": true,
    "stdout": "...",
    "execution_time": 12.5,
    "timestamp": "2024-01-01T12:00:00"
  }
}
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

```bash
black bastet_node/
flake8 bastet_node/
```

## Security Considerations

- Store sensitive credentials in environment variables or secure configuration files
- Use SSL/TLS for all communications with console server
- Verify SSL certificates in production environments
- Limit task execution permissions appropriately
- Review task definitions before execution in production

## License

Copyright (c) 2024 Bastet AI.

Original Bastet project code and documentation are licensed under the [Apache License 2.0](LICENSE). Third-party dependencies, container images, submodules, imported program data, and other third-party materials retain their respective licenses and notices; they are not relicensed by this grant.

Versions previously distributed under MIT remain available under that grant; this change does not revoke earlier permissions.

## Support

For issues and questions, please open an issue on GitHub:
https://github.com/bastet-ai/bastet-node/issues

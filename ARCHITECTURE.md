# Bastet Node Architecture

## Overview

Bastet Node is a Python-based command-line tool that acts as a distributed agent for security testing. It connects to a central Bastet console server, receives security testing tasks, executes them, and reports results back.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Bastet Console Server                     │
│                  (Central Command & Control)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ REST API (HTTPS)
                         │ - Check-ins
                         │ - Task Assignment
                         │ - Result Collection
                         │
        ┌────────────────┴────────────────┐
        │                                  │
        ▼                                  ▼
┌───────────────┐                  ┌───────────────┐
│ Bastet Node 1 │                  │ Bastet Node 2 │
├───────────────┤                  ├───────────────┤
│  ┌─────────┐  │                  │  ┌─────────┐  │
│  │  Node   │  │                  │  │  Node   │  │
│  │Manager  │  │                  │  │Manager  │  │
│  └────┬────┘  │                  │  └────┬────┘  │
│       │       │                  │       │       │
│  ┌────▼────┐  │                  │  ┌────▼────┐  │
│  │ Client  │  │                  │  │ Client  │  │
│  └─────────┘  │                  │  └─────────┘  │
│       │       │                  │       │       │
│  ┌────▼────┐  │                  │  ┌────▼────┐  │
│  │  Task   │  │                  │  │  Task   │  │
│  │Executor │  │                  │  │Executor │  │
│  └─────────┘  │                  │  └─────────┘  │
│       │       │                  │       │       │
│  ┌────▼────┐  │                  │  ┌────▼────┐  │
│  │Security │  │                  │  │Security │  │
│  │  Tools  │  │                  │  │  Tools  │  │
│  └─────────┘  │                  │  └─────────┘  │
└───────────────┘                  └───────────────┘
```

## Component Architecture

### 1. Node Manager (`node.py`)
- **Main orchestrator** for the Bastet Node
- Manages the check-in loop
- Coordinates task execution
- Handles graceful shutdown

**Key Responsibilities:**
- Initialize all components
- Perform periodic check-ins with console server
- Distribute tasks to thread pool
- Manage concurrent task execution
- Handle signals (SIGINT, SIGTERM)

### 2. Client (`client.py`)
- **HTTP/HTTPS client** for console server communication
- Implements REST API calls
- Handles authentication

**Key Methods:**
- `checkin()` - Check in with server and receive tasks
- `submit_results()` - Submit task execution results

**Features:**
- API key and bearer token authentication
- SSL/TLS support with custom CA certificates
- Configurable timeouts
- Error handling and retry logic

### 3. Task Executor (`task_executor.py`)
- **Executes security testing tasks**
- Supports multiple task types
- Tracks execution metrics

**Task Types:**
- **Command**: Execute shell commands
- **Scan**: Run security scans (port scans, vulnerability scans)
- **Test**: Execute security tests (SQL injection, XSS, etc.)

**Features:**
- Timeout handling
- Error capture and reporting
- Execution time tracking
- Timestamp recording

### 4. Configuration Manager (`config.py`)
- **Loads and manages configuration**
- Supports multiple configuration sources
- Provides easy access to settings

**Configuration Sources (in priority order):**
1. Environment variables
2. `config.local.yaml` (local overrides)
3. `config.yaml` (main configuration)
4. Default values

**Key Settings:**
- Server connection details
- Node identification
- Check-in interval
- Authentication credentials
- Logging configuration
- Security settings

### 5. Logger (`logger.py`)
- **Structured logging infrastructure**
- Console and file output
- Log rotation

**Features:**
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Rotating file handler with size limits
- Customizable format
- Console and file output

## Data Flow

### Check-in Flow

```
1. Node Manager initiates check-in
   ↓
2. Client sends check-in request to server
   - Node ID, name, status, metadata
   ↓
3. Server responds with tasks
   ↓
4. Node Manager receives tasks
   ↓
5. Tasks submitted to thread pool
   ↓
6. Task Executor runs each task
   ↓
7. Results collected
   ↓
8. Client submits results to server
   ↓
9. Wait for next check-in interval
   ↓
10. Repeat from step 1
```

### Task Execution Flow

```
Task Received
   ↓
Parse Task Type
   ↓
   ├─ Command ──> Execute shell command
   │              ├─ Capture stdout/stderr
   │              ├─ Record return code
   │              └─ Handle timeout
   │
   ├─ Scan ────> Run security scan
   │              ├─ Initialize scanner
   │              ├─ Scan target
   │              └─ Collect findings
   │
   └─ Test ────> Run security test
                  ├─ Configure test
                  ├─ Execute test
                  └─ Record results
   ↓
Collect Metadata
   - Execution time
   - Timestamp
   - Success/failure
   ↓
Return Results
```

## Security Considerations

### Authentication
- API key or bearer token required
- Credentials stored in configuration (not in code)
- Support for environment variables

### Communication
- HTTPS/TLS for server communication
- SSL certificate verification (configurable)
- Custom CA certificate support

### Task Execution
- Timeout limits to prevent runaway processes
- Error handling and isolation
- Execution in separate threads
- Resource limits (configurable)

### Logging
- Sensitive data filtering
- Secure log storage
- Log rotation to prevent disk exhaustion

## Scalability

### Horizontal Scaling
- Deploy multiple nodes
- Each node operates independently
- Server coordinates task distribution

### Concurrent Execution
- Thread pool for parallel task execution
- Configurable worker count
- Task isolation

### Resource Management
- Configurable concurrent task limit
- Timeout controls
- Memory-efficient task processing

## Configuration

### Minimal Configuration

```yaml
server:
  url: "https://console.example.com"

authentication:
  api_key: "your-api-key"
```

### Full Configuration

```yaml
server:
  url: "https://console.example.com"
  checkin_endpoint: "/api/v1/node/checkin"
  results_endpoint: "/api/v1/node/results"
  timeout: 30

node:
  id: "unique-node-id"
  name: "production-node-1"
  checkin_interval: 60
  max_concurrent_tasks: 5

authentication:
  api_key: "your-api-key"

logging:
  level: "INFO"
  file: "logs/bastet-node.log"
  max_size_mb: 10
  backup_count: 5

security:
  verify_ssl: true
  ca_cert: "/path/to/ca.crt"
```

## Extension Points

### Custom Task Types

Add new task types by extending `TaskExecutor`:

```python
def _execute_custom_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
    """Execute custom task type"""
    # Implementation here
    return {"success": True, "results": {}}
```

### Custom Authentication

Extend `BastetClient` to support additional authentication methods:

```python
def _get_headers(self) -> Dict[str, str]:
    headers = super()._get_headers()
    # Add custom authentication
    return headers
```

### Integration with Security Tools

The task executor can be extended to integrate with various security tools:
- Nmap for network scanning
- OWASP ZAP for web application scanning
- Burp Suite for penetration testing
- Custom security scripts

## Monitoring and Observability

### Metrics
- Check-in frequency
- Task execution time
- Success/failure rates
- Resource utilization

### Logging
- All operations logged
- Structured log format
- Multiple log levels
- Searchable logs

### Health Checks
- Regular check-ins indicate node health
- Task execution success rates
- Error rate monitoring

## Deployment

### Installation Methods

1. **From Source:**
   ```bash
   git clone https://github.com/bastet-ai/bastet-node.git
   cd bastet-node
   pip install -e .
   ```

2. **From PyPI:**
   ```bash
   pip install bastet-node
   ```

### Running as Service

**Systemd Unit File:**

```ini
[Unit]
Description=Bastet Node Security Scanner
After=network.target

[Service]
Type=simple
User=bastet
WorkingDirectory=/opt/bastet-node
Environment="BASTET_SERVER_URL=https://console.example.com"
Environment="BASTET_API_KEY=your-api-key"
ExecStart=/usr/local/bin/bastet-node --config /etc/bastet-node/config.yaml
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY bastet_node/ ./bastet_node/
COPY setup.py .
RUN pip install -e .

CMD ["bastet-node"]
```

## Testing

### Unit Tests
- Configuration management
- Task execution
- Client communication

### Integration Tests
- Mock server for end-to-end testing
- Task flow validation
- Error handling scenarios

### Running Tests

```bash
pytest tests/ -v
```

## Future Enhancements

### Planned Features
- Web UI for node management
- Advanced scheduling capabilities
- Result caching and offline mode
- Enhanced security tool integrations
- Distributed task coordination
- Real-time progress streaming
- Task prioritization
- Resource quota management

### Roadmap
1. **Phase 1**: Core functionality (✓ Complete)
2. **Phase 2**: Enhanced security tool integration
3. **Phase 3**: Advanced scheduling and orchestration
4. **Phase 4**: Web UI and monitoring dashboard
5. **Phase 5**: Enterprise features (SSO, RBAC, audit logs)

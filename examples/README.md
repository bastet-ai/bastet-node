# Bastet Node Examples

This directory contains example scripts for testing and demonstrating the Bastet Node.

## Mock Server

`simulate_server.py` - A simple mock implementation of the Bastet console server for local testing.

### Running the Mock Server

```bash
python examples/simulate_server.py
```

This will start a server on `http://localhost:8000` that simulates the console server API.

### Testing with Mock Server

1. In one terminal, start the mock server:
   ```bash
   python examples/simulate_server.py
   ```

2. In another terminal, run the Bastet node:
   ```bash
   bastet-node --config config.yaml
   ```

The node will connect to the mock server, receive tasks, and submit results.

## Notes

These examples are for testing and demonstration purposes only and should not be used in production.

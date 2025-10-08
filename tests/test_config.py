"""Tests for configuration management"""

import os
import tempfile
import yaml
from bastet_node.config import Config


def test_default_config():
    """Test default configuration"""
    config = Config(config_path="/nonexistent/path.yaml")
    
    assert config.get("server.url") is not None
    assert config.get("node.checkin_interval") == 60
    assert config.get("logging.level") == "INFO"


def test_config_from_file():
    """Test loading configuration from file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        test_config = {
            "server": {
                "url": "https://test.example.com"
            },
            "node": {
                "name": "test-node",
                "checkin_interval": 30
            }
        }
        yaml.dump(test_config, f)
        config_path = f.name
    
    try:
        config = Config(config_path=config_path)
        
        assert config.get("server.url") == "https://test.example.com"
        assert config.get("node.name") == "test-node"
        assert config.get("node.checkin_interval") == 30
        
    finally:
        os.unlink(config_path)


def test_config_merge():
    """Test configuration merging"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        test_config = {
            "server": {
                "url": "https://test.example.com"
            }
        }
        yaml.dump(test_config, f)
        config_path = f.name
    
    try:
        config = Config(config_path=config_path)
        
        # Should have custom server URL
        assert config.get("server.url") == "https://test.example.com"
        # Should have default checkin interval
        assert config.get("node.checkin_interval") == 60
        
    finally:
        os.unlink(config_path)


def test_config_get_with_default():
    """Test getting config values with defaults"""
    config = Config(config_path="/nonexistent/path.yaml")
    
    assert config.get("nonexistent.key", "default") == "default"
    assert config.get("server.url", "default") != "default"

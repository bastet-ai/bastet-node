"""
Configuration management for Bastet Node
"""

import os
import yaml
from typing import Dict, Any


class Config:
    """Configuration manager for Bastet Node"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or self._find_config()
        self.config = self._load_config()
    
    def _find_config(self) -> str:
        """Find configuration file in standard locations"""
        possible_paths = [
            "config.local.yaml",
            "config.yaml",
            "/etc/bastet-node/config.yaml",
            os.path.expanduser("~/.bastet-node/config.yaml")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Return default if none found
        return "config.yaml"
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            # Return default configuration
            return self._default_config()
        
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Merge with defaults
        default = self._default_config()
        return self._merge_configs(default, config)
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "server": {
                "url": os.getenv("BASTET_SERVER_URL", "http://localhost:8000"),
                "checkin_endpoint": "/api/v1/node/checkin",
                "results_endpoint": "/api/v1/node/results",
                "timeout": 30
            },
            "node": {
                "id": os.getenv("BASTET_NODE_ID", ""),
                "name": os.getenv("BASTET_NODE_NAME", "bastet-node"),
                "checkin_interval": int(os.getenv("BASTET_CHECKIN_INTERVAL", "60")),
                "max_concurrent_tasks": 5
            },
            "authentication": {
                "api_key": os.getenv("BASTET_API_KEY", ""),
                "bearer_token": os.getenv("BASTET_BEARER_TOKEN", "")
            },
            "logging": {
                "level": os.getenv("BASTET_LOG_LEVEL", "INFO"),
                "file": os.getenv("BASTET_LOG_FILE", ""),
                "max_size_mb": 10,
                "backup_count": 5
            },
            "security": {
                "verify_ssl": os.getenv("BASTET_VERIFY_SSL", "true").lower() == "true",
                "ca_cert": os.getenv("BASTET_CA_CERT", "")
            }
        }
    
    def _merge_configs(self, default: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two configuration dictionaries"""
        if override is None:
            return default
            
        result = default.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated path
        
        Args:
            path: Dot-separated configuration path (e.g., "server.url")
            default: Default value if path not found
            
        Returns:
            Configuration value
        """
        keys = path.split(".")
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value

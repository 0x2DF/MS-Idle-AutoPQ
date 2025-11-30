# config_loader.py
import yaml
from pathlib import Path

class ConfigLoader:
    """Loads and provides access to application configuration."""
    
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self._config = None
    
    def load(self):
        """Load configuration from file."""
        if not Path(self.config_path).exists():
            self._config = {}
            return self._config
        
        with open(self.config_path, "r") as f:
            self._config = yaml.safe_load(f) or {}
        return self._config
    
    def get(self, key, default=None):
        """Get a configuration value by key."""
        if self._config is None:
            self.load()
        return self._config.get(key, default)
    
    @property
    def config(self):
        """Get the full configuration dictionary."""
        if self._config is None:
            self.load()
        return self._config

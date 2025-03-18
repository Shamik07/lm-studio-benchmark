"""
Configuration and constants for the LM Studio Benchmark GUI.
"""

import json
from pathlib import Path

# Default paths
CONFIG_DIR = Path.home() / ".lm-studio-benchmark"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_OUTPUT_DIR = Path("benchmark_results")
DEFAULT_LEADERBOARD_DIR = DEFAULT_OUTPUT_DIR / "leaderboard"

# Ensure config directory exists
CONFIG_DIR.mkdir(exist_ok=True, parents=True)

# Default configuration
DEFAULT_CONFIG = {
    "endpoint": "http://localhost:1234/v1/chat/completions",
    "timeout": 120,
    "output_dir": str(DEFAULT_OUTPUT_DIR),
    "leaderboard_dir": str(DEFAULT_LEADERBOARD_DIR),
    "execute_code": True,
    "monitor_resources": True,
    "theme": "dark",
}

# Benchmark categories
CATEGORIES = [
    "syntax", 
    "algorithms", 
    "data_structures", 
    "debugging", 
    "api_usage", 
    "web_dev", 
    "concurrency", 
    "testing",
    "error_handling", 
    "oop"
]

# Difficulty levels
DIFFICULTIES = ["easy", "medium", "hard"]

# Programming languages
LANGUAGES = [
    "python", 
    "javascript", 
    "typescript", 
    "java", 
    "cpp", 
    "csharp", 
    "php", 
    "go", 
    "rust", 
    "swift", 
    "kotlin", 
    "dart"
]

# Performance metrics
PERFORMANCE_METRICS = [
    "test_pass_rate",
    "api_success_rate",
    "execution_success_rate",
    "avg_response_time"
]

# Resource metrics
RESOURCE_METRICS = [
    "memory_peak_gb",
    "memory_avg_gb",
    "cpu_max_percent",
    "cpu_avg_percent",
    "gpu_avg_utilization",
    "gpu_max_utilization"
]

def load_config():
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except (json.JSONDecodeError, OSError):
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
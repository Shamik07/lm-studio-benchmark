#!/usr/bin/env python3
"""
Resource Monitor for LM Studio Benchmark
Monitor GPU, CPU, and memory usage during model inference
"""

import time
import psutil
import threading
import platform
import json
from pathlib import Path
import numpy as np
from typing import Dict, List, Any, Optional

# Conditional import for GPU monitoring
try:
    if platform.system() == 'Darwin' and platform.processor() == 'arm':
        # For Apple Silicon (M1/M2/M3)
        import subprocess
    else:
        # For NVIDIA GPUs
        import pynvml
except ImportError:
    pass

class ResourceMonitor:
    """
    Monitor system resources during benchmark runs
    """
    
    def __init__(self, sample_interval: float = 0.5):
        """
        Initialize the resource monitor
        
        Args:
            sample_interval: Time between samples in seconds
        """
        self.sample_interval = sample_interval
        self.monitoring = False
        self.samples = []
        self.monitoring_thread = None
        self.start_time = 0
        
        # Initialize GPU monitoring based on platform
        self.gpu_available = False
        self.is_apple_silicon = platform.system() == 'Darwin' and platform.processor() == 'arm'
        
        if self.is_apple_silicon:
            self.gpu_available = True
        else:
            try:
                import pynvml
                pynvml.nvmlInit()
                self.gpu_available = True
                self.pynvml = pynvml
                self.device_count = pynvml.nvmlDeviceGetCount()
            except (ImportError, AttributeError):
                self.gpu_available = False
    
    def start_monitoring(self):
        """Start monitoring resources"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.samples = []
        self.start_time = time.time()
        
        # Start monitoring in a separate thread
        self.monitoring_thread = threading.Thread(target=self._monitor_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """
        Stop monitoring and return results
        
        Returns:
            Dictionary with resource usage statistics
        """
        if not self.monitoring:
            return {}
        
        self.monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        
        # Calculate statistics
        return self._calculate_stats()
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            sample = self._collect_sample()
            self.samples.append(sample)
            time.sleep(self.sample_interval)
    
    def _collect_sample(self) -> Dict[str, Any]:
        """
        Collect a single resource usage sample
        
        Returns:
            Dictionary with resource usage metrics
        """
        sample = {
            "timestamp": time.time() - self.start_time,
            "cpu": {
                "percent": psutil.cpu_percent(interval=None),
                "per_cpu": psutil.cpu_percent(interval=None, percpu=True)
            },
            "memory": {
                "used_gb": psutil.virtual_memory().used / (1024**3),
                "available_gb": psutil.virtual_memory().available / (1024**3),
                "percent": psutil.virtual_memory().percent
            },
            "gpu": self._get_gpu_metrics()
        }
        return sample
    
    def _get_gpu_metrics(self) -> Dict[str, Any]:
        """
        Get GPU metrics depending on the platform
        
        Returns:
            Dictionary with GPU metrics
        """
        if not self.gpu_available:
            return {"available": False}
        
        if self.is_apple_silicon:
            return self._get_apple_silicon_metrics()
        else:
            return self._get_nvidia_metrics()
    
    def _get_apple_silicon_metrics(self) -> Dict[str, Any]:
        """
        Get Apple Silicon GPU metrics using powermetrics
        
        Returns:
            Dictionary with GPU metrics
        """
        try:
            # Use powermetrics for a quick sampling (needs sudo)
            # This might require user to enter password once
            cmd = ["sudo", "powermetrics", "-n", "1", "-i", "100", "--samplers", "gpu_power", "--format", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                gpu_metrics = {
                    "available": True,
                    "utilization": data.get("gpu", {}).get("gpu_utilization", 0),
                    "power_w": data.get("gpu", {}).get("gpu_power", 0) / 1000  # Convert mW to W
                }
                return gpu_metrics
        except (subprocess.SubprocessError, json.JSONDecodeError, KeyError):
            pass
        
        # Fallback to simpler metrics if powermetrics fails
        try:
            # Try to get GPU utilization from Activity Monitor data
            cmd = ["ps", "-eo", "%cpu,command"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Crude estimation of GPU usage based on processes
            gpu_processes = ["WindowServer", "MTLCompilerService", "AMDGPUServicesService"]
            gpu_usage = 0
            
            for line in result.stdout.splitlines():
                parts = line.strip().split(None, 1)
                if len(parts) == 2:
                    try:
                        cpu = float(parts[0])
                        cmd = parts[1]
                        if any(p in cmd for p in gpu_processes):
                            gpu_usage += cpu
                    except ValueError:
                        continue
            
            return {
                "available": True,
                "utilization": min(gpu_usage / 100, 100),  # Crude approximation
                "estimated": True
            }
        except Exception:
            return {"available": True, "error": "Could not collect metrics"}
    
    def _get_nvidia_metrics(self) -> Dict[str, Any]:
        """
        Get NVIDIA GPU metrics using pynvml
        
        Returns:
            Dictionary with GPU metrics
        """
        try:
            metrics = {"available": True, "devices": []}
            
            for i in range(self.device_count):
                handle = self.pynvml.nvmlDeviceGetHandleByIndex(i)
                util = self.pynvml.nvmlDeviceGetUtilizationRates(handle)
                memory = self.pynvml.nvmlDeviceGetMemoryInfo(handle)
                temperature = self.pynvml.nvmlDeviceGetTemperature(handle, self.pynvml.NVML_TEMPERATURE_GPU)
                power = self.pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert from mW to W
                
                device_metrics = {
                    "id": i,
                    "name": self.pynvml.nvmlDeviceGetName(handle),
                    "utilization": util.gpu,
                    "memory": {
                        "used_gb": memory.used / (1024**3),
                        "total_gb": memory.total / (1024**3),
                        "percent": (memory.used / memory.total) * 100
                    },
                    "temperature_c": temperature,
                    "power_w": power
                }
                metrics["devices"].append(device_metrics)
            
            return metrics
        except Exception as e:
            return {"available": True, "error": str(e)}
    
    def _calculate_stats(self) -> Dict[str, Any]:
        """
        Calculate statistics from collected samples
        
        Returns:
            Dictionary with resource usage statistics
        """
        if not self.samples:
            return {"error": "No samples collected"}
        
        # Calculate CPU statistics
        cpu_percent = [s["cpu"]["percent"] for s in self.samples]
        
        # Calculate memory statistics
        memory_used = [s["memory"]["used_gb"] for s in self.samples]
        memory_percent = [s["memory"]["percent"] for s in self.samples]
        
        # Calculate GPU statistics if available
        gpu_stats = {}
        if self.gpu_available:
            if self.is_apple_silicon:
                gpu_util = []
                for s in self.samples:
                    if "gpu" in s and "utilization" in s["gpu"]:
                        gpu_util.append(s["gpu"]["utilization"])
                
                if gpu_util:
                    gpu_stats = {
                        "utilization": {
                            "mean": np.mean(gpu_util),
                            "max": np.max(gpu_util),
                            "min": np.min(gpu_util),
                            "std": np.std(gpu_util)
                        }
                    }
            else:
                # Process NVIDIA GPU statistics
                device_stats = {}
                for device_idx in range(self.device_count):
                    device_util = []
                    device_memory = []
                    device_power = []
                    
                    for s in self.samples:
                        if "gpu" in s and "devices" in s["gpu"] and len(s["gpu"]["devices"]) > device_idx:
                            device = s["gpu"]["devices"][device_idx]
                            device_util.append(device.get("utilization", 0))
                            device_memory.append(device.get("memory", {}).get("percent", 0))
                            device_power.append(device.get("power_w", 0))
                    
                    if device_util:
                        device_stats[f"device_{device_idx}"] = {
                            "utilization": {
                                "mean": np.mean(device_util),
                                "max": np.max(device_util),
                                "min": np.min(device_util),
                                "std": np.std(device_util)
                            },
                            "memory_percent": {
                                "mean": np.mean(device_memory),
                                "max": np.max(device_memory),
                                "std": np.std(device_memory)
                            },
                            "power_w": {
                                "mean": np.mean(device_power),
                                "max": np.max(device_power),
                                "std": np.std(device_power)
                            }
                        }
                
                gpu_stats = {"devices": device_stats}
        
        # Overall statistics
        return {
            "duration": self.samples[-1]["timestamp"],
            "sample_count": len(self.samples),
            "samples": self.samples,  # Include raw samples
            "cpu": {
                "percent": {
                    "mean": np.mean(cpu_percent),
                    "max": np.max(cpu_percent),
                    "min": np.min(cpu_percent),
                    "std": np.std(cpu_percent)
                }
            },
            "memory": {
                "used_gb": {
                    "mean": np.mean(memory_used),
                    "max": np.max(memory_used),
                    "min": np.min(memory_used),
                    "peak_delta": np.max(memory_used) - memory_used[0]
                },
                "percent": {
                    "mean": np.mean(memory_percent),
                    "max": np.max(memory_percent)
                }
            },
            "gpu": gpu_stats,
            "platform": {
                "system": platform.system(),
                "processor": platform.processor(),
                "python_version": platform.python_version()
            }
        }
    
    def save_results(self, results: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        Save resource monitoring results to a file
        
        Args:
            results: Results from stop_monitoring()
            output_path: Path to save results (optional)
            
        Returns:
            Path to the saved file
        """
        if output_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = f"benchmark_results/resource_usage_{timestamp}.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        
        return str(output_path)
    
    def plot_resource_usage(self, results_file: str, output_path: Optional[str] = None):
        """
        Generate plots of resource usage
        
        Args:
            results_file: Path to results JSON file
            output_path: Path to save the plot (optional)
            
        Returns:
            Path to the saved plot
        """
        import matplotlib.pyplot as plt
        
        with open(results_file, "r") as f:
            results = json.load(f)
        
        # Check if samples are included in the results file
        if "samples" not in results:
            print("Warning: No samples found in the resource file. Cannot generate resource usage plot.")
            return None
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
        
        # Plot timestamps
        timestamps = [s["timestamp"] for s in results["samples"]]
        
        # Plot CPU usage
        cpu_percent = [s["cpu"]["percent"] for s in results["samples"]]
        ax1.plot(timestamps, cpu_percent, 'b-', label='CPU Usage')
        ax1.set_ylabel('CPU Usage (%)')
        ax1.set_title('Resource Usage During Benchmark')
        ax1.grid(True)
        ax1.legend()
        
        # Plot Memory usage
        memory_percent = [s["memory"]["percent"] for s in results["samples"]]
        ax2.plot(timestamps, memory_percent, 'g-', label='Memory Usage')
        ax2.set_ylabel('Memory Usage (%)')
        ax2.grid(True)
        ax2.legend()
        
        # Plot GPU usage if available
        gpu_available = results.get("gpu", {}).get("available", False)
        is_apple_silicon = "system" in results.get("platform", {}) and results["platform"]["system"] == "Darwin" and "processor" in results["platform"] and "apple" in results["platform"]["processor"].lower()
        
        if gpu_available:
            if is_apple_silicon:
                gpu_util = [s["gpu"].get("utilization", 0) for s in results["samples"]]
                ax3.plot(timestamps, gpu_util, 'r-', label='GPU Utilization')
                ax3.set_ylabel('GPU Utilization (%)')
            else:
                # For NVIDIA, plot the first GPU if available
                gpu_utils = []
                for s in results["samples"]:
                    if "gpu" in s and "devices" in s["gpu"] and s["gpu"]["devices"]:
                        gpu_utils.append(s["gpu"]["devices"][0].get("utilization", 0))
                    else:
                        gpu_utils.append(0)
                
                if any(gpu_utils):
                    ax3.plot(timestamps, gpu_utils, 'r-', label='GPU Utilization')
                    ax3.set_ylabel('GPU Utilization (%)')
                else:
                    ax3.text(0.5, 0.5, 'GPU metrics not available', 
                            horizontalalignment='center', verticalalignment='center', transform=ax3.transAxes)
        else:
            ax3.text(0.5, 0.5, 'GPU metrics not available', 
                    horizontalalignment='center', verticalalignment='center', transform=ax3.transAxes)
        
        ax3.grid(True)
        ax3.legend()
        ax3.set_xlabel('Time (seconds)')
        
        plt.tight_layout()
        
        # Save the plot
        if output_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = f"benchmark_results/resource_usage_plot_{timestamp}.png"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        plt.savefig(output_path)
        plt.close()
        
        return str(output_path)
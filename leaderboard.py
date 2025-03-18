#!/usr/bin/env python3
"""
Leaderboard module for LM Studio Coding Benchmark.
Manages the storage, retrieval, and visualization of benchmark results.
"""

import json
import os
import time
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import pandas as pd
from tabulate import tabulate

class Leaderboard:
    """
    Leaderboard class for managing benchmark results and creating visualizations.
    """
    
    def __init__(self, leaderboard_path: Union[str, Path] = "benchmark_results/leaderboard"):
        """
        Initialize the leaderboard.
        
        Args:
            leaderboard_path: Path to the leaderboard directory
        """
        self.leaderboard_path = Path(leaderboard_path)
        self.leaderboard_path.mkdir(exist_ok=True, parents=True)
        
        # Path to the main leaderboard database file
        self.db_path = self.leaderboard_path / "leaderboard_db.json"
        
        # Load or initialize the leaderboard database
        self.db = self._load_db()
    
    def _load_db(self) -> Dict[str, Any]:
        """
        Load the leaderboard database or create a new one if it doesn't exist.
        
        Returns:
            The leaderboard database as a dictionary
        """
        if self.db_path.exists():
            try:
                with open(self.db_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error loading leaderboard database. Creating a new one.")
                return self._initialize_db()
        else:
            return self._initialize_db()
    
    def _initialize_db(self) -> Dict[str, Any]:
        """
        Initialize a new leaderboard database.
        
        Returns:
            A new leaderboard database structure
        """
        db = {
            "version": 1,
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "entries": [],
            "models": {}
        }
        
        # Save the new database
        self._save_db(db)
        
        return db
    
    def _save_db(self, db: Dict[str, Any] = None) -> None:
        """
        Save the leaderboard database to disk.
        
        Args:
            db: The database to save (uses self.db if None)
        """
        if db is None:
            db = self.db
        
        # Update the last_updated timestamp
        db["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.db_path, "w") as f:
            json.dump(db, f, indent=2)
    
    def add_entry(self, 
              analysis_file: Union[str, Path], 
              model_name: str, 
              model_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Add a benchmark result to the leaderboard.
        
        Args:
            analysis_file: Path to the analysis JSON file
            model_name: Name of the model
            model_info: Additional information about the model
            
        Returns:
            The added entry
        """
        # Load the analysis file
        analysis_path = Path(analysis_file)
        if not analysis_path.exists():
            raise FileNotFoundError(f"Analysis file not found: {analysis_file}")
        
        with open(analysis_path, "r") as f:
            analysis = json.load(f)
        
        # Check if there's a resource metrics file
        resource_metrics = None
        resource_path = analysis_path.parent / f"{analysis_path.stem.replace('analysis_', '')}_resources.json"
        if resource_path.exists():
            try:
                with open(resource_path, "r") as f:
                    resource_metrics = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Found resource metrics file but couldn't parse it: {resource_path}")
        
        # Create a new entry
        entry = {
            "id": f"entry_{int(time.time())}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_name": model_name,
            "analysis_file": str(analysis_path),
            "summary": analysis["summary"],
            "title": analysis.get("title", "Unnamed Benchmark")
        }
        
        # Add model info if provided
        if model_info:
            entry["model_info"] = model_info
        
        # Add resource metrics if available
        if resource_metrics:
            entry["resource_metrics"] = {
                "cpu_avg_percent": resource_metrics["cpu"]["percent"]["mean"],
                "cpu_max_percent": resource_metrics["cpu"]["percent"]["max"],
                "memory_avg_gb": resource_metrics["memory"]["used_gb"]["mean"],
                "memory_peak_gb": resource_metrics["memory"]["used_gb"]["max"],
            }
            
            # Add GPU metrics if available
            if resource_metrics.get("gpu"):
                gpu_metrics = resource_metrics["gpu"]
                if "utilization" in gpu_metrics:
                    entry["resource_metrics"]["gpu_avg_utilization"] = gpu_metrics["utilization"]["mean"]
                    entry["resource_metrics"]["gpu_max_utilization"] = gpu_metrics["utilization"]["max"]
                elif "devices" in gpu_metrics:
                    # Just use the first device for now
                    for device_name, device_stats in gpu_metrics["devices"].items():
                        if "utilization" in device_stats:
                            entry["resource_metrics"]["gpu_avg_utilization"] = device_stats["utilization"]["mean"]
                            entry["resource_metrics"]["gpu_max_utilization"] = device_stats["utilization"]["max"]
                        break  # Just use the first device
        
        # Add the entry to the database
        self.db["entries"].append(entry)
        
        # Update or add model in the models dictionary
        if model_name not in self.db["models"]:
            self.db["models"][model_name] = {
                "best_score": entry["summary"]["test_pass_rate"] if "test_pass_rate" in entry["summary"] else entry["summary"].get("api_success_rate", 0),
                "entries": [entry["id"]],
                "last_updated": entry["timestamp"]
            }
        else:
            # Track this entry
            self.db["models"][model_name]["entries"].append(entry["id"])
            self.db["models"][model_name]["last_updated"] = entry["timestamp"]
            
            # Update best score if better
            current_score = entry["summary"]["test_pass_rate"] if "test_pass_rate" in entry["summary"] else entry["summary"].get("api_success_rate", 0)
            if current_score > self.db["models"][model_name]["best_score"]:
                self.db["models"][model_name]["best_score"] = current_score
        
        # Save the updated database
        self._save_db()
        
        return entry
    

    def visualize_resource_metrics(self, 
                              metric: str = "memory_peak_gb",
                              top_n: int = 10,
                              output_path: Union[str, Path] = None) -> str:
        """
        Generate a bar chart visualization of resource metrics across models.
        
        Args:
            metric: The resource metric to visualize (cpu_avg_percent, memory_peak_gb, etc.)
            top_n: Number of top models to include
            output_path: Path to save the visualization (if None, auto-generate)
            
        Returns:
            Path to the saved visualization
        """
        # Get models with resource metrics
        entries_with_metrics = []
        
        for entry in self.db["entries"]:
            if "resource_metrics" in entry and metric in entry["resource_metrics"]:
                entries_with_metrics.append(entry)
        
        if not entries_with_metrics:
            raise ValueError(f"No entries found with resource metric: {metric}")
        
        # Sort entries by the specified metric
        if metric in ["memory_peak_gb", "memory_avg_gb", "cpu_max_percent", "cpu_avg_percent"]:
            # For these metrics, lower is better
            sorted_entries = sorted(entries_with_metrics, key=lambda e: e["resource_metrics"][metric])
        else:
            # For other metrics, like GPU utilization, higher might be better
            sorted_entries = sorted(entries_with_metrics, key=lambda e: e["resource_metrics"][metric], reverse=True)
        
        # Take top N entries
        top_entries = sorted_entries[:top_n]
        
        # Prepare data for the chart
        model_names = []
        metric_values = []
        
        for entry in top_entries:
            model_names.append(f"{entry['model_name']}\n({entry['timestamp'].split()[0]})")
            metric_values.append(entry["resource_metrics"][metric])
        
        # Create the visualization
        plt.figure(figsize=(12, 8))
        
        # Create bars
        bars = plt.bar(model_names, metric_values, color='lightgreen')
        
        # Add value annotations
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f"{height:.2f}" + ("%" if "percent" in metric else " GB" if "gb" in metric.lower() else ""),
                    ha='center', va='bottom')
        
        # Set labels and title
        plt.title(f"Model Comparison by {metric.replace('_', ' ').title()}")
        plt.xlabel("Model")
        
        # Set ylabel based on metric
        if "percent" in metric:
            ylabel = "Percentage (%)"
        elif "gb" in metric.lower():
            ylabel = "Memory (GB)"
        else:
            ylabel = metric.replace("_", " ").title()
        
        plt.ylabel(ylabel)
        plt.xticks(rotation=45, ha="right")
        
        plt.tight_layout()
        
        # Generate output path if not provided
        if output_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = self.leaderboard_path / f"resource_metrics_{metric}_{timestamp}.png"
        else:
            output_path = Path(output_path)
        
        # Save the visualization
        plt.savefig(output_path)
        plt.close()
        
        return str(output_path)
    
    def list_entries(self, 
                     model_name: str = None, 
                     limit: int = None,
                     metric: str = "test_pass_rate",
                     min_date: str = None,
                     max_date: str = None) -> List[Dict[str, Any]]:
        """
        List entries in the leaderboard with optional filtering.
        
        Args:
            model_name: Filter by model name
            limit: Maximum number of entries to return
            metric: The metric to sort by (default: test_pass_rate)
            min_date: Minimum date for filtering (format: YYYY-MM-DD)
            max_date: Maximum date for filtering (format: YYYY-MM-DD)
            
        Returns:
            A list of matching entries
        """
        entries = self.db["entries"].copy()
        
        # Apply model name filter
        if model_name:
            entries = [e for e in entries if e["model_name"] == model_name]
        
        # Apply date filters
        if min_date:
            entries = [e for e in entries if e["timestamp"].split()[0] >= min_date]
        if max_date:
            entries = [e for e in entries if e["timestamp"].split()[0] <= max_date]
        
        # Determine the sort key: first try test_pass_rate, then api_success_rate
        def get_sort_key(entry):
            summary = entry["summary"]
            if metric == "test_pass_rate" and "test_pass_rate" in summary:
                return summary["test_pass_rate"]
            elif metric == "api_success_rate" or (metric == "test_pass_rate" and "test_pass_rate" not in summary):
                return summary.get("api_success_rate", 0)
            elif metric == "execution_success_rate":
                return summary.get("execution_success_rate", 0)
            elif metric == "avg_response_time":
                # For response time, lower is better so we use negative value
                return -summary.get("avg_response_time", float("inf"))
            else:
                # Try to get the specified metric
                return summary.get(metric, 0)
        
        # Sort by the specified metric (descending order)
        sorted_entries = sorted(entries, key=get_sort_key, reverse=True)
        
        # Apply limit
        if limit and limit > 0:
            sorted_entries = sorted_entries[:limit]
        
        return sorted_entries
    
    def list_models(self, 
                    metric: str = "best_score", 
                    limit: int = None) -> List[Dict[str, Any]]:
        """
        List models in the leaderboard.
        
        Args:
            metric: The metric to sort by (default: best_score)
            limit: Maximum number of models to return
            
        Returns:
            A list of models with their stats
        """
        models = []
        
        for name, info in self.db["models"].items():
            # Get the latest entry for this model
            latest_entry_id = info["entries"][-1]
            latest_entry = next((e for e in self.db["entries"] if e["id"] == latest_entry_id), None)
            
            models.append({
                "name": name,
                "best_score": info["best_score"],
                "entry_count": len(info["entries"]),
                "last_updated": info["last_updated"],
                "latest_results": latest_entry["summary"] if latest_entry else None
            })
        
        # Sort by the specified metric
        if metric == "best_score":
            sorted_models = sorted(models, key=lambda m: m["best_score"], reverse=True)
        elif metric == "entry_count":
            sorted_models = sorted(models, key=lambda m: m["entry_count"], reverse=True)
        elif metric == "last_updated":
            sorted_models = sorted(models, key=lambda m: m["last_updated"], reverse=True)
        else:
            # Try to sort by a specific metric in the latest results
            def get_latest_metric(model):
                if model["latest_results"] and metric in model["latest_results"]:
                    return model["latest_results"][metric]
                return 0
            
            sorted_models = sorted(models, key=get_latest_metric, reverse=True)
        
        # Apply limit
        if limit and limit > 0:
            sorted_models = sorted_models[:limit]
        
        return sorted_models
    
    def get_model_history(self, model_name: str) -> List[Dict[str, Any]]:
        """
        Get the benchmark history for a specific model.
        
        Args:
            model_name: The name of the model
            
        Returns:
            A list of benchmark entries for the model in chronological order
        """
        if model_name not in self.db["models"]:
            return []
        
        # Get entry IDs for this model
        entry_ids = self.db["models"][model_name]["entries"]
        
        # Find these entries in the entries list
        entries = [e for e in self.db["entries"] if e["id"] in entry_ids]
        
        # Sort by timestamp
        return sorted(entries, key=lambda e: e["timestamp"])
    
    def delete_entry(self, entry_id: str) -> bool:
        """
        Delete an entry from the leaderboard.
        
        Args:
            entry_id: The ID of the entry to delete
            
        Returns:
            True if the entry was deleted, False otherwise
        """
        # Find the entry
        entry_idx = None
        entry = None
        for i, e in enumerate(self.db["entries"]):
            if e["id"] == entry_id:
                entry_idx = i
                entry = e
                break
        
        if entry_idx is None:
            return False
        
        # Remove the entry
        self.db["entries"].pop(entry_idx)
        
        # Update the models reference
        model_name = entry["model_name"]
        if model_name in self.db["models"]:
            # Remove this entry ID from the model's entries
            self.db["models"][model_name]["entries"] = [
                eid for eid in self.db["models"][model_name]["entries"] 
                if eid != entry_id
            ]
            
            # If no entries left, remove the model
            if not self.db["models"][model_name]["entries"]:
                del self.db["models"][model_name]
            else:
                # Recalculate best score
                best_score = 0
                for eid in self.db["models"][model_name]["entries"]:
                    for e in self.db["entries"]:
                        if e["id"] == eid:
                            score = e["summary"]["test_pass_rate"] if "test_pass_rate" in e["summary"] else e["summary"].get("api_success_rate", 0)
                            best_score = max(best_score, score)
                            break
                
                self.db["models"][model_name]["best_score"] = best_score
        
        # Save the updated database
        self._save_db()
        
        return True
    
    def visualize_leaderboard(self, 
                             metric: str = "test_pass_rate",
                             top_n: int = 10,
                             output_path: Union[str, Path] = None) -> str:
        """
        Generate a bar chart visualization of the leaderboard.
        
        Args:
            metric: The metric to visualize
            top_n: Number of top models to include
            output_path: Path to save the visualization (if None, auto-generate)
            
        Returns:
            Path to the saved visualization
        """
        # Get top models
        top_models = self.list_models(limit=top_n)
        
        # Prepare data for the chart
        model_names = []
        metric_values = []
        
        for model in top_models:
            model_names.append(model["name"])
            
            # Get the metric value from the latest results
            if model["latest_results"]:
                if metric in model["latest_results"]:
                    metric_values.append(model["latest_results"][metric])
                elif metric == "test_pass_rate" and "test_pass_rate" not in model["latest_results"]:
                    # Fallback to api_success_rate if test_pass_rate is requested but not available
                    metric_values.append(model["latest_results"].get("api_success_rate", 0))
                else:
                    metric_values.append(0)
            else:
                metric_values.append(0)
        
        # Create the visualization
        plt.figure(figsize=(12, 8))
        
        # Create bars
        bars = plt.bar(model_names, metric_values, color='skyblue')
        
        # Add value annotations
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f"{height:.2f}" + ("%" if metric.endswith("rate") else ""),
                    ha='center', va='bottom')
        
        # Set labels and title
        plt.title(f"Top {min(top_n, len(top_models))} Models by {metric}")
        plt.xlabel("Model")
        ylabel = metric.replace("_", " ").title()
        if metric.endswith("rate"):
            ylabel += " (%)"
            # Convert values to percentages
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y*100:.0f}%"))
            plt.ylim(0, max(metric_values) * 1.15)  # Leave room for annotations
        
        plt.ylabel(ylabel)
        plt.xticks(rotation=45, ha="right")
        
        plt.tight_layout()
        
        # Generate output path if not provided
        if output_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = self.leaderboard_path / f"leaderboard_{metric}_{timestamp}.png"
        else:
            output_path = Path(output_path)
        
        # Save the visualization
        plt.savefig(output_path)
        plt.close()
        
        return str(output_path)
    
    def visualize_model_history(self, 
                               model_name: str,
                               metrics: List[str] = None,
                               output_path: Union[str, Path] = None) -> str:
        """
        Generate a line chart visualization of a model's performance history.
        
        Args:
            model_name: The name of the model
            metrics: List of metrics to visualize (default: ["test_pass_rate", "api_success_rate"])
            output_path: Path to save the visualization (if None, auto-generate)
            
        Returns:
            Path to the saved visualization
        """
        # Default metrics
        if metrics is None:
            metrics = ["test_pass_rate", "api_success_rate"]
        
        # Get model history
        history = self.get_model_history(model_name)
        
        if not history:
            raise ValueError(f"No history found for model: {model_name}")
        
        # Prepare data for the chart
        timestamps = []
        metric_data = {metric: [] for metric in metrics}
        
        for entry in history:
            timestamps.append(entry["timestamp"])
            
            # Collect each metric
            for metric in metrics:
                if metric in entry["summary"]:
                    metric_data[metric].append(entry["summary"][metric])
                elif metric == "test_pass_rate" and "test_pass_rate" not in entry["summary"]:
                    # Fallback to api_success_rate if test_pass_rate is requested but not available
                    metric_data[metric].append(entry["summary"].get("api_success_rate", 0))
                else:
                    metric_data[metric].append(0)
        
        # Create the visualization
        plt.figure(figsize=(12, 8))
        
        # Plot each metric
        for metric in metrics:
            plt.plot(timestamps, metric_data[metric], marker='o', label=metric.replace("_", " ").title())
        
        # Set labels and title
        plt.title(f"Performance History for {model_name}")
        plt.xlabel("Timestamp")
        plt.ylabel("Metric Value")
        
        # Format x-axis labels
        plt.xticks(rotation=45, ha="right")
        
        # Add legend
        plt.legend()
        
        # Format y-axis as percentage for rate metrics
        if all(metric.endswith("rate") for metric in metrics):
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y*100:.0f}%"))
        
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Generate output path if not provided
        if output_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = self.leaderboard_path / f"{model_name}_history_{timestamp}.png"
        else:
            output_path = Path(output_path)
        
        # Save the visualization
        plt.savefig(output_path)
        plt.close()
        
        return str(output_path)
    
    def generate_leaderboard_report(self, 
                                   output_path: Union[str, Path] = None,
                                   top_n: int = 10,
                                   format: str = "markdown") -> str:
        """
        Generate a leaderboard report.
        
        Args:
            output_path: Path to save the report (if None, auto-generate)
            top_n: Number of top models to include
            format: Report format ("markdown", "html", or "text")
            
        Returns:
            Path to the saved report
        """
        # Get top models
        top_models = self.list_models(limit=top_n)
        
        # Create a DataFrame for the report
        df = pd.DataFrame({
            "Rank": range(1, len(top_models) + 1),
            "Model": [m["name"] for m in top_models],
            "Best Score": [f"{m['best_score']:.2%}" for m in top_models],
            "Run Count": [m["entry_count"] for m in top_models],
            "Last Updated": [m["last_updated"] for m in top_models]
        })
        
        # Add metrics from the latest results
        metrics = ["test_pass_rate", "api_success_rate", "execution_success_rate", "avg_response_time"]
        for metric in metrics:
            # Try to get the metric for each model
            values = []
            for model in top_models:
                if model["latest_results"] and metric in model["latest_results"]:
                    if metric.endswith("rate"):
                        values.append(f"{model['latest_results'][metric]:.2%}")
                    else:
                        values.append(f"{model['latest_results'][metric]:.2f}s")
                else:
                    values.append("N/A")
            
            # Add the metric column
            df[metric.replace("_", " ").title()] = values
        
        # Generate the report content
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        title = f"# LM Studio Coding Benchmark Leaderboard\n\nGenerated: {timestamp}\n\n"
        
        if format == "markdown":
            content = title + df.to_markdown(index=False)
        elif format == "html":
            content = f"<h1>LM Studio Coding Benchmark Leaderboard</h1>\n<p>Generated: {timestamp}</p>\n\n"
            content += df.to_html(index=False)
        else:  # text
            content = f"LM Studio Coding Benchmark Leaderboard\nGenerated: {timestamp}\n\n"
            content += tabulate(df, headers="keys", tablefmt="plain", showindex=False)
        
        # Generate output path if not provided
        if output_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            extension = {"markdown": "md", "html": "html", "text": "txt"}[format]
            output_path = self.leaderboard_path / f"leaderboard_report_{timestamp}.{extension}"
        else:
            output_path = Path(output_path)
        
        # Save the report
        with open(output_path, "w") as f:
            f.write(content)
        
        return str(output_path)
    
    def compare_models(self, 
                  model_names: List[str],
                  metrics: List[str] = None,
                  resource_metrics: List[str] = None,
                  output_path: Union[str, Path] = None) -> str:
        """
        Generate a comparison visualization of multiple models.
        
        Args:
            model_names: List of model names to compare
            metrics: List of metrics to compare (default: test_pass_rate, api_success_rate, etc.)
            resource_metrics: List of resource metrics to include (optional)
            output_path: Path to save the visualization (if None, auto-generate)
            
        Returns:
            Path to the saved visualization
        """
        # Default metrics
        if metrics is None:
            metrics = ["test_pass_rate", "api_success_rate", "execution_success_rate", "avg_response_time"]
        
        # Default resource metrics
        if resource_metrics is None:
            resource_metrics = []
        
        # Get the latest entry for each model
        models_data = []
        for name in model_names:
            if name in self.db["models"]:
                # Get the latest entry ID
                latest_entry_id = self.db["models"][name]["entries"][-1]
                # Find this entry
                latest_entry = next((e for e in self.db["entries"] if e["id"] == latest_entry_id), None)
                
                if latest_entry:
                    models_data.append({
                        "name": name,
                        "summary": latest_entry["summary"],
                        "resource_metrics": latest_entry.get("resource_metrics", {})
                    })
        
        if not models_data:
            raise ValueError("No data found for the specified models")
        
        # Combine all metrics
        all_metrics = metrics.copy()
        
        # Add resource metrics that exist in the data
        for metric in resource_metrics:
            if any(metric in model["resource_metrics"] for model in models_data):
                all_metrics.append(f"resource:{metric}")
        
        # Prepare data for radar chart
        N = len(all_metrics)
        angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
        angles += angles[:1]  # Close the loop
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        
        # Plot each model
        for model in models_data:
            values = []
            for metric in all_metrics:
                if metric.startswith("resource:"):
                    # This is a resource metric
                    resource_metric = metric.split(":", 1)[1]
                    if resource_metric in model["resource_metrics"]:
                        # For memory and CPU metrics, lower is better, so invert
                        if resource_metric in ["memory_peak_gb", "memory_avg_gb", "cpu_max_percent", "cpu_avg_percent"]:
                            # Normalize and invert (1.0 means best, 0.0 means worst)
                            all_values = [m["resource_metrics"].get(resource_metric, 0) for m in models_data 
                                        if resource_metric in m["resource_metrics"]]
                            if all_values:
                                min_val = min(all_values)
                                max_val = max(all_values)
                                if max_val > min_val:
                                    # Invert so lower is better (1.0 means lowest/best)
                                    normalized = 1.0 - ((model["resource_metrics"][resource_metric] - min_val) / (max_val - min_val))
                                else:
                                    normalized = 1.0
                                values.append(normalized)
                            else:
                                values.append(0)
                        else:
                            # For other resource metrics, higher might be better
                            all_values = [m["resource_metrics"].get(resource_metric, 0) for m in models_data 
                                        if resource_metric in m["resource_metrics"]]
                            if all_values:
                                min_val = min(all_values)
                                max_val = max(all_values)
                                if max_val > min_val:
                                    normalized = (model["resource_metrics"][resource_metric] - min_val) / (max_val - min_val)
                                else:
                                    normalized = 1.0
                                values.append(normalized)
                            else:
                                values.append(0)
                    else:
                        values.append(0)
                else:
                    # Regular performance metric
                    if metric in model["summary"]:
                        # For response time, invert the value since lower is better
                        if metric == "avg_response_time":
                            # Normalize response time - assuming 10s is relatively slow
                            response_time = model["summary"][metric]
                            all_times = [m["summary"].get(metric, 0) for m in models_data if metric in m["summary"]]
                            if all_times:
                                max_time = max(all_times)
                                if max_time > 0:
                                    normalized = max(0, 1 - (response_time / max_time))
                                else:
                                    normalized = 1.0
                            else:
                                normalized = 0.5
                            values.append(normalized)
                        else:
                            values.append(model["summary"][metric])
                    else:
                        values.append(0)
            
            # Close the loop
            values += values[:1]
            
            # Plot the model
            ax.plot(angles, values, linewidth=2, label=model["name"])
            ax.fill(angles, values, alpha=0.1)
        
        # Set the labels
        metric_labels = []
        for metric in all_metrics:
            if metric.startswith("resource:"):
                # Format resource metric labels
                resource_metric = metric.split(":", 1)[1]
                label = resource_metric.replace("_", " ").title()
                if "percent" in resource_metric:
                    label = f"Low {label}"
                elif "gb" in resource_metric.lower():
                    label = f"Low {label}"
                else:
                    label = resource_metric.replace("_", " ").title()
                metric_labels.append(label)
            else:
                # Format regular metric labels
                if metric == "avg_response_time":
                    metric_labels.append("Speed")
                else:
                    metric_labels.append(metric.replace("_", " ").title())
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metric_labels)
        
        # Add legend and title
        ax.legend(loc='upper right')
        plt.title("Model Comparison (Including Resource Metrics)", size=15, y=1.1)
        
        plt.tight_layout()
        
        # Generate output path if not provided
        if output_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            model_suffix = "_".join(model_names)[:30]  # Limit length
            output_path = self.leaderboard_path / f"model_comparison_{model_suffix}_{timestamp}.png"
        else:
            output_path = Path(output_path)
        
        # Save the visualization
        plt.savefig(output_path)
        plt.close()
        
        return str(output_path)
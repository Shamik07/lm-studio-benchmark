from lm_studio_benchmark import LMStudioBenchmark
from code_extractor import CodeExtractor
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
import numpy as np

try:
    from resource_monitor import ResourceMonitor
except ImportError:
    ResourceMonitor = None

class EnhancedLMStudioBenchmark(LMStudioBenchmark):
    """
    Enhanced version of LM Studio Benchmark with code execution capabilities.
    """
    
    def __init__(self, model_endpoint: str = "http://localhost:1234/v1/chat/completions", 
         timeout: int = 120,
         results_dir: str = "benchmark_results",
         title: str = None,
         execute_code: bool = True,
         monitor_resources: bool = False
         ):
        """
        Initialize the enhanced benchmarking tool.
        
        Args:
            model_endpoint: The API endpoint for your LM Studio model
            timeout: Maximum time in seconds to wait for a response
            results_dir: Directory to save benchmark results
            title: Optional title for this benchmark run
            execute_code: Whether to execute code to verify functionality
        """
        # Call parent's init to set up base attributes
        super().__init__(model_endpoint, timeout, results_dir, title)
        
        # Add enhanced benchmark specific attributes
        self.execute_code = execute_code
        self.code_extractor = CodeExtractor()
        
        # Initialize resource monitor if requested
        self.monitor_resources = monitor_resources
        self.resource_monitor = None
        if monitor_resources and ResourceMonitor is not None:
            self.resource_monitor = ResourceMonitor()
    
    def query_model(self, prompt: str, language: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query the LM Studio model with a coding prompt and execute the code.
        
        Args:
            prompt: The coding task prompt
            language: The programming language to use
            task: The task definition
        
        Returns:
            Dictionary with query results including code execution if enabled
        """
        # Start monitoring resources for this query if enabled
        task_resource_results = None
        if self.monitor_resources and self.resource_monitor:
            self.resource_monitor.start_monitoring()
        
        start_time = time.time()
        success = True

        if language not in [lang for info in self.code_extractor.language_info.values() 
                   for lang in info["aliases"]]:
            print(f"Warning: Language '{language}' may not be supported for code execution")
        
        # Make language name consistent for prompt
        language_display = language
        for key, info in self.code_extractor.language_info.items():  # Use code_extractor's language_info
            if language.lower() in info["aliases"]:
                if key == "csharp":
                    language_display = "C#"
                elif key == "cpp":
                    language_display = "C++"
                else:
                    language_display = key.capitalize()
                break
        
        full_prompt = f"Write code in {language_display} for the following task:\n\n{prompt}\n\n"
        full_prompt += "Provide only the code implementation with minimal comments. Use best practices for the language."
        
        try:
            response = self._send_api_request(full_prompt)
            
            if response["success"]:
                raw_output = response["content"]
                # Extract code from raw output
                extracted_code = self.code_extractor.extract_code(raw_output, language)
                
                # Execute code if enabled
                execution_results = {}
                if self.execute_code:
                    execution_results = self.code_extractor.execute_code(extracted_code, language, task)
                
                # Check for execution success if available
                if execution_results and "success" in execution_results:
                    success = execution_results["success"]
            else:
                raw_output = f"Error: {response['error']}"
                extracted_code = raw_output
                success = False
                execution_results = {
                    "success": False,
                    "error": "Failed to get response from model",
                    "output": "",
                    "passed_tests": 0,
                    "total_tests": len(task.get("test_cases", []))
                }
                
        except Exception as e:
            raw_output = f"Exception: {str(e)}"
            extracted_code = raw_output
            success = False
            execution_results = {
                "success": False,
                "error": str(e),
                "output": f"Exception during query: {str(e)}",
                "passed_tests": 0,
                "total_tests": len(task.get("test_cases", []))
            }
            
        elapsed_time = time.time() - start_time
        
        # Stop monitoring resources
        if self.monitor_resources and self.resource_monitor:
            task_resource_results = self.resource_monitor.stop_monitoring()
        
        result = {
            "code_output": extracted_code,
            "raw_response": raw_output,
            "response_time": elapsed_time,
            "success": success,
            "execution_results": execution_results
        }
        
        # Add resource results if available
        if task_resource_results:
            result["resource_results"] = task_resource_results
        
        return result
    
    def _send_api_request(self, prompt: str) -> Dict[str, Any]:
        """
        Send request to the model endpoint.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            Dictionary with response information
        """
        try:
            import requests
            
            response = requests.post(
                self.model_endpoint,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,  # Lower temperature for more deterministic responses
                    "max_tokens": 2000
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return {
                    "success": True,
                    "content": content
                }
            else:
                return {
                    "success": False,
                    "error": f"Status code: {response.status_code}, Response: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_benchmark(self, 
                      categories: List[str] = None, 
                      difficulties: List[str] = None,
                      languages: List[str] = None,
                      num_runs: int = 1) -> Dict[str, Any]:
        """
        Run the benchmark on selected tasks with code execution.
        
        Args:
            categories: List of categories to benchmark (None = all)
            difficulties: List of difficulties to benchmark (None = all)
            languages: List of languages to benchmark (None = all)
            num_runs: Number of runs per task for better statistics
            
        Returns:
            Dictionary with benchmark results
        """
        filtered_tasks = self.tasks
        
        if categories:
            filtered_tasks = [t for t in filtered_tasks if t["category"] in categories]
        
        if difficulties:
            filtered_tasks = [t for t in filtered_tasks if t["difficulty"] in difficulties]
        
        results = {
            "model_endpoint": self.model_endpoint,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "num_runs": num_runs,
            "title": self.title,
            "tasks": []
        }
        
        total_tasks = 0
        for task in filtered_tasks:
            task_languages = languages if languages else task["languages"]
            task_languages = [lang for lang in task_languages if lang in task["languages"]]
            total_tasks += len(task_languages)
        
        completed_tasks = 0
        print(f"Starting benchmark with {total_tasks} tasks...")
        
        # Start global resource monitoring if enabled
        overall_resource_results = None
        if self.monitor_resources and self.resource_monitor:
            self.resource_monitor.start_monitoring()
        
        for task in filtered_tasks:
            task_languages = languages if languages else task["languages"]
            # Filter to only languages supported by this task
            task_languages = [lang for lang in task_languages if lang in task["languages"]]
            
            for language in task_languages:
                completed_tasks += 1
                print(f"[{completed_tasks}/{total_tasks}] Running task: {task['name']} ({language}, {task['difficulty']})")
                
                task_result = {
                    "task_name": task["name"],
                    "category": task["category"],
                    "difficulty": task["difficulty"],
                    "language": language,
                    "runs": []
                }
                
                for run in range(num_runs):
                    if num_runs > 1:
                        print(f"  Run {run+1}/{num_runs}")
                    
                    query_result = self.query_model(task["prompt"], language, task)
                    
                    run_result = {
                        "run_id": run,
                        "success": query_result["success"],
                        "response_time": query_result["response_time"],
                        "code_output": query_result["code_output"],
                        "raw_response": query_result["raw_response"]
                    }
                    
                    # Add execution results if available
                    if "execution_results" in query_result:
                        run_result["execution_results"] = query_result["execution_results"]
                    
                    # Add resource results if available
                    if "resource_results" in query_result:
                        run_result["resource_results"] = query_result["resource_results"]
                    
                    task_result["runs"].append(run_result)
                
                results["tasks"].append(task_result)
                
                # Save intermediate results after each task
                safe_title = "".join(c if c.isalnum() else "_" for c in self.title)
                results_filename = self.run_dir / f"{safe_title}_in_progress.json"
                with open(results_filename, "w") as f:
                    json.dump(results, f, indent=2)
        
        # Stop global resource monitoring if enabled
        if self.monitor_resources and self.resource_monitor:
            overall_resource_results = self.resource_monitor.stop_monitoring()
            
            # Save resource monitoring results
            if overall_resource_results:
                safe_title = "".join(c if c.isalnum() else "_" for c in self.title)
                resource_file = self.run_dir / f"{safe_title}_resources.json"
                with open(resource_file, "w") as f:
                    json.dump(overall_resource_results, f, indent=2)
                print(f"Overall resource usage saved to {resource_file}")
                
                # Add resource metrics to results
                results["resource_metrics"] = overall_resource_results
        
        # Save final results
        safe_title = "".join(c if c.isalnum() else "_" for c in self.title)
        results_filename = self.run_dir / f"{safe_title}.json"
        with open(results_filename, "w") as f:
            json.dump(results, f, indent=2)
            
        print(f"Benchmark results saved to {results_filename}")
        
        return results
    
    def analyze_results(self, results: Optional[Dict[str, Any]] = None, results_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze benchmark results with execution metrics.
        
        Args:
            results: Results dictionary from run_benchmark
            results_file: Path to results JSON file (if results not provided)
            
        Returns:
            Dictionary with analysis metrics
        """
        if results is None and results_file:
            with open(results_file, "r") as f:
                results = json.load(f)
        
        if results is None:
            raise ValueError("Either results or results_file must be provided")
        
        analysis = {
            "model_endpoint": results["model_endpoint"],
            "timestamp": results["timestamp"],
            "title": results.get("title", "Unnamed Run"),
            "summary": {
                "total_tasks": len(results["tasks"]),
                "avg_response_time": 0,
                "api_success_rate": 0,
                "execution_success_rate": 0,
                "test_pass_rate": 0,
                "by_category": {},
                "by_difficulty": {},
                "by_language": {}
            },
            "detailed": []
        }
        
        total_time = 0
        total_api_success = 0
        total_execution_success = 0
        total_test_passes = 0
        total_test_cases = 0
        total_runs = 0
        
        # Initialize dictionaries to collect statistics
        categories = {}
        difficulties = {}
        languages = {}
        
        for task in results["tasks"]:
            category = task["category"]
            difficulty = task["difficulty"]
            language = task["language"]
            
            # Initialize category/difficulty/language stats if needed
            for dimension, dimension_value in [
                ("category", category), 
                ("difficulty", difficulty), 
                ("language", language)
            ]:
                dimension_dict = None
                if dimension == "category":
                    dimension_dict = categories
                elif dimension == "difficulty":
                    dimension_dict = difficulties
                elif dimension == "language":
                    dimension_dict = languages
                    
                if dimension_value not in dimension_dict:
                    dimension_dict[dimension_value] = {
                        "runs": 0, 
                        "time": 0, 
                        "api_success": 0,
                        "execution_success": 0,
                        "test_passes": 0,
                        "total_tests": 0
                    }
            
            task_time = 0
            task_api_success = 0
            task_execution_success = 0
            task_test_passes = 0
            task_total_tests = 0
            
            for run in task["runs"]:
                total_runs += 1
                task_time += run["response_time"]
                
                # API success
                if run["success"]:
                    task_api_success += 1
                    total_api_success += 1
                
                # Execution success and test passes
                if "execution_results" in run:
                    execution_results = run["execution_results"]
                    
                    if execution_results.get("success", False):
                        task_execution_success += 1
                        total_execution_success += 1
                    
                    task_test_passes += execution_results.get("passed_tests", 0)
                    task_total_tests += execution_results.get("total_tests", 0)
                    
                    total_test_passes += execution_results.get("passed_tests", 0)
                    total_test_cases += execution_results.get("total_tests", 0)
            
            avg_task_time = task_time / len(task["runs"])
            api_success_rate = task_api_success / len(task["runs"])
            execution_success_rate = task_execution_success / len(task["runs"]) if task_total_tests > 0 else 0
            test_pass_rate = task_test_passes / task_total_tests if task_total_tests > 0 else 0
            
            total_time += task_time
            
            # Update dimension stats
            categories[category]["runs"] += len(task["runs"])
            categories[category]["time"] += task_time
            categories[category]["api_success"] += task_api_success
            categories[category]["execution_success"] += task_execution_success
            categories[category]["test_passes"] += task_test_passes
            categories[category]["total_tests"] += task_total_tests
            
            difficulties[difficulty]["runs"] += len(task["runs"])
            difficulties[difficulty]["time"] += task_time
            difficulties[difficulty]["api_success"] += task_api_success
            difficulties[difficulty]["execution_success"] += task_execution_success
            difficulties[difficulty]["test_passes"] += task_test_passes
            difficulties[difficulty]["total_tests"] += task_total_tests
            
            languages[language]["runs"] += len(task["runs"])
            languages[language]["time"] += task_time
            languages[language]["api_success"] += task_api_success
            languages[language]["execution_success"] += task_execution_success
            languages[language]["test_passes"] += task_test_passes
            languages[language]["total_tests"] += task_total_tests
            
            # Add detailed task analysis
            task_analysis = {
                "task_name": task["task_name"],
                "category": category,
                "difficulty": difficulty,
                "language": language,
                "avg_response_time": avg_task_time,
                "api_success_rate": api_success_rate,
                "execution_success_rate": execution_success_rate,
                "test_pass_rate": test_pass_rate,
                "execution_stats": {
                    "passes": task_test_passes,
                    "total": task_total_tests
                }
            }
            
            analysis["detailed"].append(task_analysis)
        
        # Calculate summary statistics
        analysis["summary"]["avg_response_time"] = total_time / total_runs if total_runs > 0 else 0
        analysis["summary"]["api_success_rate"] = total_api_success / total_runs if total_runs > 0 else 0
        analysis["summary"]["execution_success_rate"] = total_execution_success / total_runs if total_test_cases > 0 else 0
        analysis["summary"]["test_pass_rate"] = total_test_passes / total_test_cases if total_test_cases > 0 else 0
        
        # Calculate dimension statistics
        for category, stats in categories.items():
            analysis["summary"]["by_category"][category] = {
                "avg_response_time": stats["time"] / stats["runs"] if stats["runs"] > 0 else 0,
                "api_success_rate": stats["api_success"] / stats["runs"] if stats["runs"] > 0 else 0,
                "execution_success_rate": stats["execution_success"] / stats["runs"] if stats["total_tests"] > 0 else 0,
                "test_pass_rate": stats["test_passes"] / stats["total_tests"] if stats["total_tests"] > 0 else 0
            }
        
        for difficulty, stats in difficulties.items():
            analysis["summary"]["by_difficulty"][difficulty] = {
                "avg_response_time": stats["time"] / stats["runs"] if stats["runs"] > 0 else 0,
                "api_success_rate": stats["api_success"] / stats["runs"] if stats["runs"] > 0 else 0,
                "execution_success_rate": stats["execution_success"] / stats["runs"] if stats["total_tests"] > 0 else 0,
                "test_pass_rate": stats["test_passes"] / stats["total_tests"] if stats["total_tests"] > 0 else 0
            }
        
        for language, stats in languages.items():
            analysis["summary"]["by_language"][language] = {
                "avg_response_time": stats["time"] / stats["runs"] if stats["runs"] > 0 else 0,
                "api_success_rate": stats["api_success"] / stats["runs"] if stats["runs"] > 0 else 0,
                "execution_success_rate": stats["execution_success"] / stats["runs"] if stats["total_tests"] > 0 else 0,
                "test_pass_rate": stats["test_passes"] / stats["total_tests"] if stats["total_tests"] > 0 else 0
            }
        
        return analysis
    
    def visualize_results(self, analysis: Dict[str, Any] = None, analysis_file: str = None, 
                          output_dir: str = None):
        """
        Generate enhanced visualizations of benchmark results.
        
        Args:
            analysis: Analysis dictionary from analyze_results
            analysis_file: Path to analysis JSON file (if analysis not provided)
            output_dir: Directory to save visualizations (default: results_dir)
        """
        if analysis is None and analysis_file:
            with open(analysis_file, "r") as f:
                analysis = json.load(f)
        
        if analysis is None:
            raise ValueError("Either analysis or analysis_file must be provided")
            
        # Make sure the title is set in the analysis
        if "title" not in analysis and hasattr(self, "title"):
            analysis["title"] = self.title
        
        if output_dir is None:
            output_dir = self.run_dir if hasattr(self, "run_dir") else self.results_dir
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True, parents=True)
        
        # Add title to file names if provided
        title_prefix = ""
        if "title" in analysis and analysis["title"]:
            title_prefix = "".join(c if c.isalnum() else "_" for c in analysis["title"]) + "_"
        
        # Generate standard visualizations from parent class
        super().visualize_results(analysis, output_dir=output_dir)
        
        # Generate additional visualizations for execution metrics
        
        # Plot 1: API Success vs Execution Success vs Test Pass Rate
        self._plot_success_metrics_comparison(
            analysis["summary"],
            f"Success Metrics - {analysis.get('title', 'Unnamed Run')}",
            output_dir / f"{title_prefix}success_metrics_comparison.png"
        )
        
        # Plot 2: Test Pass Rate by Category
        self._plot_metric_by_dimension(
            analysis["summary"]["by_category"], 
            "test_pass_rate",
            f"Test Pass Rate by Category - {analysis.get('title', 'Unnamed Run')}",
            "Category",
            "Test Pass Rate",
            output_dir / f"{title_prefix}test_pass_rate_by_category.png",
            is_rate=True
        )
        
        # Plot 3: Test Pass Rate by Difficulty
        self._plot_metric_by_dimension(
            analysis["summary"]["by_difficulty"], 
            "test_pass_rate",
            f"Test Pass Rate by Difficulty - {analysis.get('title', 'Unnamed Run')}",
            "Difficulty",
            "Test Pass Rate",
            output_dir / f"{title_prefix}test_pass_rate_by_difficulty.png",
            is_rate=True,
            sort_keys=["easy", "medium", "hard"]
        )
        
        # Plot 4: Test Pass Rate by Language
        self._plot_metric_by_dimension(
            analysis["summary"]["by_language"], 
            "test_pass_rate",
            f"Test Pass Rate by Language - {analysis.get('title', 'Unnamed Run')}",
            "Language",
            "Test Pass Rate",
            output_dir / f"{title_prefix}test_pass_rate_by_language.png",
            is_rate=True
        )
        
        # Plot 5: Detailed Task Performance Heatmap
        self._plot_task_performance_heatmap(
            analysis["detailed"],
            output_dir / f"{title_prefix}task_performance_heatmap.png",
            title_suffix=analysis.get('title', 'Unnamed Run')
        )
        
        print(f"Enhanced visualizations saved to {output_dir}")
    
    def _plot_success_metrics_comparison(self, summary: Dict[str, Any], title: str, output_path: Path):
        """Plot a comparison of the different success metrics."""
        plt.figure(figsize=(10, 6))
        
        metrics = [
            ("API Success", summary["api_success_rate"] * 100),
            ("Execution Success", summary["execution_success_rate"] * 100),
            ("Test Pass Rate", summary["test_pass_rate"] * 100)
        ]
        
        labels = [m[0] for m in metrics]
        values = [m[1] for m in metrics]
        
        bars = plt.bar(labels, values, color=['skyblue', 'lightgreen', 'coral'])
        
        # Add value annotations
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f"{height:.2f}%",
                    ha='center', va='bottom')
        
        plt.title(title)
        plt.ylabel("Success Rate (%)")
        plt.ylim(0, 110)  # Leave room for annotations
        
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
    
    def _plot_task_performance_heatmap(self, detailed_data: List[Dict[str, Any]], output_path: Path, title_suffix=''):
        """Plot a heatmap of task performance by category and language."""
        # Extract unique categories and languages
        categories = sorted(set(item["category"] for item in detailed_data))
        languages = sorted(set(item["language"] for item in detailed_data))
        
        # Create a matrix for the heatmap
        matrix = np.zeros((len(categories), len(languages)))
        count_matrix = np.zeros((len(categories), len(languages)))
        
        # Fill the matrix with test pass rates
        for item in detailed_data:
            cat_idx = categories.index(item["category"])
            lang_idx = languages.index(item["language"])
            matrix[cat_idx, lang_idx] += item["test_pass_rate"]
            count_matrix[cat_idx, lang_idx] += 1
        
        # Average where we have multiple entries
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                if count_matrix[i, j] > 0:
                    matrix[i, j] /= count_matrix[i, j]
        
        # Plot the heatmap
        plt.figure(figsize=(14, 10))
        plt.imshow(matrix, cmap='YlGnBu', aspect='auto')
        
        # Add annotations
        for i in range(len(categories)):
            for j in range(len(languages)):
                if count_matrix[i, j] > 0:
                    plt.text(j, i, f"{matrix[i, j]*100:.1f}%", 
                            ha="center", va="center", 
                            color="black" if matrix[i, j] > 0.5 else "white")
                else:
                    plt.text(j, i, "N/A", ha="center", va="center", color="gray")
        
        # Add labels and title
        plt.colorbar(label="Test Pass Rate")
        plt.xticks(range(len(languages)), languages, rotation=45, ha="right")
        plt.yticks(range(len(categories)), categories)
        plt.xlabel("Language")
        plt.ylabel("Category")
        plt.title(f"Task Performance Heatmap - {title_suffix}")
        
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
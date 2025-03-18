from code_extractor import CodeExtractor
import json
import time
import requests
import os
from pathlib import Path
import concurrent.futures
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any, Tuple

class LMStudioBenchmark:
    """
    A benchmarking tool for LM Studio models on coding tasks.
    """
    
    def __init__(self, model_endpoint: str = "http://localhost:1234/v1/chat/completions", 
         timeout: int = 120,
         results_dir: str = "benchmark_results",
         title: str = None):
        # Basic attributes
        self.model_endpoint = model_endpoint
        self.timeout = timeout
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.title = title or f"benchmark_{int(time.time())}"
        
        # Create a specific directory for this benchmark run
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() else "_" for c in self.title)
        self.run_dir = self.results_dir / f"{safe_title}_{timestamp}"
        self.run_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize code extractor
        self.code_extractor = CodeExtractor()
        self.execute_code = False  # Base class doesn't execute code by default
        
        # Load benchmark tasks
        self.tasks = self._load_benchmark_tasks()
        
    def _load_benchmark_tasks(self) -> List[Dict[str, Any]]:
        """
        Load the benchmark tasks from the predefined set, with all languages added.
        """
        # Complete list of all supported languages
        all_languages = ["python", "javascript", "java", "cpp", "go", "rust", "csharp", "php", "swift", "kotlin", "dart"]
        
        # Languages that work best for specialized tasks
        algorithmic_languages = all_languages
        web_languages = ["python", "javascript", "php", "go", "rust"]
        
        return [
            # Basic tasks
            {
                "category": "syntax",
                "name": "hello_world",
                "description": "Write a 'Hello, World!' program",
                "prompt": "Write a function that prints 'Hello, World!'",
                "difficulty": "easy",
                "test_cases": [{"input": None, "expected": "Hello, World!"}],
                "languages": all_languages
            },
            {
                "category": "algorithms",
                "name": "fibonacci",
                "description": "Implement a Fibonacci sequence generator",
                "prompt": "Write a function that returns the nth Fibonacci number.",
                "difficulty": "easy",
                "test_cases": [
                    {"input": 0, "expected": 0},
                    {"input": 1, "expected": 1},
                    {"input": 10, "expected": 55}
                ],
                "languages": algorithmic_languages
            },
            {
                "category": "algorithms",
                "name": "binary_search",
                "description": "Implement binary search algorithm",
                "prompt": "Write a function to perform binary search on a sorted array.",
                "difficulty": "medium",
                "test_cases": [
                    {"input": {"arr": [1, 2, 3, 4, 5], "target": 3}, "expected": 2},
                    {"input": {"arr": [1, 2, 3, 4, 5], "target": 6}, "expected": -1}
                ],
                "languages": algorithmic_languages
            },
            
            # Data structures
            {
                "category": "data_structures",
                "name": "linked_list",
                "description": "Implement a linked list",
                "prompt": "Implement a singly linked list with methods for append, delete, and search.",
                "difficulty": "medium",
                "test_cases": [],  # Complex to automatically test
                "languages": algorithmic_languages
            },
            
            # Advanced algorithms
            {
                "category": "algorithms",
                "name": "quicksort",
                "description": "Implement the quicksort algorithm",
                "prompt": "Write a function to sort an array using the quicksort algorithm.",
                "difficulty": "hard",
                "test_cases": [
                    {"input": [5, 2, 9, 1, 5, 6], "expected": [1, 2, 5, 5, 6, 9]}
                ],
                "languages": algorithmic_languages
            },
            
            # Bug fixing
            {
                "category": "debugging",
                "name": "fix_bug",
                "description": "Fix a bug in a function",
                "prompt": """Fix the bug in this function:
    ```python
    def calculate_average(numbers):
        total = 0
        for num in numbers:
            total += num
        return total / len(numbers - 1)
    ```""",
                "difficulty": "medium",
                "test_cases": [
                    {"input": [1, 2, 3, 4, 5], "expected": 3.0}
                ],
                "languages": ["python"]  # This is Python-specific
            },
            
            # API and library usage
            {
                "category": "api_usage",
                "name": "json_parser",
                "description": "Parse and manipulate JSON data",
                "prompt": "Write a function that takes a JSON string containing a list of users with 'name' and 'age' fields, and returns the average age.",
                "difficulty": "medium",
                "test_cases": [
                    {"input": '{"users":[{"name":"John","age":30},{"name":"Jane","age":25}]}', "expected": 27.5}
                ],
                "languages": all_languages  # JSON is supported in all languages
            },
            
            # Web development
            {
                "category": "web_dev",
                "name": "html_parser",
                "description": "Extract data from HTML",
                "prompt": "Write a function that extracts all the links from an HTML string.",
                "difficulty": "medium",
                "test_cases": [
                    {"input": '<html><body><a href="https://example.com">Link</a><a href="https://test.com">Test</a></body></html>', 
                    "expected": ["https://example.com", "https://test.com"]}
                ],
                "languages": web_languages
            },
            
            # Concurrency
            {
                "category": "concurrency",
                "name": "parallel_processing",
                "description": "Implement a parallel processing solution",
                "prompt": "Write a function that uses multithreading to download content from multiple URLs concurrently.",
                "difficulty": "hard",
                "test_cases": [],  # Complex to automatically test
                "languages": ["python", "java", "go", "rust", "cpp", "csharp"]  # Languages with good concurrency support
            },
            
            # Testing
            {
                "category": "testing",
                "name": "unit_test",
                "description": "Write unit tests for a function",
                "prompt": """Write unit tests for this function:
    ```python
    def is_palindrome(s):
        s = s.lower().replace(' ', '')
        return s == s[::-1]
    ```""",
                "difficulty": "medium",
                "test_cases": [],  # Meta-testing is complex
                "languages": ["python", "javascript", "java", "cpp", "csharp"]  # Languages with good testing frameworks
            }
        ]

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
        start_time = time.time()
        success = True

        if not hasattr(self, 'code_extractor') or self.code_extractor is None:
            self.code_extractor = CodeExtractor()
            
        if not hasattr(self, 'execute_code'):
            self.execute_code = False
        
        # Make language name consistent for prompt
        language_display = language
        try:
            for key, info in self.code_extractor.language_info.items():
                if language.lower() in info["aliases"]:
                    if key == "csharp":
                        language_display = "C#"
                    elif key == "cpp":
                        language_display = "C++"
                    else:
                        language_display = key.capitalize()
                    break
        except (AttributeError, KeyError) as e:
            print(f"Warning: Error accessing language information: {e}")
        
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
        
        return {
            "code_output": extracted_code,
            "raw_response": raw_output,
            "response_time": elapsed_time,
            "success": success,
            "execution_results": execution_results
        }
    
    def _send_api_request(self, prompt: str) -> Dict[str, Any]:
        """
        Send request to the model endpoint.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            Dictionary with response information
        """
        try:
            response = requests.post(
                self.model_endpoint,
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
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
        Run the benchmark on selected tasks.
        
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
        
        for task in filtered_tasks:
            task_languages = languages if languages else task["languages"]
            for language in task_languages:
                if language in task["languages"]:
                    print(f"Running task: {task['name']} ({language}, {task['difficulty']})")
                    
                    task_result = {
                        "task_name": task["name"],
                        "category": task["category"],
                        "difficulty": task["difficulty"],
                        "language": language,
                        "runs": []
                    }
                    
                    for run in range(num_runs):
                        query_result = self.query_model(task["prompt"], language, task)
                        
                        run_result = {
                            "run_id": run,
                            "success": query_result["success"],
                            "response_time": query_result["response_time"],
                            "code_output": query_result["code_output"],
                            "raw_response": query_result.get("raw_response", "")
                        }
                        
                        task_result["runs"].append(run_result)
                    
                    results["tasks"].append(task_result)
        
        # Save results to file
        safe_title = "".join(c if c.isalnum() else "_" for c in self.title)
        results_filename = self.run_dir / f"{safe_title}.json"
        with open(results_filename, "w") as f:
            json.dump(results, f, indent=2)
            
        print(f"Benchmark results saved to {results_filename}")
        
        return results
    
    def analyze_results(self, results: Dict[str, Any] = None, results_file: str = None) -> Dict[str, Any]:
        """
        Analyze benchmark results.
        
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
                "success_rate": 0,
                "by_category": {},
                "by_difficulty": {},
                "by_language": {}
            },
            "detailed": []
        }
        
        total_time = 0
        total_success = 0
        total_runs = 0
        
        categories = {}
        difficulties = {}
        languages = {}
        
        for task in results["tasks"]:
            category = task["category"]
            difficulty = task["difficulty"]
            language = task["language"]
            
            if category not in categories:
                categories[category] = {"runs": 0, "time": 0, "success": 0}
            if difficulty not in difficulties:
                difficulties[difficulty] = {"runs": 0, "time": 0, "success": 0}
            if language not in languages:
                languages[language] = {"runs": 0, "time": 0, "success": 0}
            
            task_time = 0
            task_success = 0
            
            for run in task["runs"]:
                total_runs += 1
                task_time += run["response_time"]
                
                if run["success"]:
                    task_success += 1
                    total_success += 1
            
            avg_task_time = task_time / len(task["runs"])
            success_rate = task_success / len(task["runs"])
            
            total_time += task_time
            
            # Update category stats
            categories[category]["runs"] += len(task["runs"])
            categories[category]["time"] += task_time
            categories[category]["success"] += task_success
            
            # Update difficulty stats
            difficulties[difficulty]["runs"] += len(task["runs"])
            difficulties[difficulty]["time"] += task_time
            difficulties[difficulty]["success"] += task_success
            
            # Update language stats
            languages[language]["runs"] += len(task["runs"])
            languages[language]["time"] += task_time
            languages[language]["success"] += task_success
            
            # Add detailed task analysis
            task_analysis = {
                "task_name": task["task_name"],
                "category": category,
                "difficulty": difficulty,
                "language": language,
                "avg_response_time": avg_task_time,
                "success_rate": success_rate
            }
            
            analysis["detailed"].append(task_analysis)
        
        # Calculate summary statistics
        analysis["summary"]["avg_response_time"] = total_time / total_runs
        analysis["summary"]["success_rate"] = total_success / total_runs
        
        # Calculate category statistics
        for category, stats in categories.items():
            analysis["summary"]["by_category"][category] = {
                "avg_response_time": stats["time"] / stats["runs"],
                "success_rate": stats["success"] / stats["runs"]
            }
        
        # Calculate difficulty statistics
        for difficulty, stats in difficulties.items():
            analysis["summary"]["by_difficulty"][difficulty] = {
                "avg_response_time": stats["time"] / stats["runs"],
                "success_rate": stats["success"] / stats["runs"]
            }
        
        # Calculate language statistics
        for language, stats in languages.items():
            analysis["summary"]["by_language"][language] = {
                "avg_response_time": stats["time"] / stats["runs"],
                "success_rate": stats["success"] / stats["runs"]
            }
        
        return analysis
    
    def visualize_results(self, analysis: Dict[str, Any] = None, analysis_file: str = None, 
                          output_dir: str = None):
        """
        Generate visualizations of benchmark results.
        
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
        
        # Plot 1: Response time by category
        self._plot_metric_by_dimension(
            analysis["summary"]["by_category"], 
            "avg_response_time",
            f"Response Time by Category - {analysis.get('title', 'Unnamed Run')}",
            "Category",
            "Average Response Time (s)",
            output_dir / f"{title_prefix}response_time_by_category.png"
        )
        
        # Plot 2: Success rate by category
        self._plot_metric_by_dimension(
            analysis["summary"]["by_category"], 
            "api_success_rate",
            f"Success Rate by Category - {analysis.get('title', 'Unnamed Run')}",
            "Category",
            "Success Rate",
            output_dir / f"{title_prefix}api_success_rate_by_category.png",
            is_rate=True
        )
        
        # Plot 3: Response time by difficulty
        self._plot_metric_by_dimension(
            analysis["summary"]["by_difficulty"], 
            "avg_response_time",
            f"Response Time by Difficulty - {analysis.get('title', 'Unnamed Run')}",
            "Difficulty",
            "Average Response Time (s)",
            output_dir / f"{title_prefix}response_time_by_difficulty.png",
            sort_keys=["easy", "medium", "hard"]
        )
        
        # Plot 4: Success rate by difficulty
        self._plot_metric_by_dimension(
            analysis["summary"]["by_difficulty"], 
            "api_success_rate",
            f"Success Rate by Difficulty - {analysis.get('title', 'Unnamed Run')}",
            "Difficulty",
            "Success Rate",
            output_dir / f"{title_prefix}api_success_rate_by_difficulty.png",
            is_rate=True,
            sort_keys=["easy", "medium", "hard"]
        )
        
        # Plot 5: Response time by language
        self._plot_metric_by_dimension(
            analysis["summary"]["by_language"], 
            "avg_response_time",
            f"Response Time by Language - {analysis.get('title', 'Unnamed Run')}",
            "Language",
            "Average Response Time (s)",
            output_dir / f"{title_prefix}response_time_by_language.png"
        )
        
        # Plot 6: Success rate by language
        self._plot_metric_by_dimension(
            analysis["summary"]["by_language"], 
            "api_success_rate",
            f"Success Rate by Language - {analysis.get('title', 'Unnamed Run')}",
            "Language",
            "Success Rate",
            output_dir / f"{title_prefix}api_success_rate_by_language.png",
            is_rate=True
        )
        
        # Plot 7: Task comparison
        self._plot_task_comparison(
            analysis["detailed"],
            output_dir / f"{title_prefix}task_comparison.png",
            title_suffix=analysis.get('title', 'Unnamed Run')
        )
        
        print(f"Visualizations saved to {output_dir}")
    
    def _plot_metric_by_dimension(self, data: Dict[str, Dict[str, float]], 
                                 metric: str, title: str, xlabel: str, ylabel: str,
                                 output_path: str, is_rate: bool = False,
                                 sort_keys: List[str] = None):
        """Helper function to plot metrics by a dimension."""
        plt.figure(figsize=(10, 6))
        
        if sort_keys:
            # Sort by provided keys
            sorted_items = [(k, data[k][metric]) for k in sort_keys if k in data]
        else:
            # Sort by metric value
            sorted_items = sorted([(k, v[metric]) for k, v in data.items()], 
                                 key=lambda x: x[1], reverse=True)
        
        labels = [item[0] for item in sorted_items]
        values = [item[1] for item in sorted_items]
        
        bars = plt.bar(labels, values, color='skyblue')
        
        # Add value annotations
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f"{height:.2f}" + ("%" if is_rate else ""),
                    ha='center', va='bottom')
        
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        if is_rate:
            plt.ylim(0, 1.1)  # For rate plots
            # Convert y-axis to percentage
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
        
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
    
    def _plot_task_comparison(self, detailed_data: List[Dict[str, Any]], output_path: str, title_suffix=''):
        """Plot a comparison of all tasks."""
        plt.figure(figsize=(12, 8))
        
        # Sort tasks by difficulty, then success rate
        difficulty_order = {"easy": 0, "medium": 1, "hard": 2}
        sorted_data = sorted(detailed_data, 
                            key=lambda x: (difficulty_order[x["difficulty"]], -x["api_success_rate"]))
        
        # Prepare data
        tasks = [f"{item['task_name']}\n({item['language']})" for item in sorted_data]
        response_times = [item["avg_response_time"] for item in sorted_data]
        success_rates = [item["api_success_rate"] for item in sorted_data]
        
        # Set up colors based on difficulty
        colors = ['green' if item["difficulty"] == "easy" else
                 'orange' if item["difficulty"] == "medium" else
                 'red' for item in sorted_data]
        
        # Plot
        x = np.arange(len(tasks))
        width = 0.35
        
        fig, ax1 = plt.subplots(figsize=(14, 8))
        
        # Plot response time bars
        bars1 = ax1.bar(x - width/2, response_times, width, color='skyblue', alpha=0.7, label='Response Time')
        ax1.set_ylabel('Response Time (s)')
        ax1.set_ylim(0, max(response_times) * 1.2)
        
        # Create second y-axis for success rate
        ax2 = ax1.twinx()
        bars2 = ax2.bar(x + width/2, success_rates, width, color=colors, alpha=0.7, label='Success Rate')
        ax2.set_ylabel('Success Rate')
        ax2.set_ylim(0, 1.1)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
        
        # X-axis settings
        ax1.set_xticks(x)
        ax1.set_xticklabels(tasks, rotation=45, ha='right')
        
        # Add a legend
        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        
        # Add difficulty legend
        difficulty_handles = [
            plt.Rectangle((0,0), 1, 1, color='green', alpha=0.7),
            plt.Rectangle((0,0), 1, 1, color='orange', alpha=0.7),
            plt.Rectangle((0,0), 1, 1, color='red', alpha=0.7)
        ]
        difficulty_labels = ['Easy', 'Medium', 'Hard']
        
        ax1.legend(handles1 + difficulty_handles, labels1 + difficulty_labels, 
                  loc='upper left', bbox_to_anchor=(0, -0.15), ncol=4)
        
        title = 'Task Comparison: Response Time and Success Rate'
        if title_suffix:
            title += f' - {title_suffix}'
        plt.title(title)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

# Usage example
if __name__ == "__main__":
    # Create benchmark runner
    benchmark = LMStudioBenchmark(
        model_endpoint="http://localhost:1234/v1/chat/completions",
        results_dir="benchmark_results"
    )
    
    # Run benchmark (adjust parameters as needed)
    results = benchmark.run_benchmark(
        categories=None,  # All categories
        difficulties=["easy", "medium"],  # Only easy and medium tasks
        languages=["python"],  # Only Python
        num_runs=3  # Run each task 3 times for better statistics
    )
    
    # Analyze results
    analysis = benchmark.analyze_results(results)
    
    # Visualize results
    benchmark.visualize_results(analysis)
    
    # Print summary
    print("\nBenchmark Summary:")
    print(f"Average Response Time: {analysis['summary']['avg_response_time']:.2f}s")
    print(f"Overall Success Rate: {analysis['summary']['success_rate']*100:.2f}%")
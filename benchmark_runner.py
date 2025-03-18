#!/usr/bin/env python3
"""
Enhanced LM Studio Coding Benchmark Runner Script
This script provides a command-line interface to run benchmarks
against your LM Studio models with code execution capabilities.
"""

from resource_monitor import ResourceMonitor

import argparse
import sys
import json
import time 
import matplotlib.pyplot as plt
import concurrent.futures
from tqdm import tqdm
from pathlib import Path

# Import the benchmarking classes
from enhanced_benchmark import EnhancedLMStudioBenchmark

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Benchmark LM Studio models on coding tasks with execution support."
    )

    # Add leaderboard commands subparser
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Main benchmark command (default)
    benchmark_parser = subparsers.add_parser("benchmark", help="Run benchmark")

    benchmark_parser.add_argument(
        "--monitor-resources",
        action="store_true",
        help="Monitor resource usage (CPU, memory, GPU) during benchmark"
    )
    
    benchmark_parser.add_argument(
        "--endpoint", 
        type=str, 
        default="http://localhost:1234/v1/chat/completions",
        help="LM Studio API endpoint URL"
    )
    
    benchmark_parser.add_argument(
        "--output-dir", 
        type=str, 
        default="benchmark_results",
        help="Directory to save results"
    )
    
    benchmark_parser.add_argument(
        "--timeout", 
        type=int, 
        default=120,
        help="Maximum time in seconds to wait for model response"
    )
    
    benchmark_parser.add_argument(
        "--categories",
        nargs="*",
        choices=["syntax", "algorithms", "data_structures", "debugging", 
                 "api_usage", "web_dev", "concurrency", "testing", "error_handling", "oop"],
        help="Categories to benchmark (default: all)"
    )
    
    benchmark_parser.add_argument(
        "--difficulties",
        nargs="*",
        choices=["easy", "medium", "hard"],
        help="Difficulty levels to benchmark (default: all)"
    )
    
    benchmark_parser.add_argument(
        "--languages",
        nargs="*",
        choices=["c", "cpp", "csharp", "php", "rust", "go", 
                 "javascript", "typescript", "java", "kotlin", 
                 "dart", "python", "swift"],
        help="Programming languages to benchmark (default: all available per task)"
    )
    
    benchmark_parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of runs per task for better statistics"
    )
    
    benchmark_parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Custom title for this benchmark run (will be used in filenames and reports)"
    )
    
    benchmark_parser.add_argument(
        "--compare",
        nargs="*",
        help="Compare multiple previous benchmark result files"
    )
    
    benchmark_parser.add_argument(
        "--analyze-only",
        type=str,
        help="Path to results file to analyze without running benchmarks"
    )
    
    benchmark_parser.add_argument(
        "--visualize-only",
        type=str,
        help="Path to analysis file to visualize without running benchmarks"
    )
    
    benchmark_parser.add_argument(
        "--execute-code",
        action="store_true",
        help="Execute code to verify functionality (requires language runtimes)"
    )
    
    benchmark_parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of parallel tasks to run (default: 1, sequential)"
    )
    
    benchmark_parser.add_argument(
        "--resume",
        type=str,
        help="Resume from a previously interrupted benchmark file"
    )

    # Leaderboard commands
    leaderboard_parser = subparsers.add_parser("leaderboard", help="Leaderboard management")
    leaderboard_subparsers = leaderboard_parser.add_subparsers(dest="leaderboard_command", help="Leaderboard command")

    # Add resource-specific commands
    resource_parser = leaderboard_subparsers.add_parser("resources", help="Resource metrics visualization")
    resource_parser.add_argument("--metric", type=str, default="memory_peak_gb", 
                            choices=["memory_peak_gb", "memory_avg_gb", "cpu_max_percent", "cpu_avg_percent", 
                                    "gpu_avg_utilization", "gpu_max_utilization"],
                            help="Resource metric to visualize")
    resource_parser.add_argument("--top", type=int, default=10, help="Number of top models to include")
    resource_parser.add_argument("--output", type=str, help="Output file path")
    
    # Add to leaderboard
    add_parser = leaderboard_subparsers.add_parser("add", help="Add benchmark result to leaderboard")
    add_parser.add_argument("analysis_file", help="Path to analysis JSON file")
    add_parser.add_argument("model_name", help="Name of the model")
    add_parser.add_argument("--model-info", type=str, help="JSON string with model info (optional)")
    
    # List leaderboard entries
    list_parser = leaderboard_subparsers.add_parser("list", help="List leaderboard entries")
    list_parser.add_argument("--model", type=str, help="Filter by model name")
    list_parser.add_argument("--limit", type=int, default=10, help="Maximum number of entries to return")
    list_parser.add_argument("--metric", type=str, default="test_pass_rate", 
                            choices=["test_pass_rate", "api_success_rate", "execution_success_rate", "avg_response_time"],
                            help="Metric to sort by")
    list_parser.add_argument("--min-date", type=str, help="Minimum date (YYYY-MM-DD)")
    list_parser.add_argument("--max-date", type=str, help="Maximum date (YYYY-MM-DD)")
    
    # List models in leaderboard
    models_parser = leaderboard_subparsers.add_parser("models", help="List models in leaderboard")
    models_parser.add_argument("--metric", type=str, default="best_score", 
                              choices=["best_score", "last_updated", "entry_count",
                                      "test_pass_rate", "api_success_rate", "execution_success_rate"],
                              help="Metric to sort by")
    models_parser.add_argument("--limit", type=int, default=10, help="Maximum number of models to show")
    
    # Visualize leaderboard
    visualize_parser = leaderboard_subparsers.add_parser("visualize", help="Create leaderboard visualization")
    visualize_parser.add_argument("--metric", type=str, default="test_pass_rate", 
                                choices=["test_pass_rate", "api_success_rate", "execution_success_rate", "avg_response_time"],
                                help="Metric to visualize")
    visualize_parser.add_argument("--top", type=int, default=10, help="Number of top models to include")
    visualize_parser.add_argument("--output", type=str, help="Output file path")
    
    # Generate leaderboard report
    report_parser = leaderboard_subparsers.add_parser("report", help="Generate leaderboard report")
    report_parser.add_argument("--top", type=int, default=10, help="Number of top models to include")
    report_parser.add_argument("--format", type=str, default="markdown", 
                              choices=["markdown", "html", "text"],
                              help="Report format")
    report_parser.add_argument("--output", type=str, help="Output file path")
    
    # Compare models
    model_compare_parser = leaderboard_subparsers.add_parser("compare", help="Compare models")
    model_compare_parser.add_argument("models", nargs="+", help="Models to compare")
    model_compare_parser.add_argument("--metrics", nargs="+", 
                            default=["test_pass_rate", "api_success_rate", "execution_success_rate", "avg_response_time"],
                            help="Metrics to compare")
    model_compare_parser.add_argument("--resource-metrics", nargs="+", 
                            choices=["memory_peak_gb", "memory_avg_gb", "cpu_max_percent", "cpu_avg_percent", 
                                    "gpu_avg_utilization", "gpu_max_utilization"],
                            help="Resource metrics to include in comparison")
    model_compare_parser.add_argument("--output", type=str, help="Output file path")
    
    # Show model history
    history_parser = leaderboard_subparsers.add_parser("history", help="Show model history")
    history_parser.add_argument("model_name", help="Name of the model")
    history_parser.add_argument("--metrics", nargs="+", 
                               default=["test_pass_rate", "api_success_rate"],
                               help="Metrics to visualize")
    history_parser.add_argument("--output", type=str, help="Output file path")
    
    # Delete entry from leaderboard
    delete_parser = leaderboard_subparsers.add_parser("delete", help="Delete entry from leaderboard")
    delete_parser.add_argument("entry_id", help="ID of the entry to delete")
    
    return parser.parse_args()

def compare_benchmarks(benchmark_files, output_dir):
    """Compare multiple benchmark result files and generate comparative visualizations."""
    print(f"Comparing {len(benchmark_files)} benchmark results...")
    
    all_results = []
    all_analyses = []
    
    for file_path in benchmark_files:
        try:
            with open(file_path, "r") as f:
                results = json.load(f)
                all_results.append(results)
                
            # Create a temporary benchmark instance to analyze this result
            temp_benchmark = EnhancedLMStudioBenchmark(results_dir=output_dir)
            analysis = temp_benchmark.analyze_results(results)
            all_analyses.append(analysis)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Create comparison visualizations
    output_dir = Path(output_dir)
    compare_dir = output_dir / "comparisons"
    compare_dir.mkdir(exist_ok=True, parents=True)
    
    # Compare success rates for different metrics
    metrics = [
        ("api_success_rate", "API Success Rate", "Success Rate (%)", "skyblue"),
        ("execution_success_rate", "Execution Success Rate", "Success Rate (%)", "lightgreen"),
        ("test_pass_rate", "Test Pass Rate", "Pass Rate (%)", "coral")
    ]
    
    for metric, title, ylabel, color in metrics:
        plt.figure(figsize=(12, 6))
        
        titles = [result.get("title", Path(file).stem) for result, file in zip(all_results, benchmark_files)]
        rates = [analysis["summary"].get(metric, 0) * 100 for analysis in all_analyses]
        
        plt.bar(titles, rates, color=color)
        plt.title(f"{title} Comparison")
        plt.ylabel(ylabel)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(compare_dir / f"{metric}_comparison.png")
        plt.close()
    
    # Compare response times
    plt.figure(figsize=(12, 6))
    
    response_times = [analysis["summary"]["avg_response_time"] for analysis in all_analyses]
    
    plt.bar(titles, response_times, color='lightcoral')
    plt.title("Response Time Comparison")
    plt.ylabel("Average Response Time (s)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(compare_dir / "response_time_comparison.png")
    plt.close()
    
    # Create a summary table/matrix comparing performance across languages
    all_languages = set()
    for analysis in all_analyses:
        all_languages.update(analysis["summary"]["by_language"].keys())
    
    all_languages = sorted(all_languages)
    
    # Create a radar chart for overall metrics
    try:
        create_radar_chart(all_analyses, titles, compare_dir / "metrics_radar_chart.png")
    except Exception as e:
        print(f"Error creating radar chart: {e}")
    
    # Create a comparison report
    report_path = compare_dir / "comparison_report.json"
    comparison = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "benchmarks": titles,
        "metrics": {
            "api_success_rates": dict(zip(titles, [a["summary"]["api_success_rate"] * 100 for a in all_analyses])),
            "execution_success_rates": dict(zip(titles, [a["summary"].get("execution_success_rate", 0) * 100 for a in all_analyses])),
            "test_pass_rates": dict(zip(titles, [a["summary"].get("test_pass_rate", 0) * 100 for a in all_analyses])),
            "response_times": dict(zip(titles, response_times))
        },
        "by_language": {
            lang: {
                title: analysis["summary"]["by_language"].get(lang, {}).get("test_pass_rate", 0) * 100 
                for title, analysis in zip(titles, all_analyses)
            } for lang in all_languages
        },
        "detailed": all_analyses
    }
    
    with open(report_path, "w") as f:
        json.dump(comparison, f, indent=2)
    
    print(f"Comparison results saved to {compare_dir}")
    
    # Print summary of comparison
    print("\nBenchmark Comparison Summary:")
    print("-" * 40)
    for title, analysis in zip(titles, all_analyses):
        print(f"{title}:")
        print(f"  API Success Rate: {analysis['summary']['api_success_rate']*100:.2f}%")
        print(f"  Execution Success: {analysis['summary'].get('execution_success_rate', 0)*100:.2f}%")
        print(f"  Test Pass Rate: {analysis['summary'].get('test_pass_rate', 0)*100:.2f}%")
        print(f"  Avg Response Time: {analysis['summary']['avg_response_time']:.2f}s")
        print()
    
    return 0

def create_radar_chart(all_analyses, titles, output_path):
    """Create a radar chart comparing the key metrics across benchmarks."""
    import numpy as np
    
    metrics = [
        "api_success_rate", 
        "execution_success_rate", 
        "test_pass_rate", 
        "inverse_response_time"  # We'll convert response time to be higher=better
    ]
    
    metric_labels = [
        "API Success", 
        "Execution Success", 
        "Test Pass Rate", 
        "Speed"
    ]
    
    # Prepare the data
    data = []
    for analysis in all_analyses:
        # Calculate inverse response time and normalize it to 0-1 scale
        avg_time = analysis["summary"]["avg_response_time"]
        inverse_time = 1.0 / (avg_time if avg_time > 0 else 1.0)
        
        # Normalize inverse time to reasonable scale (higher is better)
        # This is a simplistic approach, could be made more sophisticated
        inverse_time_normalized = min(inverse_time / 0.1, 1.0)  # Assuming 10s+ is slow (value of 0.1)
        
        values = [
            analysis["summary"]["api_success_rate"],
            analysis["summary"].get("execution_success_rate", 0),
            analysis["summary"].get("test_pass_rate", 0),
            inverse_time_normalized
        ]
        data.append(values)
    
    # Set up the radar chart
    angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]  # Close the loop
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    # Add each benchmark to the chart
    for i, (values, title) in enumerate(zip(data, titles)):
        values = values + values[:1]  # Close the loop
        ax.plot(angles, values, linewidth=2, linestyle='solid', label=title)
        ax.fill(angles, values, alpha=0.1)
    
    # Set the labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metric_labels)
    
    # Add legend and title
    ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.title("Benchmark Comparison Radar Chart", size=15, color='blue', y=1.1)
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def run_task_parallel(benchmark, task, language, num_runs):
    """Run a single task for parallel execution."""
    print(f"Running task: {task['name']} ({language}, {task['difficulty']})")
    
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
        
        query_result = benchmark.query_model(task["prompt"], language, task)
        
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
        
        task_result["runs"].append(run_result)
    
    return task_result

def run_parallel_benchmark(benchmark, filtered_tasks, languages, num_runs, max_workers):
    """Run the benchmark tasks in parallel."""
    results = {
        "model_endpoint": benchmark.model_endpoint,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "num_runs": num_runs,
        "title": benchmark.title,
        "tasks": []
    }
    
    tasks_to_run = []
    for task in filtered_tasks:
        task_languages = languages if languages else task["languages"]
        task_languages = [lang for lang in task_languages if lang in task["languages"]]
        
        for language in task_languages:
            tasks_to_run.append((task, language))
    
    print(f"Running {len(tasks_to_run)} tasks in parallel with {max_workers} workers...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for task, language in tasks_to_run:
            future = executor.submit(run_task_parallel, benchmark, task, language, num_runs)
            futures.append(future)
        
        # Use tqdm for progress tracking
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            task_result = future.result()
            results["tasks"].append(task_result)
            
            # Save intermediate results
            safe_title = "".join(c if c.isalnum() else "_" for c in benchmark.title)
            results_filename = benchmark.run_dir / f"{safe_title}_in_progress.json"
            with open(results_filename, "w") as f:
                json.dump(results, f, indent=2)
    
    # Save final results
    safe_title = "".join(c if c.isalnum() else "_" for c in benchmark.title)
    results_filename = benchmark.run_dir / f"{safe_title}.json"
    with open(results_filename, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Benchmark results saved to {results_filename}")
    
    return results

def resume_benchmark(benchmark, resume_file, categories, difficulties, languages, num_runs, parallel):
    """Resume a benchmark from a previously interrupted run."""
    print(f"Resuming benchmark from {resume_file}...")
    
    try:
        with open(resume_file, "r") as f:
            previous_results = json.load(f)
        
        # Set benchmark title to match previous run
        if "title" in previous_results:
            benchmark.title = previous_results["title"]
        
        # Filter tasks based on parameters
        filtered_tasks = benchmark.tasks
        
        if categories:
            filtered_tasks = [t for t in filtered_tasks if t["category"] in categories]
        
        if difficulties:
            filtered_tasks = [t for t in filtered_tasks if t["difficulty"] in difficulties]
        
        # Determine which tasks have already been completed
        completed_tasks = set()
        for task_result in previous_results["tasks"]:
            completed_tasks.add((task_result["task_name"], task_result["language"]))
        
        # Build list of tasks that still need to be run
        tasks_to_run = []
        for task in filtered_tasks:
            task_languages = languages if languages else task["languages"]
            task_languages = [lang for lang in task_languages if lang in task["languages"]]
            
            for language in task_languages:
                if (task["name"], language) not in completed_tasks:
                    tasks_to_run.append((task, language))
        
        print(f"Found {len(previous_results['tasks'])} completed tasks, {len(tasks_to_run)} remaining.")
        
        if not tasks_to_run:
            print("All tasks already completed!")
            return previous_results
        
        # Run remaining tasks
        new_results = {
            "model_endpoint": benchmark.model_endpoint,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "num_runs": num_runs,
            "title": benchmark.title,
            "tasks": previous_results["tasks"]  # Start with previously completed tasks
        }
        
        # Run tasks based on parallel option
        if parallel > 1:
            # Run tasks in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as executor:
                futures = []
                for task, language in tasks_to_run:
                    future = executor.submit(run_task_parallel, benchmark, task, language, num_runs)
                    futures.append(future)
                
                # Use tqdm for progress tracking
                for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
                    task_result = future.result()
                    new_results["tasks"].append(task_result)
                    
                    # Save intermediate results
                    safe_title = "".join(c if c.isalnum() else "_" for c in benchmark.title)
                    results_filename = benchmark.run_dir / f"{safe_title}_in_progress.json"
                    with open(results_filename, "w") as f:
                        json.dump(new_results, f, indent=2)
        else:
            # Run tasks sequentially
            for task, language in tqdm(tasks_to_run):
                task_result = run_task_parallel(benchmark, task, language, num_runs)
                new_results["tasks"].append(task_result)
                
                # Save intermediate results
                safe_title = "".join(c if c.isalnum() else "_" for c in benchmark.title)
                results_filename = benchmark.run_dir / f"{safe_title}_in_progress.json"
                with open(results_filename, "w") as f:
                    json.dump(new_results, f, indent=2)
        
        # Save final results
        safe_title = "".join(c if c.isalnum() else "_" for c in benchmark.title)
        results_filename = benchmark.run_dir / f"{safe_title}.json"
        with open(results_filename, "w") as f:
            json.dump(new_results, f, indent=2)
            
        print(f"Resumed benchmark results saved to {results_filename}")
        
        return new_results
        
    except Exception as e:
        print(f"Error resuming benchmark: {e}")
        return None

def handle_leaderboard_command(args):
    """Handle leaderboard commands."""
    from leaderboard import Leaderboard
    
    # Create leaderboard instance
    leaderboard = Leaderboard()
    
    if args.leaderboard_command == "add":
        # Parse model_info if provided
        model_info = None
        if args.model_info:
            try:
                model_info = json.loads(args.model_info)
            except json.JSONDecodeError:
                print(f"Error parsing model_info JSON: {args.model_info}")
                return 1
        
        # Add entry
        try:
            entry = leaderboard.add_entry(args.analysis_file, args.model_name, model_info)
            print(f"Added entry {entry['id']} for model {args.model_name} to leaderboard")
            return 0
        except Exception as e:
            print(f"Error adding entry to leaderboard: {e}")
            return 1
        
    elif args.leaderboard_command == "resources":
        # Visualize resource metrics
        try:
            output_path = leaderboard.visualize_resource_metrics(
                metric=args.metric,
                top_n=args.top,
                output_path=args.output
            )
            print(f"Resource metrics visualization saved to {output_path}")
            return 0
        except Exception as e:
            print(f"Error visualizing resource metrics: {e}")
            return 1
        
    elif args.leaderboard_command == "list":
        # List entries
        try:
            entries = leaderboard.list_entries(
                model_name=args.model,
                limit=args.limit,
                metric=args.metric,
                min_date=args.min_date,
                max_date=args.max_date
            )
            
            if not entries:
                print("No entries found.")
                return 0
            
            # Create a DataFrame for tabular output
            import pandas as pd
            from tabulate import tabulate
            
            data = []
            for i, entry in enumerate(entries):
                data.append({
                    "Rank": i + 1,
                    "ID": entry["id"],
                    "Model": entry["model_name"],
                    "Timestamp": entry["timestamp"],
                    "Title": entry["title"],
                    args.metric: f"{entry['summary'].get(args.metric, 0):.2%}" if args.metric.endswith("rate") else 
                               f"{entry['summary'].get(args.metric, 0):.2f}s" if args.metric == "avg_response_time" else
                               entry['summary'].get(args.metric, "N/A")
                })
            
            df = pd.DataFrame(data)
            print(tabulate(df, headers="keys", tablefmt="pretty", showindex=False))
            return 0
        except Exception as e:
            print(f"Error listing entries: {e}")
            return 1
    
    elif args.leaderboard_command == "models":
        # List models
        try:
            models = leaderboard.list_models(metric=args.metric, limit=args.limit)
            
            if not models:
                print("No models found.")
                return 0
            
            # Create a DataFrame for tabular output
            import pandas as pd
            from tabulate import tabulate
            
            data = []
            for i, model in enumerate(models):
                data.append({
                    "Rank": i + 1,
                    "Model": model["name"],
                    "Best Score": f"{model['best_score']:.2%}",
                    "Entries": model["entry_count"],
                    "Last Updated": model["last_updated"]
                })
            
            df = pd.DataFrame(data)
            print(tabulate(df, headers="keys", tablefmt="pretty", showindex=False))
            return 0
        except Exception as e:
            print(f"Error listing models: {e}")
            return 1
    
    elif args.leaderboard_command == "visualize":
        # Create visualization
        try:
            output_path = leaderboard.visualize_leaderboard(
                metric=args.metric,
                top_n=args.top,
                output_path=args.output
            )
            print(f"Leaderboard visualization saved to {output_path}")
            return 0
        except Exception as e:
            print(f"Error creating visualization: {e}")
            return 1
    
    elif args.leaderboard_command == "report":
        # Generate report
        try:
            output_path = leaderboard.generate_leaderboard_report(
                output_path=args.output,
                top_n=args.top,
                format=args.format
            )
            print(f"Leaderboard report saved to {output_path}")
            return 0
        except Exception as e:
            print(f"Error generating report: {e}")
            return 1
    
    elif args.leaderboard_command == "compare":
        # Compare models
        try:
            output_path = leaderboard.compare_models(
                model_names=args.models,
                metrics=args.metrics,
                resource_metrics=args.resource_metrics, 
                output_path=args.output
            )
            print(f"Model comparison visualization saved to {output_path}")
            return 0
        except Exception as e:
            print(f"Error comparing models: {e}")
            return 1
    
    elif args.leaderboard_command == "history":
        # Show model history
        try:
            output_path = leaderboard.visualize_model_history(
                model_name=args.model_name,
                metrics=args.metrics,
                output_path=args.output
            )
            print(f"Model history visualization saved to {output_path}")
            return 0
        except Exception as e:
            print(f"Error showing model history: {e}")
            return 1
    
    elif args.leaderboard_command == "delete":
        # Delete entry
        try:
            success = leaderboard.delete_entry(args.entry_id)
            if success:
                print(f"Deleted entry {args.entry_id} from leaderboard")
                return 0
            else:
                print(f"Entry {args.entry_id} not found")
                return 1
        except Exception as e:
            print(f"Error deleting entry: {e}")
            return 1
    
    else:
        print("Unknown leaderboard command. Run with --help for usage information.")
        return 1

def prompt_add_to_leaderboard(analysis_file, benchmark_title):
    """
    Prompt the user to add the benchmark results to the leaderboard.
    
    Args:
        analysis_file: Path to the analysis file
        benchmark_title: Title of the benchmark
        
    Returns:
        True if added to leaderboard, False otherwise
    """
    try:
        # First check if leaderboard module is available
        try:
            from leaderboard import Leaderboard
        except ImportError as e:
            missing_module = str(e).split("'")[1] if "'" in str(e) else str(e)
            print(f"\nCannot add to leaderboard: Missing module '{missing_module}'")
            print(f"Please install required dependencies: pip install pandas tabulate")
            return False
        
        while True:
            response = input(f"\nWould you like to add this benchmark result '{benchmark_title}' to the leaderboard? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                model_name = input("Enter model name for the leaderboard (press Enter to use benchmark title): ").strip()
                if not model_name:
                    model_name = benchmark_title
                
                # Ask for additional model info
                add_info = input("Add additional model info? (e.g., parameters, version) (y/n): ").strip().lower()
                model_info = {}
                if add_info in ['y', 'yes']:
                    parameters = input("Number of parameters (e.g., 7B, 13B): ").strip()
                    if parameters:
                        model_info["parameters"] = parameters
                    
                    version = input("Model version: ").strip()
                    if version:
                        model_info["version"] = version
                    
                    architecture = input("Model architecture: ").strip()
                    if architecture:
                        model_info["architecture"] = architecture
                    
                    quantization = input("Quantization (e.g., Q4_K_M, 4-bit): ").strip()
                    if quantization:
                        model_info["quantization"] = quantization
                
                # Create leaderboard and add entry
                leaderboard = Leaderboard()
                entry = leaderboard.add_entry(
                    analysis_file, 
                    model_name, 
                    model_info if model_info else None
                )
                
                print(f"Added entry {entry['id']} for model {model_name} to leaderboard")
                return True
            elif response in ['n', 'no']:
                print("Benchmark results not added to leaderboard")
                return False
            else:
                print("Please enter 'y' or 'n'")
    except Exception as e:
        print(f"Error adding to leaderboard: {e}")
        return False

def main():
    args = parse_arguments()

    # Handle leaderboard commands
    if hasattr(args, 'command') and args.command == "leaderboard":
        return handle_leaderboard_command(args)
    
    # Handle benchmark comparison
    if args.compare:
        return compare_benchmarks(args.compare, args.output_dir)
    
    # Create benchmark instance
    benchmark_title = args.title or f"benchmark_{int(time.time())}"
    benchmark = EnhancedLMStudioBenchmark(
        model_endpoint=args.endpoint,
        timeout=args.timeout,
        results_dir=args.output_dir,
        title=benchmark_title,
        execute_code=args.execute_code,
        monitor_resources=args.monitor_resources 
    )
    
    # Handle visualization-only mode
    if args.visualize_only:
        print(f"Visualizing analysis from {args.visualize_only}")
        try:
            with open(args.visualize_only, "r") as f:
                analysis = json.load(f)
                
            # Extract the title from the analysis file if available
            if "title" in analysis:
                benchmark.title = analysis["title"]
                
            # Create a specific directory for this visualization if needed
            if not hasattr(benchmark, "run_dir") or not benchmark.run_dir.exists():
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                safe_title = "".join(c if c.isalnum() else "_" for c in benchmark.title)
                viz_dir = benchmark.results_dir / f"{safe_title}_viz_{timestamp}"
                viz_dir.mkdir(exist_ok=True, parents=True)
                benchmark.run_dir = viz_dir
                print(f"Created visualization directory: {viz_dir}")
                
            benchmark.visualize_results(analysis)
            return 0
        except Exception as e:
            print(f"Error visualizing results: {e}")
            return 1
    
    # Handle analysis-only mode
    if args.analyze_only:
        print(f"Analyzing results from {args.analyze_only}")
        try:
            # Get title from results file
            with open(args.analyze_only, "r") as f:
                results_data = json.load(f)
                if "title" in results_data:
                    benchmark.title = results_data["title"]
            
            # Create a specific directory for this analysis
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c if c.isalnum() else "_" for c in benchmark.title)
            analysis_dir = benchmark.results_dir / f"{safe_title}_analysis_{timestamp}"
            analysis_dir.mkdir(exist_ok=True, parents=True)
            benchmark.run_dir = analysis_dir
            
            analysis = benchmark.analyze_results(results_file=args.analyze_only)
            
            # Save analysis
            analysis_file = benchmark.run_dir / f"analysis_{safe_title}.json"
            with open(analysis_file, "w") as f:
                json.dump(analysis, f, indent=2)
            
            print(f"Analysis saved to {analysis_file}")
            
            # Visualize
            benchmark.visualize_results(analysis)
            
            # Print summary
            print("\nBenchmark Summary:")
            print(f"Average Response Time: {analysis['summary']['avg_response_time']:.2f}s")
            print(f"API Success Rate: {analysis['summary']['api_success_rate']*100:.2f}%")
            
            if "execution_success_rate" in analysis["summary"]:
                print(f"Execution Success Rate: {analysis['summary']['execution_success_rate']*100:.2f}%")
            
            if "test_pass_rate" in analysis["summary"]:
                print(f"Test Pass Rate: {analysis['summary']['test_pass_rate']*100:.2f}%")
            
            return 0
        except Exception as e:
            print(f"Error analyzing results: {e}")
            return 1
    
    # Handle resume mode
    if args.resume:
        results = resume_benchmark(
            benchmark, 
            args.resume, 
            args.categories, 
            args.difficulties, 
            args.languages, 
            args.runs,
            args.parallel
        )
        
        if not results:
            return 1
        
        # Analyze results
        print("Analyzing results...")
        analysis = benchmark.analyze_results(results)
        
        # Save analysis
        safe_title = "".join(c if c.isalnum() else "_" for c in benchmark_title)
        analysis_file = benchmark.run_dir / f"analysis_{safe_title}.json"
        with open(analysis_file, "w") as f:
            json.dump(analysis, f, indent=2)
        
        print(f"Analysis saved to {analysis_file}")
        
        # Visualize
        print("Generating visualizations...")
        benchmark.visualize_results(analysis)
        
        # Print summary
        print("\nBenchmark Summary:")
        print(f"Average Response Time: {analysis['summary']['avg_response_time']:.2f}s")
        print(f"API Success Rate: {analysis['summary']['api_success_rate']*100:.2f}%")
        
        if "execution_success_rate" in analysis["summary"]:
            print(f"Execution Success Rate: {analysis['summary']['execution_success_rate']*100:.2f}%")
        
        if "test_pass_rate" in analysis["summary"]:
            print(f"Test Pass Rate: {analysis['summary']['test_pass_rate']*100:.2f}%")
        
        return 0
    
    # Run benchmark
    print("Starting benchmark...")
    try:
        # Initialize the resource monitor if requested
        resource_monitor = None
        if hasattr(args, 'monitor_resources') and args.monitor_resources:
            print("Initializing resource monitoring...")
            resource_monitor = ResourceMonitor()
            
        # Filter tasks based on categories and difficulties
        filtered_tasks = benchmark.tasks
        
        if args.categories:
            filtered_tasks = [t for t in filtered_tasks if t["category"] in args.categories]
        
        if args.difficulties:
            filtered_tasks = [t for t in filtered_tasks if t["difficulty"] in args.difficulties]
        
        # Run benchmark based on parallel option
        if args.parallel > 1:
            # Start resource monitoring
            if resource_monitor:
                resource_monitor.start_monitoring()
            
            results = run_parallel_benchmark(
                benchmark,
                filtered_tasks,
                args.languages,
                args.runs,
                args.parallel
            )
            
            # Stop resource monitoring and get results
            resource_results = None
            if resource_monitor:
                resource_results = resource_monitor.stop_monitoring()
                safe_title = "".join(c if c.isalnum() else "_" for c in benchmark_title)
                resource_file = resource_monitor.save_results(resource_results, 
                                                            f"benchmark_results/{safe_title}_resources.json")
                print(f"Resource usage saved to {resource_file}")
        else:
            # Start resource monitoring
            if resource_monitor:
                resource_monitor.start_monitoring()
            
            # Run benchmark sequentially
            results = benchmark.run_benchmark(
                categories=args.categories,
                difficulties=args.difficulties,
                languages=args.languages,
                num_runs=args.runs
            )
            
            # Stop resource monitoring and get results
            resource_results = None
            if resource_monitor:
                resource_results = resource_monitor.stop_monitoring()
                safe_title = "".join(c if c.isalnum() else "_" for c in benchmark_title)
                resource_file = resource_monitor.save_results(resource_results, 
                                                            f"benchmark_results/{safe_title}_resources.json")
                print(f"Resource usage saved to {resource_file}")
        
        # Add resource metrics to results if available
        if resource_results:
            results["resource_metrics"] = resource_results
        
        # Analyze results
        print("Analyzing results...")
        analysis = benchmark.analyze_results(results)
        
        # Save analysis
        safe_title = "".join(c if c.isalnum() else "_" for c in benchmark_title)
        analysis_file = benchmark.run_dir / f"analysis_{safe_title}.json"
        with open(analysis_file, "w") as f:
            json.dump(analysis, f, indent=2)
        
        print(f"Analysis saved to {analysis_file}")
        
        # Visualize
        print("Generating visualizations...")
        benchmark.visualize_results(analysis)
        
        # Visualize resource usage if available
        if resource_monitor and resource_results:
            resource_plot = resource_monitor.plot_resource_usage(
                f"benchmark_results/{safe_title}_resources.json",
                f"benchmark_results/{safe_title}_resource_plot.png"
            )
            print(f"Resource usage plot saved to {resource_plot}")
        
        # Print summary
        print("\nBenchmark Summary:")
        print(f"Average Response Time: {analysis['summary']['avg_response_time']:.2f}s")
        print(f"API Success Rate: {analysis['summary']['api_success_rate']*100:.2f}%")
        
        if "execution_success_rate" in analysis["summary"]:
            print(f"Execution Success Rate: {analysis['summary']['execution_success_rate']*100:.2f}%")
        
        if "test_pass_rate" in analysis["summary"]:
            print(f"Test Pass Rate: {analysis['summary']['test_pass_rate']*100:.2f}%")
        
        # Print resource summary if available
        if resource_results:
            print("\nResource Usage Summary:")
            print(f"CPU Avg: {resource_results['cpu']['percent']['mean']:.1f}%, Max: {resource_results['cpu']['percent']['max']:.1f}%")
            print(f"Memory Avg: {resource_results['memory']['used_gb']['mean']:.2f} GB, Peak: {resource_results['memory']['used_gb']['max']:.2f} GB")
            
            if resource_results.get("gpu") and resource_results["gpu"]:
                if "utilization" in resource_results["gpu"]:
                    print(f"GPU Utilization Avg: {resource_results['gpu']['utilization']['mean']:.1f}%, Max: {resource_results['gpu']['utilization']['max']:.1f}%")
                elif "devices" in resource_results["gpu"]:
                    for device, stats in resource_results["gpu"]["devices"].items():
                        print(f"{device} Utilization Avg: {stats['utilization']['mean']:.1f}%, Max: {stats['utilization']['max']:.1f}%")
        
        # Ask user if they want to add to leaderboard
        prompt_add_to_leaderboard(str(analysis_file), benchmark_title)

        return 0
    except Exception as e:
        print(f"Error running benchmark: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
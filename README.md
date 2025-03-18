# LM Studio Coding Benchmark

A comprehensive benchmarking tool for evaluating LM Studio models on various coding tasks.

## Overview

This tool allows you to benchmark your LM Studio models on a variety of coding tasks across different programming languages, difficulty levels, and categories. It provides detailed analysis and visualizations to help you understand your model's performance, plus a leaderboard to track and compare multiple models over time.

## Features

- Benchmark models on various coding tasks
- Support for multiple programming languages (Python, JavaScript, Java, C++)
- Different difficulty levels (easy, medium, hard)
- Various task categories (syntax, algorithms, data structures, debugging, API usage, web development, concurrency, testing)
- Detailed analysis with visualizations
- Compare multiple benchmark runs
- **Leaderboard system** to track model performance over time
- Generate reports and visualizations comparing different models

## Installation

1. Clone this repository
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```bash
python benchmark_runner.py benchmark
```

This will run the benchmark using default settings:
- Endpoint: http://localhost:1234/v1/chat/completions
- All categories, difficulties, and languages
- One run per task

### Advanced Options

```bash
python benchmark_runner.py benchmark --endpoint "http://localhost:1234/v1/chat/completions" \
                          --output-dir "benchmark_results" \
                          --timeout 120 \
                          --categories algorithms data_structures \
                          --difficulties easy medium \
                          --languages python javascript \
                          --runs 3 \
                          --title "MyModel_v1_Benchmark"
```

### Command-line Arguments for Benchmarking

| Argument | Description |
|----------|-------------|
| `--endpoint` | LM Studio API endpoint URL |
| `--output-dir` | Directory to save results |
| `--timeout` | Maximum time in seconds to wait for model response |
| `--categories` | Categories to benchmark (default: all) |
| `--difficulties` | Difficulty levels to benchmark (default: all) |
| `--languages` | Programming languages to benchmark (default: all available per task) |
| `--runs` | Number of runs per task for better statistics |
| `--title` | Custom title for this benchmark run (will be used in filenames and reports) |
| `--compare` | Compare multiple previous benchmark result files |
| `--analyze-only` | Path to results file to analyze without running benchmarks |
| `--visualize-only` | Path to analysis file to visualize without running benchmarks |
| `--execute-code` | Execute code to verify functionality (requires language runtimes) |
| `--parallel` | Number of parallel tasks to run (default: 1, sequential) |
| `--resume` | Resume from a previously interrupted benchmark file |

## Available Task Categories

- `syntax`: Basic syntax tasks
- `algorithms`: Algorithm implementation tasks
- `data_structures`: Data structure implementation tasks
- `debugging`: Bug fixing tasks
- `api_usage`: API and library usage tasks
- `web_dev`: Web development tasks
- `concurrency`: Parallel processing tasks
- `testing`: Unit testing tasks

## Analyzing Results

To analyze an existing results file without running benchmarks again:

```bash
python benchmark_runner.py benchmark --analyze-only "benchmark_results/my_benchmark.json"
```

## Visualizing Results

To visualize an existing analysis file:

```bash
python benchmark_runner.py benchmark --visualize-only "benchmark_results/analysis_my_benchmark.json"
```

## Comparing Benchmarks

To compare multiple benchmark runs:

```bash
python benchmark_runner.py benchmark --compare "benchmark_results/model1.json" "benchmark_results/model2.json"
```

## Leaderboard System

The benchmark tool now includes a leaderboard system to track and compare model performance over time.

### Adding Benchmark Results to the Leaderboard

After running a benchmark and generating analysis, add it to the leaderboard:

```bash
python benchmark_runner.py leaderboard add analysis_file.json "Model Name"
```

You can also add additional model information:

```bash
python benchmark_runner.py leaderboard add analysis_file.json "Model Name" \
  --model-info '{"parameters": "7B", "version": "1.0", "architecture": "Transformer"}'
```

### Viewing the Leaderboard

List the top models in the leaderboard:

```bash
python benchmark_runner.py leaderboard models
```

List benchmark entries:

```bash
python benchmark_runner.py leaderboard list
```

### Creating Visualizations

Visualize the leaderboard:

```bash
python benchmark_runner.py leaderboard visualize
```

Compare specific models:

```bash
python benchmark_runner.py leaderboard compare "Model A" "Model B" "Model C"
```

View a model's performance history:

```bash
python benchmark_runner.py leaderboard history "Model Name"
```

### Generating Reports

Create a leaderboard report:

```bash
python benchmark_runner.py leaderboard report
```

### Available Leaderboard Commands

| Command | Description |
|---------|-------------|
| `add` | Add benchmark result to leaderboard |
| `list` | List leaderboard entries |
| `models` | List models in leaderboard |
| `visualize` | Create leaderboard visualization |
| `report` | Generate leaderboard report |
| `compare` | Compare models |
| `history` | Show model history |
| `delete` | Delete entry from leaderboard |

Run `python benchmark_runner.py leaderboard [command] --help` for detailed usage information.

## Resource Monitoring

The benchmark tool now includes resource monitoring capabilities to track CPU, memory, and GPU usage during benchmarks. This is especially useful for optimizing performance on MacBook M3 Max and other hardware.

### Running Benchmarks with Resource Monitoring

Add the `--monitor-resources` flag to your benchmark command:

```bash
python benchmark_runner.py benchmark --title "Model-Test" --execute-code --monitor-resources
```

This will:
1. Track CPU, memory, and GPU usage during the benchmark
2. Save detailed resource metrics alongside benchmark results
3. Generate resource usage visualizations
4. Include resource metrics in the benchmark summary

### Resource Metrics in the Leaderboard

Resource metrics are automatically included in the leaderboard when available. You can:

1. Visualize resource metrics across models:

```bash
python benchmark_runner.py leaderboard resources --metric memory_peak_gb
```

2. Compare resource efficiency between models:

```bash
python benchmark_runner.py leaderboard compare "Model A" "Model B" --resource-metrics memory_peak_gb cpu_max_percent
```

### Available Resource Metrics

- **CPU Usage**: 
  - `cpu_avg_percent`: Average CPU usage during benchmark
  - `cpu_max_percent`: Peak CPU usage

- **Memory Usage**:
  - `memory_avg_gb`: Average memory usage in GB
  - `memory_peak_gb`: Peak memory usage in GB

- **GPU Usage** (when available):
  - `gpu_avg_utilization`: Average GPU utilization percentage
  - `gpu_max_utilization`: Peak GPU utilization percentage

### MacBook M3 Max Optimization

For Apple Silicon devices like MacBook M3 Max, the tool uses platform-specific methods to monitor GPU usage and provides insights to help you optimize model performance for your hardware.

Resource monitoring has minimal overhead and provides valuable data for comparing different models' efficiency on your specific hardware configuration.

## Example Output

The tool generates various visualizations including:
- Response time by category
- Success rate by category
- Response time by difficulty
- Success rate by difficulty
- Response time by language
- Success rate by language
- Task comparison
- Leaderboard rankings
- Model comparison charts
- Performance history trends

Results and analysis are saved in JSON format for further processing.

## Auto-Add to Leaderboard

The benchmark now includes an interactive feature to automatically add results to the leaderboard after completion.

### How it Works

1. After a benchmark run finishes successfully, you will be prompted:
   ```
   Would you like to add this benchmark result 'Benchmark-Title' to the leaderboard? (y/n):
   ```

2. If you choose yes (`y`), you'll be prompted to:
   - Enter a model name (or press Enter to use the benchmark title)
   - Add additional model information like parameters, version, architecture, and quantization

3. The benchmark results are then automatically added to the leaderboard with the provided metadata

### Benefits

- Streamlines the workflow by removing the need to manually add results to the leaderboard
- Ensures proper metadata is captured for each benchmark
- Makes it easier to maintain a comprehensive record of model performance

### Example

```
Benchmark Summary:
Average Response Time: 0.78s
API Success Rate: 100.00%
Execution Success Rate: 0.00%
Test Pass Rate: 0.00%

Resource Usage Summary:
CPU Avg: 6.3%, Max: 12.6%
Memory Avg: 15.23 GB, Peak: 16.28 GB
GPU Utilization Avg: 0.0%, Max: 0.0%

Would you like to add this benchmark result 'Test-Resources' to the leaderboard? (y/n): y
Enter model name for the leaderboard (press Enter to use benchmark title): qwen2.5-7b-instruct
Add additional model info? (e.g., parameters, version) (y/n): y
Number of parameters (e.g., 7B, 13B): 7B
Model version: 2.5
Model architecture: Transformer
Quantization (e.g., Q4_K_M, 4-bit): Q4_K_M

Added entry entry_1710785531 for model qwen2.5-7b-instruct to leaderboard
```

You can still manually add entries to the leaderboard using the command:
```bash
python benchmark_runner.py leaderboard add <analysis_file> <model_name>
```

## License

[MIT License](LICENSE)
# Benchmark Results Directory

This directory contains the output data from the LM Studio Coding Benchmark tool.

## Directory Structure

Each benchmark run creates a new subdirectory with the format:
```
{benchmark_title}_{timestamp}/
```

For example:
```
mlx_community_qwen2_5_coder_7b_instruct_No_Spec_20250314_011812/
```

## Files in Each Benchmark Directory

Each benchmark run directory typically contains the following files:

- **{benchmark_title}.json**: Raw benchmark results with detailed information about each task, run, and model response
- **{benchmark_title}_in_progress.json**: Temporary file created during benchmark execution (may be deleted after completion)
- **analysis_{benchmark_title}.json**: Analysis of the benchmark results with various metrics and statistics

## Visualization Files

After analysis, the following visualization files may be generated:

- **response_time_by_category.png**: Average response time for each category
- **api_success_rate_by_category.png**: Success rate for each category
- **response_time_by_difficulty.png**: Average response time by difficulty level
- **api_success_rate_by_difficulty.png**: Success rate by difficulty level
- **response_time_by_language.png**: Average response time by programming language
- **api_success_rate_by_language.png**: Success rate by programming language
- **task_comparison.png**: Comparison of all tasks by response time and success rate
- **success_metrics_comparison.png**: Comparison of different success metrics (API, execution, test pass)
- **test_pass_rate_by_category.png**: Test pass rate by category
- **test_pass_rate_by_difficulty.png**: Test pass rate by difficulty level
- **test_pass_rate_by_language.png**: Test pass rate by programming language
- **task_performance_heatmap.png**: Heatmap showing performance across categories and languages

## Analysis Directory

When using the `--analyze-only` flag, an analysis directory is created with the format:
```
{benchmark_title}_analysis_{timestamp}/
```

This directory contains the analysis results and visualizations.

## Comparison Directory

When using the `--compare` flag to compare multiple benchmarks, a comparison directory is created at:
```
comparisons/
```

This directory contains comparative visualizations between different benchmark runs.

## Interpreting Results

- **API Success Rate**: Percentage of runs where the model successfully produced valid code
- **Execution Success Rate**: Percentage of runs where the code executed without errors
- **Test Pass Rate**: Percentage of test cases that passed successfully
- **Response Time**: Average time taken for the model to generate a response
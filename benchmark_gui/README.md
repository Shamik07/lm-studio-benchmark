# LM Studio Benchmark GUI

A comprehensive graphical user interface for the LM Studio Coding Benchmark tool, designed to evaluate and compare language models on programming tasks with detailed analysis and visualization capabilities.

## Features

- **Interactive Benchmark Interface**: Easily configure and run coding benchmarks with real-time progress tracking
- **Rich Visualization Tools**: Generate and explore detailed visualizations of benchmark results
- **Comprehensive Leaderboard System**: Track and compare performance across different models with multiple metrics
- **Resource Monitoring**: Track CPU, memory, and GPU usage during benchmarking for efficiency comparison
- **Detailed Performance Analysis**: Examine performance breakdowns by category, difficulty, and language
- **Report Generation**: Create formatted reports in Markdown, HTML, or plain text formats
- **Theme Support**: Switch between light and dark themes for comfortable viewing

## Installation

### Prerequisites

- Python 3.8 or later
- Required Python packages:
  - ttkbootstrap>=1.10.1
  - matplotlib>=3.5.0
  - Pillow>=9.0.0
  - numpy>=1.22.0
  - pandas>=1.4.0
  - tabulate>=0.8.10
  - requests>=2.28.0

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/lm-studio-benchmark-gui.git
   cd lm-studio-benchmark-gui
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Usage Guide

### Benchmark Tab

The Benchmark tab allows you to run coding benchmarks against any LM Studio model or compatible API endpoint.

1. **Configure the benchmark**:
   - Set the API endpoint for your model (default: http://localhost:1234/v1/chat/completions)
   - Choose a benchmark title and customize run settings
   - Select categories, difficulties, and languages to test
   - Configure execution options and resource monitoring

2. **Run the benchmark**:
   - Click "Run Benchmark" to start the evaluation
   - Monitor progress in real-time with detailed logging
   - View comprehensive results summary when complete
   - Cancel running benchmarks safely if needed

3. **Result Options**:
   - View detailed analysis with performance breakdowns
   - Examine color-coded metrics for quick performance assessment
   - Navigate through category, difficulty, and language performance
   - Generate visualizations or add to leaderboard for comparison

### Visualize Tab

The Visualize tab provides advanced tools to generate and explore visualizations from benchmark analyses.

1. **Select analysis file**:
   - Choose an analysis file from a previous benchmark
   - Select specific visualization types to generate
   - Customize visualization parameters

2. **Generate and explore**:
   - Create visualizations with a single click
   - Navigate through multiple charts with intuitive controls
   - View visualization interpretations and context
   - Save visualizations in PNG format for reports or presentations

### Leaderboard Tab

The Leaderboard tab maintains a database of benchmark results for comprehensive comparison.

1. **View leaderboard**:
   - See models ranked by various performance metrics
   - Filter and sort to focus on specific aspects
   - Apply custom filters to find specific model types

2. **Analyze entries**:
   - View detailed statistics for each benchmark run
   - Examine color-coded performance breakdowns
   - Explore tooltips for metric explanations
   - Dive into category, difficulty, and language performance

3. **Generate comparisons**:
   - Compare multiple models side-by-side with radar charts
   - Visualize performance history of specific models over time
   - Analyze resource efficiency across different models
   - Generate comprehensive comparison reports

4. **Generate reports**:
   - Create formatted leaderboard reports
   - Choose from Markdown, HTML, or plain text formats
   - Customize report content and depth

### Settings Tab

The Settings tab provides extensive configuration options for the application.

1. **General settings**:
   - Default API endpoint configuration
   - Output directories with path selection
   - Theme selection (light/dark)

2. **Benchmark options**:
   - Default execution settings
   - Resource monitoring toggles
   - Parallel execution configuration
   - Timeout settings

3. **Export/import**:
   - Save and load configurations for consistent settings
   - Reset leaderboard if needed
   - Manage application data

## Workflow Examples

### Basic Model Evaluation

1. Open the Benchmark tab
2. Set your LM Studio model endpoint
3. Select desired programming tasks (categories, difficulties, languages)
4. Run the benchmark and monitor progress
5. Review the detailed results with color-coded metrics
6. Add results to leaderboard for future comparison

### Model Comparison

1. Benchmark multiple models using the same task selection
2. Go to the Leaderboard tab
3. Select the models you want to compare (2+)
4. Generate radar chart comparison visualizations
5. Examine relative strengths and weaknesses
6. Save comparison visualization for documentation

### Performance Tracking

1. Run regular benchmarks on your model as you improve it
2. Use the "View Model History" option in the Leaderboard tab
3. Visualize performance trends over time
4. Identify categories or languages that need improvement
5. Focus tuning efforts based on detailed analytics

### Resource Efficiency Analysis

1. Run benchmarks with resource monitoring enabled
2. Go to the Leaderboard tab
3. Use the "Visualize Resource Metrics" function
4. Compare memory usage, CPU utilization, or GPU usage
5. Identify models with the best performance/resource ratio

## Project Structure

```
benchmark_gui/
├── main.py                   # Main entry point
├── app.py                    # Main Application class
├── config.py                 # Configuration and constants
├── utils.py                  # Utility functions
├── styles.py                 # Theme and styling definitions
├── views/                    # UI components
│   ├── benchmark_view.py     # Benchmark tab UI
│   ├── visualize_view.py     # Visualization tab UI
│   ├── leaderboard_view.py   # Leaderboard tab UI
│   ├── settings_view.py      # Settings tab UI
│   └── dialogs/              # Dialog windows
│       ├── add_leaderboard_entry.py  # Add to leaderboard dialog
│       ├── entry_details.py  # Entry details dialog
│       ├── generate_report.py # Report generation dialog
│       ├── model_compare.py  # Model comparison dialog
│       ├── model_history.py  # Model history dialog
│       └── resource_viz.py   # Resource visualization dialog
└── controllers/              # Business logic
    ├── benchmark_controller.py   # Benchmark execution logic
    ├── visualize_controller.py   # Visualization generation logic
    ├── leaderboard_controller.py # Leaderboard management logic
    └── settings_controller.py    # Settings and configuration logic
```

## Key Features

### Enhanced Benchmark Execution
- Real-time progress tracking with detailed logging
- Safe cancellation of running benchmarks
- Comprehensive error handling with specific guidance
- Resource monitoring for CPU, memory, and GPU

### Advanced Visualization
- Multiple visualization types for different analysis needs
- Intuitive navigation between visualizations
- Contextual interpretation guidance
- Easy saving and sharing options

### Comprehensive Leaderboard
- Track and compare models with multiple performance metrics
- Detailed entry analysis with performance breakdowns
- Model comparison with radar charts
- Performance history tracking over time
- Resource efficiency visualization
- Report generation in multiple formats

### Robust User Interface
- Intuitive tab-based navigation
- Modern and responsive design
- Consistent light and dark themes
- Tooltips and contextual help throughout
- Color-coded metrics for quick assessment

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the LM Studio Coding Benchmark tool
- Uses ttkbootstrap for modern UI styling
- Inspired by Shadcn design principles
- Matplotlib for visualization generation
- Pandas and NumPy for data handling
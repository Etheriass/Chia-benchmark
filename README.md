# Performance Profiling of the Chia Blockchain

This project was developed as part of the course **CS554 - Data-Intensive Computing** (Spring 2025, Illinois Institute of Technology).

It provides a complete benchmarking and performance analysis framework for the Chia blockchain's plotting process. The objective is to evaluate how key system parameters—such as thread count, number of buckets, memory usage, and compression levels—impact the performance of different plotting phases and resource utilization.

## Project Structure

### Directories
- `logs/`: Contains raw output logs from Chia plotter runs, parsed JSON files with phase and table timing, and CSV files capturing system resource metrics (CPU, memory, disk I/O).
- `plot/`: 
  - `final/`: Stores finalized plot files.
  - `temp/`: Stores temporary files generated during the plotting process.

### Scripts
- `benchmark_run.py`: Automates Chia plot creation over a grid of configurations (threads, buckets, compression levels).
- `benchmark_log_parser.py`: Parses Chia plotter logs and extracts structured timing data in JSON format.
- `benchmark_chia_plot.py`: Coordinates plotting execution and system resource monitoring.
- `benchmark_visualization.py`: Generates visualizations from parsed JSON and CSV files, including phase-by-phase timings and resource usage plots.

## Key Findings

Through empirical testing on $k=28$ and $k=32$ plots using the `chiapos` plotter, the following insights were observed:
- **Phase 1** is highly CPU-bound and sensitive to thread count. Increasing threads significantly reduces execution time for this phase.
- **Phase 3** is impacted by the number of buckets, with more buckets improving sorting efficiency and reducing runtime, especially on larger $k=32$ plots.
- Resource usage trends confirmed that disk throughput and memory behavior vary significantly across phases, depending on configuration.
- Compression levels (evaluated externally) trade off final plot size with compute requirements, and GPU-accelerated plotting (e.g., Bladebit CUDA) maintains stable performance up to moderate compression levels.

A detailed analysis of all benchmarks, methodology, and results is available in the final report:

> 📄 **Performance Profiling of the Chia Blockchain.pdf**

## Dependencies

To install all required packages, run:

```bash
pip install -r requirements.txt
```

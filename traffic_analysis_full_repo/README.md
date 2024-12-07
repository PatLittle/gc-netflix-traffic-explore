# Government Traffic Benchmark Analysis

This repository automates the analysis of network traffic paths between the Government of Canada networks and popular platforms like Netflix, YouTube, BBC, and CNN. It runs a traceroute, WHOIS lookup, and BGP path analysis using public tools and data sources.

## Features
- **Traceroute Analysis**: Logs network hops and latency.
- **WHOIS Lookup**: Determines ownership of IP addresses.
- **Synthetic Probing**: Estimates traffic volume by downloading small files.
- **Visualization**: Generates bar charts and choropleth maps.

## Setup
1. Clone the repository:
    ```bash
    git clone <repo-link>
    ```
2. Run the script locally:
    ```bash
    python benchmark_traffic_analysis.py
    ```
3. Outputs are saved in the `output/` folder.

## GitHub Actions
The script runs daily and commits updated outputs back to the repository automatically.
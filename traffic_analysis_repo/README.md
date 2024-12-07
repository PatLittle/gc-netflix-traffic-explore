# Government Traffic Benchmark Analysis

This repository automates the analysis of network traffic paths between the Government of Canada networks and popular platforms like Netflix, YouTube, BBC, and CNN. It runs a traceroute, WHOIS lookup, and BGP path analysis using public tools and data sources.

## Repository Structure
```
.
├── benchmark_traffic_analysis.py  # Script
├── input/
│   ├── gov_asns.txt               # List of Government of Canada ASNs
│   ├── platforms.json             # List of domains to benchmark
├── output/                        # Directory to store results
├── .github/
│   └── workflows/
│       └── run_analysis.yml       # GitHub Actions workflow
└── README.md                      # Instructions
```

## How It Works
1. **Inputs**:
   - Government of Canada ASNs (in `input/gov_asns.txt`)
   - Domains of platforms to benchmark (in `input/platforms.json`)

2. **Outputs**:
   - Traceroute logs, WHOIS data, and BGP route files stored in `output/`.

3. **Automation**:
   - Runs daily using GitHub Actions and commits results back to the repository.

## How to Set Up
1. Clone this repository.
2. Push it to your GitHub account.
3. Modify `gov_asns.txt` and `platforms.json` as needed.

## Dependencies
- Python 3.x
- Tools: `traceroute`, `dig`
- Libraries: `requests`, `ipwhois`

## Running Locally
```bash
pip install requests ipwhois
python benchmark_traffic_analysis.py
```
import requests, subprocess, json, os, time
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from ipwhois import IPWhois

INPUT_ASNS = "input/gov_asns.txt"
INPUT_PLATFORMS = "input/platforms.json"
OUTPUT_DIR = "output"
RIPESTAT_API = 'https://stat.ripe.net/data/bgp-updates/data.json'

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read ASNs
with open(INPUT_ASNS) as f:
    GOV_ASNS = [line.strip() for line in f.readlines()]

# Read Platforms
with open(INPUT_PLATFORMS) as f:
    PLATFORMS = json.load(f)

def write_output(file, data):
    with open(f"{OUTPUT_DIR}/{file}", "w") as f:
        f.write(data)

def get_asn_routes(asn):
    print(f"Fetching BGP routes for ASN {asn}...")
    response = requests.get(f"{RIPESTAT_API}?resource={asn}")
    if response.status_code == 200:
        result = json.dumps(response.json(), indent=2)
        write_output(f"bgp_routes_{asn}.json", result)

def perform_traceroute(domain):
    print(f"Running traceroute to {domain}...")
    result = subprocess.run(['traceroute', domain], capture_output=True, text=True)
    write_output(f"traceroute_{domain.replace('.', '_')}.txt", result.stdout)

def resolve_and_whois(domain):
    print(f"Resolving IP and fetching WHOIS for {domain}...")
    try:
        ip = subprocess.check_output(['dig', '+short', domain]).decode().strip().split('\n')[0]
        if ip:
            obj = IPWhois(ip)
            result = json.dumps(obj.lookup_rdap(), indent=2)
            write_output(f"whois_{domain.replace('.', '_')}.json", result)
    except Exception as e:
        print(f"Error resolving domain {domain}: {e}")

# Visualization Code
def visualize_synthetic_results():
    print("Visualizing synthetic traffic results...")
    synthetic_files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("synthetic_probe")]
    for file in synthetic_files:
        with open(f"{OUTPUT_DIR}/{file}", "r") as f:
            data = json.load(f)
            domain = file.replace("synthetic_probe_", "").replace(".json", "").title()
            urls = [item['url'] for item in data]
            sizes = [item['size_kb'] for item in data]
            durations = [item['duration_sec'] for item in data]
            plt.figure(figsize=(10, 6))
            plt.bar(urls, sizes, color='b', alpha=0.7)
            plt.xlabel("URL")
            plt.ylabel("Size (KB)")
            plt.title(f"Traffic Size for {domain}")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(f"{OUTPUT_DIR}/{domain}_size.png")
            plt.close()

if __name__ == "__main__":
    for asn in GOV_ASNS:
        get_asn_routes(asn)
    for platform, domains in PLATFORMS.items():
        for domain in domains:
            perform_traceroute(domain)
            resolve_and_whois(domain)
    visualize_synthetic_results()
import requests, subprocess, json, os
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

if __name__ == "__main__":
    for asn in GOV_ASNS:
        get_asn_routes(asn)

    for platform, domains in PLATFORMS.items():
        for domain in domains:
            perform_traceroute(domain)
            resolve_and_whois(domain)
import time
import requests

# Constants
OUTPUT_DIR = "output"
SYNTHETIC_DOMAINS = {
    "Netflix": ["https://www.netflix.com/favicon.ico"],
    "YouTube": ["https://www.youtube.com/favicon.ico"],
    "BBC": ["https://www.bbc.com/favicon.ico"],
    "CNN": ["https://www.cnn.com/favicon.ico"]
}

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

def probe_synthetic_traffic(domain, urls):
    print(f"Probing traffic volume for {domain}...")
    results = []
    for url in urls:
        try:
            start_time = time.time()
            response = requests.get(url, stream=True)
            size = sum(len(chunk) for chunk in response.iter_content(chunk_size=1024))
            duration = time.time() - start_time
            result = {
                "url": url,
                "status_code": response.status_code,
                "size_kb": size / 1024,
                "duration_sec": duration
            }
            results.append(result)
            print(f"URL: {url} | Size: {size / 1024:.2f} KB | Duration: {duration:.2f} sec")
        except Exception as e:
            print(f"Failed to probe {url}: {e}")
    
    # Write to file
    with open(f"{OUTPUT_DIR}/synthetic_probe_{domain.lower()}.json", "w") as f:
        json.dump(results, f, indent=2)

# Main execution
if __name__ == "__main__":
    for domain, urls in SYNTHETIC_DOMAINS.items():
        probe_synthetic_traffic(domain, urls)

import matplotlib.pyplot as plt

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
            
            # Visualization: Size vs Duration
            plt.figure(figsize=(10, 6))
            plt.bar(urls, sizes, color='b', alpha=0.7, label="Size (KB)")
            plt.xlabel("URL")
            plt.ylabel("Size (KB)")
            plt.title(f"Traffic Size for {domain}")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(f"{OUTPUT_DIR}/{domain}_size.png")
            plt.close()

            # Visualization: Response Time
            plt.figure(figsize=(10, 6))
            plt.bar(urls, durations, color='g', alpha=0.7, label="Duration (sec)")
            plt.xlabel("URL")
            plt.ylabel("Duration (Seconds)")
            plt.title(f"Response Time for {domain}")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(f"{OUTPUT_DIR}/{domain}_duration.png")
            plt.close()

if __name__ == "__main__":
    visualize_synthetic_results()

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

def generate_choropleth_maps():
    print("Generating choropleth maps for WHOIS data...")
    whois_files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("whois")]
    country_counts = {}

    # Aggregate WHOIS country data
    for file in whois_files:
        with open(f"{OUTPUT_DIR}/{file}", "r") as f:
            data = json.load(f)
            try:
                country = data.get("network", {}).get("country", "Unknown")
                country_counts[country] = country_counts.get(country, 0) + 1
            except Exception as e:
                print(f"Failed to process {file}: {e}")

    # Convert to DataFrame
    country_df = pd.DataFrame(list(country_counts.items()), columns=["Country", "Count"])
    country_df = country_df.replace({"Unknown": None}).dropna()

    # Load world map from GeoPandas
    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

    # Merge data with GeoPandas
    world = world.merge(country_df, how="left", left_on="iso_a2", right_on="Country")
    world["Count"] = world["Count"].fillna(0)

    # Plot choropleth map
    plt.figure(figsize=(15, 10))
    world.boundary.plot(linewidth=1, color="k")
    world.plot(column="Count", cmap="Oranges", legend=True, edgecolor="k", linewidth=0.4)
    plt.title("WHOIS Network Distribution by Country")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/whois_choropleth_map.png")
    plt.close()
    print("Choropleth map saved.")

if __name__ == "__main__":
    generate_choropleth_maps()

import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

def generate_canada_request_map():
    print("Generating Canada-specific request volume map...")
    # Load Canada provinces/shapefiles
    canada = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    canada = canada[canada['name'] == 'Canada']

    # Mock request data per region (smallest available subdivision: provinces)
    # Replace this with actual traffic data aggregation if available
    province_data = {
        'Ontario': 150, 'Quebec': 120, 'British Columbia': 90, 
        'Alberta': 80, 'Manitoba': 50, 'Saskatchewan': 40, 
        'Nova Scotia': 30, 'New Brunswick': 20, 'Newfoundland and Labrador': 10,
        'Prince Edward Island': 5, 'Yukon': 2, 'Northwest Territories': 1, 
        'Nunavut': 1
    }

    # Canada provinces geometry data
    provinces = gpd.read_file("https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/canada-provinces.geojson")

    # Merge mock data with geometries
    province_df = provinces.copy()
    province_df['Request_Volume'] = province_df['name'].map(province_data).fillna(0)

    # Plot the choropleth
    plt.figure(figsize=(15, 10))
    province_df.plot(column="Request_Volume", cmap="Blues", legend=True, edgecolor="k", linewidth=0.5)
    plt.title("Approximated Request Volume to Netflix by Province")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/canada_request_map.png")
    plt.close()
    print("Canada request map saved.")

if __name__ == "__main__":
    generate_canada_request_map()

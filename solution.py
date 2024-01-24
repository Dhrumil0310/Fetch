import yaml
import requests
import time
from urllib.parse import urlparse

def readConfig(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def groupEndpoints(endpoints):
    group = {}
    for endpoint in endpoints:
        url = endpoint['url']
        domain = urlparse(url).netloc
        if domain not in group:
            group[domain] = []
        group[domain].append(endpoint)
    return group

def HealthCheck(endpoints):
    results = []

    for endpoint in endpoints:
        url = endpoint['url']
        method = endpoint.get('method', 'GET')
        headers = endpoint.get('headers', {})
        body = endpoint.get('body', None)

        try:
            start_time = time.time()
            response = requests.request(method, url, headers=headers, json=body, timeout=5)
            latency = time.time() - start_time
            print("latency", latency, "response:", response)

            if response.status_code >= 200 and response.status_code < 300 and latency < 0.5:
                results.append('UP')
            else:
                results.append('DOWN')
        except requests.RequestException:
            results.append('DOWN')

    return results

def calculateAvailability(results, cumulativeResults):
    totalRequests = len(results)
    up_count = results.count('UP')

    cumulativeResults['totalRequests'] += totalRequests
    cumulativeResults['up_count'] += up_count

    print("TotalRequests =", cumulativeResults['totalRequests'], "UpCount =", cumulativeResults['up_count'])

    return round(100 * (cumulativeResults['up_count'] / cumulativeResults['totalRequests'])) if cumulativeResults['totalRequests'] > 0 else 0

def displayCumulativeAvailability(cumulativeResults, domain):
    cumulative_percentage = round(100 * (cumulativeResults['up_count'] / cumulativeResults['totalRequests'])) if cumulativeResults['totalRequests'] > 0 else 0
    print(f"{domain} has cumulative availability: {cumulative_percentage}%")

def main(file_path):
    try:
        cumulativeResults = {}

        while True:
            AllEndpoints = readConfig(file_path)
            group = groupEndpoints(AllEndpoints)

            for domain, endpoints in group.items():
                if domain not in cumulativeResults:
                    cumulativeResults[domain] = {'totalRequests': 0, 'up_count': 0}
                results = HealthCheck(endpoints)
                x = calculateAvailability(results, cumulativeResults[domain])
                displayCumulativeAvailability(cumulativeResults[domain], domain)

            time.sleep(15)
    except KeyboardInterrupt:
        print("\nProgram manually exited.")

if __name__ == "__main__":
    file_path = "config.yaml"
    main(file_path)

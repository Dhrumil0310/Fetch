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

def calculateAvailability(results):
    totalRequests = len(results)
    up_count = results.count('UP')
    return round(100 * (up_count / totalRequests)) if totalRequests > 0 else 0

def displayAvailability(availability):
    for domain, percentage in availability.items():
        print(f"{domain} has {percentage}% availability percentage")

def main(file_path):
    try:
        while True:
            AllEndpoints = readConfig(file_path)
            group = groupEndpoints(AllEndpoints)
            availability = {}

            for domain, endpoints in group.items():
                results = HealthCheck(endpoints)
                x = calculateAvailability(results)
                availability[domain] = x
                displayAvailability({domain: x})

            time.sleep(15)
    except KeyboardInterrupt:
        print("\nProgram manually exited.")

if __name__ == "__main__":
    file_path = "config.yaml"
    main(file_path)

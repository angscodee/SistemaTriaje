"""Health check script for all services"""

import sys
import httpx


def check_service(name: str, url: str) -> bool:
    """Check if a service is healthy"""
    try:
        response = httpx.get(url, timeout=5.0)
        if response.status_code == 200:
            print(f"✅ {name} is healthy")
            return True
        else:
            print(f"❌ {name} returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name} is not responding: {e}")
        return False


def main():
    """Check all services"""
    services = {
        "Backend": "http://localhost:8000/health",
        "Backend Ready": "http://localhost:8000/ready",
    }

    print("Checking services...")
    print("-" * 40)

    all_healthy = True
    for name, url in services.items():
        if not check_service(name, url):
            all_healthy = False

    print("-" * 40)
    if all_healthy:
        print("✅ All services are healthy")
        sys.exit(0)
    else:
        print("❌ Some services are not healthy")
        sys.exit(1)


if __name__ == "__main__":
    main()

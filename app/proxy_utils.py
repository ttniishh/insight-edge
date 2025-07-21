# proxy_utils.py
import requests
import random

def get_proxy():
    try:
        url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=3000&country=all&ssl=all&anonymity=all"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        proxies = response.text.strip().split("\n")
        proxies = [p.strip() for p in proxies if p.strip()]
        
        if not proxies:
            print("⚠️ No proxies fetched.")
            return None
        
        selected = random.choice(proxies)
        return {"http": f"http://{selected}", "https": f"http://{selected}"}
    
    except Exception as e:
        print(f"❌ Failed to fetch proxies: {e}")
        return None

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

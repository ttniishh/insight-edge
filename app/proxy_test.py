# proxy_test.py
import requests
from proxy_utils import get_proxy, get_headers

proxy = get_proxy()
if proxy:
    try:
        print(f"🌐 Testing proxy: {proxy}")
        res = requests.get("http://httpbin.org/ip", headers=get_headers(), proxies=proxy, timeout=10)
        print(f"[✅] Proxy Works! IP: {res.json()}")
    except Exception as e:
        print(f"[❌] Proxy Failed -> {e}")
else:
    print("⚠️ No proxy available.")

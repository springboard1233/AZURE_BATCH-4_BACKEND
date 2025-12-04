import urllib.request
import urllib.error

try:
    print(urllib.request.urlopen('http://localhost:5000/api/forecast_7').read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")

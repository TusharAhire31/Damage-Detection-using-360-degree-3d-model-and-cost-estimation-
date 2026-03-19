# garage_locator.py
import requests

def find_nearby_garages(pincode, max_results=3):
    try:
        url = f"https://nominatim.openstreetmap.org/search?postalcode={pincode}&format=json&limit=1"
        resp = requests.get(url, headers={"User-Agent":"capstone-app"}, timeout=8).json()
        place = resp[0].get("display_name","Area "+pincode) if resp else ("Area "+pincode)
    except Exception:
        place = "Area "+pincode
    garages = [
        {"name":f"AutoFix {pincode}", "address":place, "contact":"+91 9876543210"},
        {"name":f"Elite Garage {pincode}", "address":place, "contact":"+91 9988776655"},
        {"name":f"QuickFix {pincode}", "address":place, "contact":"+91 9123456789"},
    ]
    return garages[:max_results]

# firebase_client.py
import requests
import json

# Set your Firebase Realtime Database base URL here (end with a slash), e.g.
# FIREBASE_DB_URL = 'https://your-project-id-default-rtdb.firebaseio.com/'
FIREBASE_DB_URL = ''  # <-- SET THIS for real-time features

class FirebaseClient:
    def __init__(self, base_url=FIREBASE_DB_URL):
        self.base = base_url.rstrip('/')

    def push_order(self, vendor_id, order):
        if not self.base:
            return None
        url = f"{self.base}/orders/{vendor_id}.json"
        res = requests.post(url, json=order)
        if res.status_code in (200,201):
            return res.json()
        else:
            print('firebase push error', res.status_code, res.text)
            return None

    def get_orders(self, vendor_id):
        if not self.base:
            return None
        url = f"{self.base}/orders/{vendor_id}.json"
        res = requests.get(url)
        if res.status_code==200:
            return res.json() or {}
        else:
            print('firebase get error', res.status_code, res.text)
            return None

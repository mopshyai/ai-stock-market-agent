
import os
import requests

def post_to_slack(message: str):
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook:
        return False
    try:
        r = requests.post(webhook, json={"text": message})
        return r.ok
    except:
        return False

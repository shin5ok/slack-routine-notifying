import requests
import os
import json

SLACK_BASE_URL = "https://slack.com/api"
SLACK_OAUTH_TOKEN = os.environ.get("SLACK_OAUTH_TOKEN")
SLACK_CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")
OLDEST_DAYS = os.environ.get("OLDEST_DAYS", "60")
EMAIL_DOMAIN = os.environ.get("EMAIL_DOMAIN", "google.com")
DEBUG = "DEBUG" in os.environ

header_auth = {
    "Authorization": f"Bearer {str(SLACK_OAUTH_TOKEN)}",
}

def get_userlist() -> dict:

    payload = {
        "channel": SLACK_CHANNEL_ID,
    }

    slack_url = SLACK_BASE_URL + "/users.list"
    try:
        response = requests.get(slack_url, headers=header_auth, params=payload)
        if not response.ok:
            raise Exception(f"{slack_url} was {response.status_code}")
    except Exception as e:
        print(e)
    json_data = response.json()

    members = {}
    for v in json_data["members"]:
        if "profile" in v:
            if "email" in v["profile"]:
                domain = v["profile"]["email"].split("@")[1]
                if domain != EMAIL_DOMAIN:
                    continue

        if "real_name" in v:
            if v["real_name"]:
                members[v["id"]] = v["real_name"]
            if DEBUG:
                print(json.dumps(v["real_name"], indent=2))
    
    return members

def get_history(path: str = "/conversations.history") -> (dict, dict):

    from datetime import datetime, timedelta

    oldest = datetime.now() + timedelta(days=int("-" + OLDEST_DAYS))

    payload = {
        "channel": SLACK_CHANNEL_ID,
        "oldest": oldest.timestamp(),
        # "limit": 9999,
    }

    slack_url = SLACK_BASE_URL + path
    try:
        response = requests.get(slack_url, headers=header_auth, params=payload)
        if not response.ok:
            raise Exception(f"{slack_url} was {response.status_code}")
        if response.status_code != 200:
            raise Exception(f"{slack_url} was {response.status_code}")

    except Exception as e:
        print(e)

    json_data = response.json()
    messages = json_data['messages']

    if DEBUG:
        print(json.dumps(messages, indent=2))

    r = {}
    for entry in messages:
        if entry["type"] != "message":
            continue
        if not "client_msg_id" in entry:
            continue

        users = []
        users.append(entry['user'])

        if "reply_users" in entry:
            users += entry["reply_users"]

        for user in users:
            if user in r:
                r[user] += 1
            else:
                r[user] = 1

    # {'UEVSMCELV': 20, 'UEV513F3L': 11, 'U05H8PVGYGL': 5, 'UETQ7B5FU': 9, 'UQ1N1V8R1': 8}
    return r, {"OLDEST_DAYS": OLDEST_DAYS}

def main(exporter_class):
    hists, info = get_history()
    u = get_userlist()

    data = {}
    for k, v in sorted(hists.items(), key=lambda x: x[1], reverse=True):
        if not k in u:
            continue

        if not DEBUG:
            data[u[k]] = v
            u.pop(k)
 
    for e in u.values():
        data[e] = 0

    exporter_class(data, info).send()

if __name__ == "__main__":
    if not DEBUG:
        import exporter
        main(exporter.GoogleChatExporter)

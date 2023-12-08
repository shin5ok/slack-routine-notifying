import requests
import os
import json
from typing import Any

SLACK_BASE_URL = "https://slack.com/api"
SLACK_OAUTH_TOKEN = os.environ.get("SLACK_OAUTH_TOKEN")
SLACK_CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")
OLDEST_DAYS = os.environ.get("OLDEST_DAYS", "60")
EMAIL_DOMAIN = os.environ.get("EMAIL_DOMAIN", "google.com")
TEMPLATE = os.environ.get("TEMPLATE")
LLM_TEMPLATE = os.environ.get("LLM_TEMPLATE")
MODEL_NAME = os.environ.get("MODEL_NAME")
DEBUG = "DEBUG" in os.environ

header_auth = {
    "Authorization": f"Bearer {str(SLACK_OAUTH_TOKEN)}",
}

def get_public_channels() -> list[str]:
    slack_url = SLACK_BASE_URL + "/conversations.list"

    try:
        response = requests.get(slack_url, headers=header_auth, params={})
        if not response.ok:
            raise Exception(f"{slack_url} was {response.status_code}")
    except Exception as e:
        print(e)

    json_data = response.json()
    return [v['id'] for v in json_data['channels'] if not v['is_private']]


def get_userlist() -> dict[str, dict]:

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

    if json_data["ok"] != True:
        print(json.dumps(json_data, indent=2))
        raise Exception("ok is not true")

    if not "members" in json_data:
        print(json.dumps(json_data, indent=2))
        raise Exception("members not found")

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

def get_history(path: str = "/conversations.history") -> (dict[str, int], dict[str, Any]):

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

    if json_data["ok"] != True:
        print(json.dumps(json_data, indent=2))
        raise Exception("ok is not true")

    messages = json_data['messages']

    if DEBUG:
        print(json.dumps(messages, indent=2))

    last_remark_by_user: dict = {}
    r: dict = {}
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

            from datetime import datetime as dt
            import datetime
            if not user in last_remark_by_user:
                ts = dt.fromtimestamp(float(entry['ts']), datetime.timezone(datetime.timedelta(hours=9)))
                last_remark_by_user[user] = ts

    # {'UEVSMCELV': 20, 'UEV513F3L': 11, 'U05H8PVGYGL': 5, 'UETQ7B5FU': 9, 'UQ1N1V8R1': 8}
    return r, {
                "OLDEST_DAYS": OLDEST_DAYS,
                "LAST_REMARK_BY_USER": last_remark_by_user,
            }

def main(exporter_class, is_test=False):
    hists, info = get_history()
    u = get_userlist()

    data = {}
    for k, v in sorted(hists.items(), key=lambda x: x[1], reverse=True):
        if not k in u:
            continue

        data[u[k]] = [v, k]
        u.pop(k)

    for k, v in u.items():
        data[v] = [0, k]

    exporter_class(data, info, LLM_TEMPLATE, MODEL_NAME).send(is_test)

if __name__ == "__main__":
    import exporter
    main(exporter.GoogleChatExporterWithLLM)

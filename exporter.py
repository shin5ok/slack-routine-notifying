import abc
class BaseExporter(abc.ABC):

    def __init__(self, data: dict, info: dict) -> None:
        from dotenv import load_dotenv
        import os
        from os.path import join, dirname

        self.data = data

    @abc.abstractmethod
    def send(self) -> bool:
        ...

class GoogleChatExporter(BaseExporter):

    def __init__(self, data: dict, info: dict) -> None:
        from dotenv import load_dotenv
        import os
        from os.path import join, dirname

        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        self.data = data
        self.limit = os.environ.get("ASK_MEMBER_LIMIT", "2")
        self.webhook = os.environ.get("WEBHOOK_URL")
        self.members_regexp = os.environ.get("MEMBERS")
        self.info = info

    def send(self) -> bool:
        import requests
        import json

        post_data = self._gen_data()
        response = requests.post(self.webhook, data=json.dumps({"text":post_data}), headers={"Content-Type": "application/json"})
        return response.content
    

    def _gen_data(self) -> str:
        import re
        
        data = self.data
        limit = int(self.limit)

        regexp = re.compile(self.members_regexp, flags=re.IGNORECASE)
        
        actual = f"直近{self.info['OLDEST_DAYS']}日の これまでの実績\n"
        actual += "```\n"
        for k, v in data.items():
            if not regexp.match(k):
                continue
            actual += f"{k}さん {v}回\n"
        actual += "```\n"

        gen = ""
        for k, v in sorted(data.items(), key=lambda x: x[1]):
            if not regexp.match(k):
                continue

            if limit > 0:
                gen += f"*{k}さん*, "
            limit -= 1

        gen += "\n"

        gen += "\nなにか GEM Slack にポストお願いします！"
        gen += "\nもちろんネタある方はどなたでも〜"
        gen += "\n<users/all>"

        gen += "\n\n" + actual
        return gen




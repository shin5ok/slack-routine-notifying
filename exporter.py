import abc
from typing import Union


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
    def __init__(self, data: dict, info: dict, template: str) -> None:
        from dotenv import load_dotenv
        import os
        from os.path import join, dirname

        dotenv_path = "/config/.env"
        load_dotenv(dotenv_path)

        self.data = data
        self.limit = os.environ.get("ASK_MEMBER_LIMIT", "2")
        self.webhook = os.environ.get("WEBHOOK_URL")
        self.members_regexp = os.environ.get("MEMBERS")
        self.info = info
        self.template = template

    def send(self) -> bool:
        import requests
        import json

        post_data = self._gen_data()
        response = requests.post(
            self.webhook,
            data=json.dumps({"text": post_data}),
            headers={"Content-Type": "application/json"},
        )
        return response.content

    def _gen_data(self) -> str:
        import re
        from datetime import datetime as dt
        import datetime

        RECENT_DAYS: int = 7

        data = self.data
        limit = int(self.limit)

        last_remark_by_user: dict = self.info.get("LAST_REMARK_BY_USER")

        regexp = re.compile(self.members_regexp, flags=re.IGNORECASE)

        from texttable import Texttable

        actual = f"直近{self.info['OLDEST_DAYS']}日の これまでの実績\n"
        actual += "```\n"
        rows = []

        for k, v in data.items():
            if not regexp.match(k):
                continue
            row = [f"{k}さん", f"{v[0]}回"]
            actual += f"{k}さん {v[0]}回"
            if v[1] in last_remark_by_user:
                actual += f", 最終投稿日 {last_remark_by_user[v[1]].strftime('%Y/%m/%d')}"
                row.append(last_remark_by_user[v[1]].strftime("%Y/%m/%d"))
            else:
                actual += ", 投稿なし"
                row.append("投稿なし")
            actual += "\n"
            rows.append(row)
        actual += "```\n"

        gen = ""
        now = dt.now(datetime.timezone(datetime.timedelta(hours=9)))
        for k, v in sorted(data.items(), key=lambda x: x[1][0]):
            if not regexp.match(k):
                continue

            # skip if user posted something in RECENT_DAYS
            if v[1] in last_remark_by_user:
                ts = last_remark_by_user[v[1]]
                delta = now - ts
                if delta.days < RECENT_DAYS:
                    continue

            if limit > 0:
                gen += f"*{k}さん*, "
            limit -= 1

        if gen == "":
            gen += "*みなさま*\n"
            gen += "（該当する人がいませんでした）"
        else:
            if self.template:
                with open(self.template) as f:
                    gen += f.read()

            t = Texttable()
            t.set_deco(Texttable.HEADER)
            t.set_cols_dtype(["t", "t", "t"])
            rows[:0] = [["名前", "実績", "最終投稿日"]]
            t.add_rows(rows)

            gen += "\n\n" + "```\n" + t.draw() + "\n```\n"

        gen += "\n"
        return gen



class GoogleChatExporterWithLLM(GoogleChatExporter):

    def get_llm(self, message: str):
        from langchain.llms import VertexAI
        llm_template = "llm_template.txt"
        with open(llm_template) as f:
            data = f.read()
        data = data.replace("##data##", message)

        print(data)

        from usellm import LLM
        return LLM().choose_candidates(data)

    def _gen_data(self) -> str:
        import re
        from datetime import datetime as dt
        import datetime

        RECENT_DAYS: int = 7

        data = self.data
        limit = int(self.limit)

        last_remark_by_user: Union[dict, None] = self.info.get("LAST_REMARK_BY_USER")

        regexp = re.compile(self.members_regexp, flags=re.IGNORECASE)

        from texttable import Texttable

        actual_title = f"直近{self.info['OLDEST_DAYS']}日の これまでの実績\n"

        rows = []

        for k, v in data.items():
            if not regexp.match(k):
                continue
            row = [f"{k}さん", f"{v[0]}回"]
            if v[1] in last_remark_by_user:
                row.append(last_remark_by_user[v[1]].strftime("%Y/%m/%d"))
            else:
                row.append("投稿なし")
            rows.append(row)

        gen = ""
        now = dt.now(datetime.timezone(datetime.timedelta(hours=9)))
        for k, v in sorted(data.items(), key=lambda x: x[1][0]):
            if not regexp.match(k):
                continue

            # skip if user posted something in RECENT_DAYS
            if v[1] in last_remark_by_user:
                ts = last_remark_by_user[v[1]]
                delta = now - ts
                if delta.days < RECENT_DAYS:
                    continue

        if self.template:
            with open(self.template) as f:
                gen += f.read()

        t = Texttable()

        t.set_deco(Texttable.HEADER)
        t.set_cols_dtype(["t", "t", "t"])
        rows[:0] = [["名前", "実績", "最終投稿日"]]
        t.add_rows(rows)

        gen += "\n"
        gen += t.draw()

        result = self.get_llm(gen)

        result += f"""
{actual_title}
```
{t.draw()}
```
<users/all>

"""
        return result


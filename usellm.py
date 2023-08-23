import langchain
from pydantic import BaseModel

from google.cloud import aiplatform
from langchain.chat_models import ChatVertexAI
from langchain.llms import VertexAI
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.schema import HumanMessage, SystemMessage

class LLM:

    def __init__(self):
        self.llm = VertexAI()

    def choose_candidates(self, template: str, params: list = []):
        prompt = PromptTemplate(
           template = template,
           input_variables=params,
        ) 
        text = prompt.format()
        return self.llm.predict(text)


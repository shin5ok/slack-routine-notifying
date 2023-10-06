import langchain
from pydantic import BaseModel

from google.cloud import aiplatform
from langchain.chat_models import ChatVertexAI
from langchain.llms import VertexAI
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models import ChatVertexAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

llm = None
memory = ConversationBufferMemory()

class LLM:

    def __init__(self):

        parameters = {
                "temperature": 0.2,
                # "max_output_tokens": 1024,
                "top_p": 0.8,
                "top_k": 40,
            }

        global llm, memory
        chat_model = ConversationChain(
            llm=ChatVertexAI(**parameters),
            verbose=True,
            memory=memory,
        )
        self.llm = chat_model

    def choose_candidates(self, template: str, params: list = []):
        prompt = PromptTemplate(
           template = template,
           input_variables=params,
        ) 
        text = prompt.format()
        return self.llm.predict(input=text)
        # return self.llm.predict(text)


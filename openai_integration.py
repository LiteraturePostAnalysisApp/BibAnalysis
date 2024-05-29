from openai import OpenAI
import os
from rich import print
from config import jsonexample
class GptChatBot():
    def __init__(self, apikey:str=None, baseurl:str="https://api.openai.com", model:str="gpt-4o"):
        if apikey is None:
            apikey = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=apikey, base_url=baseurl)
        self.model = model
        self.jsontemplate = jsonexample
        self._chathistory = [{"role": "System", "content":self.assistant_prompt}]

    @property
    def assistant_prompt(self):
        jsontemplate = self.jsontemplate
        return f"In order to gather structured information, I would like you, as a bridge seismic and machine learning expert, to help me with the analysis and summarization of the uploaded literature. I will tip you 10000$ for a perfect answer. Please be sure to read each article entirety. If there are no information for this field, please fill in 'Oops!' and remind user. Summarize the information and directly output it in code interpreter by import json and combine results as a JSON file for me to download  without providing any explanations(only include the value, excluding description). The filename should always be 'Article_Summary_n.json'. Here are the example:{jsontemplate}"

    def get_response(self, message:str,jsonmode:bool=False):
        """Get the response from the chatbot."""
        # 后续可能需要添加JSON模式
        if jsonmode:
            raise NotImplementedError
        
        new_message = {"role": "user", "content": message}
        self._chathistory += [new_message]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self._chathistory,
            stream=True,
        )
        if isinstance(response, dict):
            response_text = response.choices[0].message.content
            self._chathistory += [{"role": "Assistant", "content": response_text}]
            return response_text
        else:
            response_text = ""
            for token in response:
                content = token.choices[0].delta.content
                if content is not None:
                    response_text += content
            self._chathistory += [{"role": "Assistant", "content": response_text}]
            return response_text
        
    def add_pdf_to_chat(self, pdf_path:str):
        uploaded_file = self.client.files.create(
            file=open(pdf_path, "rb"),
            purpose="assistants"
        )
        return uploaded_file

if __name__ == "__main__":
    apikey = "sk-5Yw6uiLGjxo31WtdWJOqUwRVvLfLvOmAUpvYjhB7Q6yHGNmA"
    chatbot = GptChatBot(baseurl = "https://api.chatanywhere.com.cn")
    # response = chatbot.get_response("What is the capital of France?", jsonmode=False)
    # print(response)
    # pdf_id = chatbot.add_pdf_to_chat("example.pdf")
    # print(pdf_id)
    print(chatbot.assistant_prompt)

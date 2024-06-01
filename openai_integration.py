from openai import OpenAI
import os
from rich import print
from config import jsonexample
from loguru import logger

class GptChatBot():
    def __init__(self, apikey:str=None, baseurl:str="https://api.openai.com", model:str="gpt-4o"):
        if apikey is None:
            try:
                apikey = os.getenv("OPENAI_API_KEY")
            except ValueError:
                logger.exception("Environment Variable OPENAI_API_KEY Not Found.")
        self.client = OpenAI(api_key=apikey, base_url=baseurl)
        self.model = model
        logger.info(f"OpenAI Client Created with Model:{model}")
        self.jsontemplate = jsonexample
        self._chathistory = [{"role": "user", "content":self.assistant_prompt}]
        self.assistant = None
        self.vector_store_ids:list[int] = []

    def create_assistant(self, assistant_name:str="Journal Analyst Assistant", instructions:str = None, tools:list[dict] = [{"type": "file_search"}]):
        self.assistant = self.client.beta.assistants.create(
            name = assistant_name,
            instructions = instructions if instructions else self.assistant_prompt,
            model = self.model,
            tools = tools,
        )

    @property
    def assistant_prompt(self):
        jsontemplate = self.jsontemplate
        return f"In order to gather structured information, I would like you, as a bridge seismic and machine learning expert, to help me with the analysis and summarization of the uploaded literature. I will tip you 10000$ for a perfect answer. Please be sure to read each article entirety. If there are no information for this field, please fill in 'Oops!' and remind user. Summarize the information and directly output it in code interpreter by import json and combine results as a JSON file for me to download  without providing any explanations(only include the value, excluding description). The filename should always be 'Article_Summary_n.json'. Example:{jsontemplate}"

    def get_response(self, message:str,jsonmode:bool=False):
        """Get the response from the chatbot."""
        # 后续可能需要添加JSON模式
        if jsonmode:
            logger.info("Response in JSON mode.")
            raise NotImplementedError
        else:
            logger.info("Response in Text mode.")
        
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
        
    def add_pdf_to_vector_store(self, vector_store_id:int, file_paths:list[str]):
        """Add the pdf to the chat."""
        # 情参考https://platform.openai.com/docs/assistants/tools/file-search/vector-stores继续编写，尚未调通
        file_streams = [open(path, "rb") for path in file_paths]
        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id = vector_store_id, files=file_streams
        )
        
        # You can print the status and the file counts of the batch to see the result of this operation.
        logger.debug(f"File Batch Status:{file_batch.status}")
        logger.debug(f"File Batch File Counts:{file_batch.file_counts}")
        return file_batch
    
    def create_vector_store(self, vector_store_name:str):
        """Create the vector store."""
        vector_store = self.client.beta.vector_stores.create(name=vector_store_name)
        self.vector_store_ids.append(vector_store.id)
        logger.info(f"Vector Store Created with ID:{vector_store.id}")
        return vector_store.id
    
    def update_assistant(self):
        """Update the assistant."""
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            tool_resources={"file_search": {"vector_store_ids": self.vector_store_ids}},
        )
        logger.info(f"Assistant(id:{self.assistant.id}) Updated with Vector Store IDs:{self.vector_store_ids}")

if __name__ == "__main__":
    apikey = "your api key here"
    chatbot = GptChatBot(baseurl = "https://api.chatanywhere.com.cn")
    # response = chatbot.get_response("What is the capital of France?", jsonmode=False)
    # print(response)
    chatbot.create_assistant("Summary Assistant", "Please help me to summarize the article.", tools = ["file_search"])
    vec_id = chatbot.create_vector_store("reference articles")
    pdfpath = 'F:\Zotero\storage\FWUIG4RU\Zhang 等 - 2023 - Prediction of seismic acceleration response of precast segmental self-centering concrete filled stee.pdf'
    pdf_id = chatbot.add_pdf_to_vector_store(vec_id, [os.path.normpath(pdfpath)])
    print(pdf_id)
    chatbot.update_assistant()

    # print(chatbot.assistant_prompt)

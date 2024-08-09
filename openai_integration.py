import openai
import os
from rich import print
from config import jsonexample
from loguru import logger
import PyPDF2
from transformers import AutoTokenizer, AutoModel
import torch
class GptChatBot:
    def __init__(self, apikey: str = None, baseurl: str = "https://api.openai.com", model: str = "gpt-4o-mini"):
        self.api_key = apikey or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        # Set the base URL and API key for the OpenAI API
        openai.api_key = self.api_key
        openai.api_base = baseurl
        
        self.model = model
        logger.info(f"OpenAI Client Created with Model: {model}")
        self.jsontemplate = jsonexample
        self._chathistory = [{"role": "user", "content": self.assistant_prompt}]
        self.assistant = None
        self.vector_store_ids = []

    def create_assistant(self, assistant_name: str = "Journal Analyst Assistant", instructions: str = None, tools: list = [{"type": "file_search"}]):
        # Assuming you want to set up an assistant for some purpose, this is not directly supported by OpenAI's API, 
        # but I'll leave the method as it might relate to some custom functionality.
        logger.info(f"Assistant created with name: {assistant_name}")
        self.assistant = {"name": assistant_name, "instructions": instructions if instructions else self.assistant_prompt, "tools": tools}

    @property
    def assistant_prompt(self):
        jsontemplate = self.jsontemplate
        return f"In order to gather structured information, I would like you, as a bridge seismic and machine learning expert, to help me with the analysis and summarization of the uploaded literature. I will tip you 10000$ for a perfect answer. Please be sure to read each article entirely. If there are no information for this field, please fill in 'Oops!' and remind user. Summarize the information and directly output it in code interpreter by importing json and combining results as a JSON file for me to download without providing any explanations (only include the value, excluding description). The filename should always be 'Article_Summary_n.json'. Example: {jsontemplate}"

    def get_response(self, message: str, jsonmode: bool = False):
        """Get the response from the chatbot."""
        if jsonmode:
            logger.info("Response in JSON mode.")
            raise NotImplementedError
        else:
            logger.info("Response in Text mode.")
        
        new_message = {"role": "user", "content": message}
        self._chathistory.append(new_message)
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self._chathistory,
            stream=True,
        )
        response_text = ""
        for token in response:
            content = token['choices'][0]['delta'].get('content', '')
            response_text += content

        self._chathistory.append({"role": "assistant", "content": response_text})
        return response_text

    def add_pdf_to_vector_store(self, vector_store_id: int, file_paths: list[str]):
        """Add the pdf to the vector store."""
        file_streams = [open(path, "rb") for path in file_paths]
        # This is not supported in the OpenAI Python client, you might have custom logic here
        logger.debug(f"Mock: Added PDFs to vector store with ID: {vector_store_id}")
        return {"status": "mocked", "file_counts": len(file_paths)}
    
    def create_vector_store(self, vector_store_name: str):
        """Create the vector store."""
        # This is not supported in the OpenAI Python client, you might have custom logic here
        logger.info(f"Mock: Created vector store with name: {vector_store_name}")
        return 12345  # Mock ID

    def update_assistant(self):
        """Update the assistant."""
        # This would update your assistant with any new information
        logger.info(f"Mock: Updated assistant with ID: {self.assistant.get('id', 'unknown')} and vector stores: {self.vector_store_ids}")

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        从 PDF 文件中提取文本内容。
        Args:
            pdf_path (str): PDF 文件路径。
        Returns:
            str: 提取的文本内容。
        """
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text

    def vectorize_text(self, text: str) -> torch.Tensor:
        """
        将文本内容向量化。
        Args:
            text (str): 要向量化的文本。
        Returns:
            torch.Tensor: 向量化的文本表示。
        """
        tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            embeddings = model(**inputs).last_hidden_state[:, 0, :]
        return embeddings

    def store_vector(self, vector: torch.Tensor, metadata: dict):
        """
        存储向量及其元数据到 Pinecone。
        Args:
            vector (torch.Tensor): 要存储的向量。
            metadata (dict): 与向量关联的元数据。
        """
        vector_id = metadata['doi']  # 使用 DOI 作为向量 ID
        self.index.upsert([(vector_id, vector.tolist(), metadata)])

    def add_pdf_to_chat(self, pdf_path: str):
        """
        Extract text from the PDF, summarize it, and send it to the chat.
        
        Args:
            pdf_path (str): Path to the PDF file.
        """
        # Step 1: Extract text from the PDF
        text = self.extract_text_from_pdf(pdf_path)
        
        # Step 2: Send the text to the GPT model for summarization
        summary_prompt = f"Please summarize the following text extracted from a PDF:\n\n{text[:1500]}\n\n... [truncated]"
        summary = self.get_response(summary_prompt)
        
        # Step 3: Store the summary in the chat history
        self._chathistory.append({"role": "assistant", "content": summary})
        
        logger.info(f"Summary of the PDF has been added to the chat history.")
        return summary

if __name__ == "__main__":

    apikey = "sk-WQdW2yrWgKIMTKV6LOYvxFUVlVNX9Gs6nQv5htHzFQmKsyYh"
    chatbot = GptChatBot(apikey=apikey, baseurl="https://api.deepbricks.ai/v1/")
    chatbot.create_assistant("Summary Assistant", "Please help me to summarize the article.", tools=[{"type": "file_search"}])

    vec_id = chatbot.create_vector_store("reference articles")
    #pdf_id = chatbot.add_pdf_to_vector_store(vec_id, [os.path.normpath(pdfpath)])
    #print(pdf_id)
    pdfpath = r"C:\Users\22525\Zotero\storage\HXQKFPME\Ali 等 - 2024 - A Simplified Approach for Dynamic Analysis of Susp.pdf"
    summary = chatbot.add_pdf_to_chat(pdfpath)
    print(summary)
    chatbot.update_assistant()

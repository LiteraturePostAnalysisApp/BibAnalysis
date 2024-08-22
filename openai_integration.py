import openai
import os
from rich import print
from config import jsonexample  # 导入jsonexample模板
from loguru import logger
import pdfplumber
from transformers import AutoTokenizer, AutoModel
import torch
from pinecone import Pinecone, ServerlessSpec
import json

class GptChatBot:
    def __init__(self, apikey: str = None, baseurl: str = "https://api.openai.com", model: str = "gpt-4o-mini", pinecone_key: str = None, pinecone_env: str = "us-west1-gcp"):
        self.api_key = apikey or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        openai.api_key = self.api_key
        openai.api_base = baseurl
        
        self.model = model
        logger.info(f"OpenAI Client Created with Model: {model}")
        self.jsontemplate = jsonexample
        self._chathistory = [{"role": "user", "content": self.assistant_prompt}]
        self.assistant = None
        self.vector_store_ids = []
        
        if pinecone_key:
            self.pinecone = Pinecone(api_key=pinecone_key)
            self.index = None
            logger.info("Pinecone initialized.")
        else:
            logger.warning("Pinecone API key not provided. Vector storage won't be available.")

    def create_assistant(self, assistant_name: str = "Journal Analyst Assistant", instructions: str = None, tools: list = [{"type": "file_search"}]):
        logger.info(f"Assistant created with name: {assistant_name}")
        self.assistant = {"name": assistant_name, "instructions": instructions if instructions else self.assistant_prompt, "tools": tools}

    @property
    def assistant_prompt(self):
        return f"In order to gather structured information, I would like you, as a multi-hazard bridge engineering expert, particularly in the combination of earthquakes with other hazards, to help me with the analysis and summarization of the uploaded literature. Please summarize the information first in natural language."

    def get_response(self, message: str):
        """Get response from the GPT model."""
        logger.info(f"Requesting response for: {message[:50]}...")
        
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

    def extract_text_from_pdf_with_plumber(self, pdf_path: str) -> str:
        """Extract text from the PDF file using pdfplumber."""
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    def split_text_into_chunks(self, text: str, max_tokens: int = 10000):
        """
        将文本拆分成多个较小的部分，每部分的长度不超过指定的最大tokens数量。
        
        Args:
            text (str): 要拆分的文本。
            max_tokens (int): 每个部分的最大tokens数量。
        
        Returns:
            list[str]: 拆分后的文本部分列表。
        """
        words = text.split()
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)
            if len(" ".join(current_chunk)) > max_tokens:
                chunks.append(" ".join(current_chunk))
                current_chunk = []

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def convert_summary_to_json(self, summary_text: str):
        """
        Convert the summary text into a structured JSON file based on the provided jsonexample template.
        This function will break down the summary into different sections of the JSON template.
        
        Args:
            summary_text (str): The text summary to be converted.
        
        Returns:
            str: The filename of the saved JSON file.
        """
        # 使用jsonexample作为模板，并根据summary_text内容填充数据
        json_output = self.jsontemplate.copy()

        # 将文本分块处理
        chunks = self.split_text_into_chunks(summary_text, max_tokens=10000)
        
        # 初始化临时数据结构
        temp_data = {
            "titles": [],
            "keywords": [],
            "authors": [],
            "dois": [],
            "hazard_types": {hazard: 0 for hazard in json_output["Research Subject"]["Hazard Type"]},
            "bridge_types": {bridge_type: 0 for bridge_type in json_output["Research Subject"]["Bridge Type"]},
            "time_scales": {time_scale: 0 for time_scale in json_output["Spatiotemporal Characteristics"]["Time Scale"]},
            "spatial_scales": {spatial_scale: 0 for spatial_scale in json_output["Spatiotemporal Characteristics"]["Spatial scale"]},
            "site_conditions": {site_condition: 0 for site_condition in json_output["Spatiotemporal Characteristics"]["Site Condition"]}
        }

        # 遍历每个文本块并提取信息
        for chunk in chunks:
            # 提取基本信息并存储
            temp_data["titles"].append(self.get_response("Extract the title from the following text: " + chunk))
            temp_data["keywords"].extend(self.get_response("Extract the keywords from the following text: " + chunk).split(","))
            temp_data["authors"].extend(self.get_response("Extract the authors from the following text: " + chunk).split(","))
            temp_data["dois"].append(self.get_response("Extract the DOI from the following text: " + chunk))
            
            # 提取研究主题信息并累加
            research_subject_prompt = "Based on the following text, fill in the research subject section: " + chunk
            for hazard in temp_data["hazard_types"]:
                if "Yes" in self.get_response(research_subject_prompt + f" Does it mention {hazard}?"):
                    temp_data["hazard_types"][hazard] += 1
            for bridge_type in temp_data["bridge_types"]:
                if "Yes" in self.get_response(research_subject_prompt + f" Does it mention {bridge_type}?"):
                    temp_data["bridge_types"][bridge_type] += 1
            
            # 提取时空特征信息并累加
            spatiotemporal_prompt = "Based on the following text, fill in the spatiotemporal characteristics section: " + chunk
            for time_scale in temp_data["time_scales"]:
                if "Yes" in self.get_response(spatiotemporal_prompt + f" Does it mention {time_scale}?"):
                    temp_data["time_scales"][time_scale] += 1
            for spatial_scale in temp_data["spatial_scales"]:
                if "Yes" in self.get_response(spatiotemporal_prompt + f" Does it mention {spatial_scale}?"):
                    temp_data["spatial_scales"][spatial_scale] += 1
            for site_condition in temp_data["site_conditions"]:
                if "Yes" in self.get_response(spatiotemporal_prompt + f" Does it mention {site_condition}?"):
                    temp_data["site_conditions"][site_condition] += 1

        # Step 1: 整合并提炼基本信息
        json_output["Basic Information"]["Title"] = self.get_response("Consolidate and summarize the following titles: " + "; ".join(temp_data["titles"]))
        json_output["Basic Information"]["Keywords"] = list(set(temp_data["keywords"]))  # 去重
        json_output["Basic Information"]["Authors"] = list(set(temp_data["authors"]))  # 去重
        json_output["Basic Information"]["DOI"] = "; ".join(set(temp_data["dois"]))  # 去重并合并

        # Step 2: 整合并提炼研究主题
        for hazard, count in temp_data["hazard_types"].items():
            json_output["Research Subject"]["Hazard Type"][hazard] = count > 0
        for bridge_type, count in temp_data["bridge_types"].items():
            json_output["Research Subject"]["Bridge Type"][bridge_type] = count > 0

        # Step 3: 整合并提炼时空特征
        for time_scale, count in temp_data["time_scales"].items():
            json_output["Spatiotemporal Characteristics"]["Time Scale"][time_scale] = count > 0
        for spatial_scale, count in temp_data["spatial_scales"].items():
            json_output["Spatiotemporal Characteristics"]["Spatial scale"][spatial_scale] = count > 0
        for site_condition, count in temp_data["site_conditions"].items():
            json_output["Spatiotemporal Characteristics"]["Site Condition"][site_condition] = count > 0

        # 继续填充其他部分，按照类似的逻辑

        # 保存 JSON 文件
        json_filename = "Article_Summary_n.json"
        with open(json_filename, 'w') as json_file:
            json.dump(json_output, json_file, indent=4)
        logger.info(f"Summary has been converted to JSON and saved as {json_filename}")
        return json_filename

# 程序入口
if __name__ == "__main__":
    apikey = os.getenv("OPENAI_API_KEY")
    pinecone_key = os.getenv("PINECONE_API_KEY")
    
    chatbot = GptChatBot(apikey=apikey, baseurl="https://api.deepbricks.ai/v1/", pinecone_key="8b5c4740-7ac6-40f3-9a6c-17e1beca3083")
    
    chatbot.create_assistant("Summary Assistant", "Please help me to summarize the article.", tools=[{"type": "file_search"}])
    
    pdfpath = r"C:\Users\22525\Zotero\storage\HXQKFPME\Ali 等 - 2024 - A Simplified Approach for Dynamic Analysis of Susp.pdf"
    
    summary = chatbot.extract_text_from_pdf_with_plumber(pdfpath)
    
    json_filename = chatbot.convert_summary_to_json(summary)
    print(f"Summary saved to {json_filename}")
    
    chatbot.update_assistant()
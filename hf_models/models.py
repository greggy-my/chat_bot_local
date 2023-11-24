from transformers import pipeline
import subprocess
import httpx
import json
import asyncio
import re
import time
from collections import defaultdict
import requests


def timing_decorator(func):
    def wrapper():
        start_time = time.time()
        result = func()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"\n\n{func.__name__} took {elapsed_time:.6f} seconds to execute.")
        return result

    return wrapper


def async_timing_decorator(func):
    async def wrapper():
        start_time = time.time()
        result = await func()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"\n\n{func.__name__} took {elapsed_time:.6f} seconds to execute.")
        return result

    return wrapper


def embed_text(text: list[str]) -> list[list]:
    """Vectorise text using embedding function"""
    embedding_function = pipeline(task="feature-extraction",
                                  model="ai-forever/sbert_large_nlu_ru",
                                  from_pt=True)
    embeddings = embedding_function(text)
    embeddings_parsed = [item[0][0] for item in embeddings]
    return embeddings_parsed


def validate_response(response: requests.Response or httpx.Response) -> bool:
    """Validate HTTP response"""
    if isinstance(response, httpx.Response) or isinstance(response, requests.Response):
        if response.status_code == 200:
            print("HTTP response is valid.")
            return True
        else:
            print(f"Invalid HTTP response. Status Code: {response.status_code}\n {response.text}\n")
            return False
    else:
        print("Invalid response. Expected an instance of requests.Response.")
        return False


def parse_model_response(response: str) -> str:
    """Parse model response, replace unrelated symbols"""
    result = response.strip()
    quotes_pattern = r'^[\'\"]+|[\'\"]+$'
    prefix_pattern = r'^(AI[^:]*:|Human[^:]*:)'
    result = re.sub(quotes_pattern, '', result)
    result = re.sub(prefix_pattern, '', result)
    result = result.strip()
    return result


class Models:
    def __init__(self):
        self.__initiate_connection()
        self.local_host = "http://localhost:11434/api/"
        self.models_urls = {"get": {"list": "tags"},
                            "post": {"generate": "generate"}}

    @staticmethod
    def __initiate_connection() -> None:
        """Initiate connection with Ollama"""
        bash_command = "ollama serve"
        try:
            subprocess.run(bash_command, shell=True, check=True)
            print("Ollama is serving.\n")
        except subprocess.CalledProcessError as e:
            print(f"Error during ollama initialisation: {e}\n")

    async def get_list_models(self) -> None:
        """Get list of available models"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url=self.local_host + self.models_urls["get"]["list"])
            if validate_response(response=response):
                all_models = [model["name"] for model in json.loads(response.text)["models"]]
                print(all_models, end="\n")

    @staticmethod
    def prompt_template(template_key: str, question: str = "", chat_memory: str = "", db_information: str = "") -> str:
        """Get prompt template depending on the type of the question"""

        def def_value():
            return f"No template with key: {template_key}"

        template = defaultdict(def_value)
        template["chat"] = f"""
        user prompt:"{question}" 
        HABR database information: "{db_information}"
        instructions: Craft your response in Russian. Craft your response without HABR database information if it is irrelevant.
        """
        template["memory_chat"] = f"""
        instructions: 
        Craft your responses only in Russian. 
        Do not duplicate messages from the ongoing conversation. 
        Do not use AI and Human to start the generation. Give your response in plain text format. Reply only from the AI side.
        
        current conversation: {chat_memory}
        """

        template["classification"] = f"""{question}"""
        return template[template_key]

    async def a_generate_response(self, model: str, prompt: str) -> tuple:
        """Generate asynchronous response to a model and get a reply and speed of text generation"""
        async with httpx.AsyncClient() as client:
            json_data = json.dumps({"model": model, "prompt": prompt, "stream": False})
            response = await client.post(url=self.local_host + self.models_urls["post"]["generate"],
                                         data=json_data, timeout=120)
            print(f"Generated HTTP response")
            if validate_response(response=response):
                model_answer = parse_model_response(json.loads(response.text)["response"])
                try:
                    model_generation_speed = round(float(json.loads(response.text)["eval_count"] \
                                                         / (json.loads(response.text)["eval_duration"] / 1e+9)), 2)
                except KeyError:
                    print("Model didn't send the speed back")
                    model_generation_speed = None
                return model_answer, model_generation_speed

    def generate_response(self, model: str, prompt: str) -> tuple:
        """Generate synchronous response to a model and get a reply and speed of text generation"""
        json_data = json.dumps({"model": model, "prompt": prompt, "stream": False})
        response = requests.post(url=self.local_host + self.models_urls["post"]["generate"],
                                 data=json_data, timeout=120)
        print(f"Sent HTTP response to generate text to {model}")
        if validate_response(response=response):
            model_answer = parse_model_response(json.loads(response.text)["response"])
            model_generation_speed = round(float(json.loads(response.text)["eval_count"] \
                                                 / (json.loads(response.text)["eval_duration"] / 1e+9)), 2)
            return model_answer, model_generation_speed


if __name__ == "__main__":
    pass

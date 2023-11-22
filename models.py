from transformers import pipeline
from langchain.llms import Ollama
from langchain.callbacks.manager import CallbackManager, AsyncCallbackManagerForLLMRun
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import requests
import subprocess
import json
import httpx
import json
import asyncio
import re
import time
import accelerate
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
    embedding_function = pipeline(task="feature-extraction",
                                  model="ai-forever/sbert_large_nlu_ru",
                                  from_pt=True)
    embeddings = embedding_function(text)
    embeddings_parsed = [item[0][0] for item in embeddings]
    return embeddings_parsed


def validate_response(response: requests.Response or httpx.Response) -> bool:
    if isinstance(response, httpx.Response) or isinstance(response, requests.Response):
        if response.status_code == 200:
            print("HTTP response is valid.\n")
            return True
        else:
            print(f"Invalid HTTP response. Status Code: {response.status_code}\n {response.text}\n")
            return False
    else:
        print("Invalid response. Expected an instance of requests.Response.")
        return False

class Models:
    def __init__(self):
        self.__initiate_connection()
        self.local_host = "http://localhost:11434/api/"
        self.models_urls = {"get": {"list": "tags"},
                            "post": {"generate": "generate"}}

    @staticmethod
    def __initiate_connection() -> None:
        bash_command = "ollama serve"
        try:
            subprocess.run(bash_command, shell=True, check=True)
            print("Ollama is serving.\n")
        except subprocess.CalledProcessError as e:
            print(f"Error during ollama initialisation: {e}\n")

    async def get_list_models(self) -> None:
        async with httpx.AsyncClient() as client:
            response = await client.get(url=self.local_host + self.models_urls["get"]["list"])
            if validate_response(response=response):
                all_models = [model["name"] for model in json.loads(response.text)["models"]]
                print(all_models, end="\n")

    @staticmethod
    def prompt_template(question: str, db_information: str, template_key: str) -> str:
        def def_value():
            return f"No template with key: {template_key}"

        template = defaultdict(def_value)
        template["chat"] = f"""
                user prompt:"{question}" 
                habr database information: "{db_information}"
                Form your answer only in Russian
                """
        template["classification"] = f"""{question}"""
        return template[template_key]

    async def a_generate_response(self, model: str, prompt: str) -> tuple:
        async with httpx.AsyncClient() as client:
            json_data = json.dumps({"model": model, "prompt": prompt, "stream": False})
            response = await client.post(url=self.local_host + self.models_urls["post"]["generate"],
                                         data=json_data, timeout=120)
            print(f"Generated HTTP response")
            if validate_response(response=response):
                model_answer = json.loads(response.text)["response"].strip()
                model_generation_speed = round(float(json.loads(response.text)["eval_count"] \
                                                     / (json.loads(response.text)["eval_duration"] / 1e+9)), 2)
                return model_answer, model_generation_speed

    def generate_response(self, model: str, prompt: str) -> tuple:
            json_data = json.dumps({"model": model, "prompt": prompt, "stream": False})
            response = requests.post(url=self.local_host + self.models_urls["post"]["generate"],
                                         data=json_data, timeout=120)
            print(f"Generated HTTP response")
            if validate_response(response=response):
                model_answer = json.loads(response.text)["response"].strip()
                model_generation_speed = round(float(json.loads(response.text)["eval_count"] \
                                                     / (json.loads(response.text)["eval_duration"] / 1e+9)), 2)
                return model_answer, model_generation_speed


if __name__ == "__main__":
    @async_timing_decorator
    async def a_main():
        models = Models()

        await models.get_list_models()

        question = 'Напиши код используя визуальный пакет tkinter в Питоне'
        db_information = 'Солнце светит ярко'
        prompt = f"""
        user prompt:"{question}" 
        habr database information: "{db_information}"
        Form your answer only in Russian
        """
        prompt_2 = f"""
                user prompt:"{question}" 
                habr database information: "{db_information}"
                Form your answer only in Russian
                """

        model_answer, model_speed = await models.generate_response(model="llama_code",
                                                                   prompt=prompt)
        print(model_answer)
        print(model_speed)


    asyncio.run(a_main())

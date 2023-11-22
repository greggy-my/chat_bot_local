import langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import BeautifulSoupTransformer
import requests
from bs4 import BeautifulSoup
import re
import copy
from vector_db import VectorDB
import csv
import json
from hf_models.models import embed_text
import os
from tqdm import tqdm


def get_html(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to retrieve HTML. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error during request: {e}")
    return None


def scrape_with_playwright(urls):
    loader = AsyncChromiumLoader(urls)
    docs = loader.load()
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(
        docs, tags_to_extract=["p"]
    )

    # Grab the first 1000 tokens of the site
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=200, chunk_overlap=0
    )
    splits = splitter.split_documents(docs_transformed)
    return splits


def preprocess_text_to_vector(documents: list[langchain.schema.document.Document]) -> dict:
    documents = copy.deepcopy(documents)
    text_dict = dict()
    text_dict['texts'] = [doc.page_content for doc in documents]
    text_dict['meta_data'] = [doc.metadata for doc in documents]
    text_dict['ids'] = [f'id{number}' for number in range(1, len(documents) + 1)]

    return text_dict


def save_dict_to_csv(filename, my_dict):
    # Get the header (keys of the dictionary)
    header = my_dict.keys()

    # Open the CSV file for writing
    with open(filename, 'w', newline='') as csv_file:
        # Create a CSV writer object
        csv_writer = csv.DictWriter(csv_file, fieldnames=header)

        # Write the header to the CSV file
        csv_writer.writeheader()

        # Write the data from the dictionary to the CSV file
        csv_writer.writerow(my_dict)


if __name__ == "__main__":
    if not os.path.exists('emergency_data_storage.json'):
        # Getting URLs from Habr
        habr_article_urls = []
        habr_search_urls = [f"https://habr.com/ru/hubs/programming/articles/top/alltime/easy/page{page_n}/" for
                            page_n in range(1, 21)]
        # Extract URLs of habr articles
        for habr_search_url in tqdm(habr_search_urls):
            html_doc = get_html(habr_search_url)

            if html_doc is not None:
                soup = BeautifulSoup(html_doc, "html.parser")

                article_url_pattern = r'^/ru/articles/\d+/$'

                for a_tags in soup.find_all("a"):
                    link = str(a_tags.get("href"))
                    match_article_link = re.match(article_url_pattern, link)
                    if match_article_link:
                        link = "https://habr.com" + link
                        habr_article_urls.append(link)

        # Extract content from the articles
        print(habr_article_urls)
        extracted_content = scrape_with_playwright(habr_article_urls)
        extracted_content_processed = preprocess_text_to_vector(extracted_content)

        # Save the data to emergency csv file
        filename = 'emergency_data_storage.json'
        with open(filename, 'w') as json_file:
            json.dump(extracted_content_processed, json_file)
    else:
        with open('emergency_data_storage.json', 'r') as json_file:
            extracted_content_processed = json.load(json_file)

    # Create embeddings
    embeddings = embed_text(extracted_content_processed["texts"])

    # Save the data to vector db
    db = VectorDB()
    if db.check_connection() is not None:
        db.create_collection(collection_name='habr')
        db.add_documents_to_current_collection(text_documents=extracted_content_processed['texts'],
                                               documents_metadata=extracted_content_processed['meta_data'],
                                               documents_ids=extracted_content_processed['ids'],
                                               embeddings=embeddings)



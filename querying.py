from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from llama_index import GPTVectorStoreIndex, download_loader, StorageContext, load_index_from_storage
import json
import os

app = FastAPI()

class URLList(BaseModel):
    urls: List[str] = None

@app.post("/run_extraction")
async def run_extraction():
    BeautifulSoupWebReader = download_loader("BeautifulSoupWebReader")
    loader = BeautifulSoupWebReader()

    # Read the URLs from the JSON file
    with open('output.json', 'r') as f:
        data = json.load(f)
        urls = [item['URL'] for item in data]

    documents = loader.load_data(urls=urls)
    index = GPTVectorStoreIndex.from_documents(documents)
    index.storage_context.persist()

    return {"status": "completed"}

@app.get("/query")
async def query_data(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="Query string is required")
    
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    index = load_index_from_storage(storage_context)
    response = index.as_query_engine().query(query)
    print(response)
    return response

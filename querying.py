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
async def run_extraction(urls: URLList = None):
    # Check if URLs are passed in the request
    if urls and urls.urls:
        # If URLs are passed, save them to a JSON file
        with open('urls.json', 'w') as f:
            json.dump(urls.dict(), f)
    else:
        # If URLs are not passed, read the URLs from the JSON file
        if os.path.isfile('urls.json') and os.path.getsize('urls.json') > 0:
            with open('urls.json', 'r') as f:
                data = json.load(f)
                urls = data.get('urls', [])
        else:
            raise HTTPException(status_code=400, detail="URLs are required")

    BeautifulSoupWebReader = download_loader("BeautifulSoupWebReader")
    loader = BeautifulSoupWebReader()

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

from fastapi import FastAPI, HTTPException, responses
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import uuid
import json
import os
import pydantic
import enum
from typing import Dict
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str

class Status(str, enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"

class Health(BaseModel):
    status: Status
    version: str
    releaseId: str

class HealthResponse(responses.JSONResponse):
    media_type = "application/health+json"

@app.get("/health", response_class=HealthResponse)
async def get_health() -> Dict[str, str]:
    return {
        "status": Status.PASS.value,  # Correct enum reference
        "version": "0.0.1",
        "releaseId": "1",
    }



@app.get("/test-link")
async def test_link(link: str):
    try:
        response = requests.get(link, headers=headers)
        if response.status_code == 200:
            return "Successfully fetched the webpage!"
        else:
            return {
                "Message: ": "Failed to fetch webpage",
                "Status Code: ": response.status_code
            }  
    except requests.exceptions.HTTPError as err:
        return f"HTTP error occurred: {err}"



@app.post("/scrape-page")
async def scrape_website(request: ScrapeRequest):
    unique_id = str(uuid.uuid4())  # Generate a unique file name for each request
    output_file = f"output_{unique_id}.json"
    
    command = [
        "scrapy", "runspider", "tradingagent/tradingagent/spiders/dynamic_spider.py",  # Make sure the path to the spider is correct
        "-a", f"start_url={request.url}",
        "-o", output_file
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        
        if not os.path.exists(output_file):
            raise HTTPException(status_code=500, detail="Scraping failed or no data collected.")
        
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        os.remove(output_file)  # Cleanup the file after reading
        return {"status": "success", "data": data}
    
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Scrapy error: {e.stderr}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# @app.post("/scrape-links")
# async def scrape_links(request: ScrapeRequest):
#     unique_id = str(uuid.uuid4())
#     output_file = f"output_{unique_id}.json"
    
#     command = [
#         "scrapy", "runspider", "tradingagent/tradingagent/spiders/dynamic_link_spider.py",
#         "-a", f"start_url={request.url}",
#         "-o", output_file
#     ]
    
#     try:
#         result = subprocess.run(
#             command,
#             check=True,
#             capture_output=True,
#             text=True,
#             timeout=300  # 5 minutes timeout
#         )
        
#         if not os.path.exists(output_file):
#             raise HTTPException(status_code=500, detail="Scraping failed or no data collected")

#         with open(output_file, "r", encoding="utf-8") as f:
#             data = json.load(f)

#         os.remove(output_file)
        
#         # Process data to include both links and texts
#         processed_data = []
#         for item in data:
#             processed_data.append({
#                 'url': item['url'],
#                 'anchor_text': item['anchor_text'],
#                 'content_snippet': item['content'][:500] + '...' if item['content'] else ''
#             })

#         return {"status": "success", "data": processed_data}

#     except subprocess.TimeoutExpired:
#         raise HTTPException(status_code=504, detail="Scraping operation timed out")
#     except subprocess.CalledProcessError as e:
#         raise HTTPException(status_code=500, detail=f"Scrapy error: {e.stderr}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     name = "dynamic_link_spider"

#     def __init__(self, start_url=None, *args, **kwargs):
#         super(DynamicSpider, self).__init__(*args, **kwargs)
#         if start_url:
#             self.start_urls = [start_url]
#             parsed_url = urlparse(start_url)
#             self.allowed_domains = [parsed_url.netloc]  # Set allowed domain dynamically

#     custom_settings = {
#         'ROBOTSTXT_OBEY': True,
#         'DOWNLOAD_DELAY': 2,
#         'CONCURRENT_REQUESTS': 1,
#         'LOG_LEVEL': 'ERROR',  
#     }

#     def parse(self, response):
#         # Extract all links from the page
#         all_links = response.css('a::attr(href)').getall()
#         for each_link in all_links:
#             if each_link and not each_link.startswith(('javascript:', 'mailto:', 'tel:')):
#                 yield response.follow(each_link, self.parse_page)

#     def parse_page(self, response):
#         # Extract text content from the page
#         text = ' '.join(response.css('body :not(script):not(style)::text').getall()).strip()
#         text = ' '.join(text.split())  # Clean the text (remove extra spaces)

    
#         yield {
#             'url': response.url
#         }


# Add keyword to the request model
class ScrapeRequest(BaseModel):
    url: str
    keyword: str  # Add keyword field

# Modified FastAPI endpoint
@app.post("/scrape-links")
async def scrape_links(request: ScrapeRequest):
    unique_id = str(uuid.uuid4())
    output_file = f"output_{unique_id}.json"
    
    command = [
        "scrapy", "runspider", "tradingagent/tradingagent/spiders/dynamic_link_spider.py",
        "-a", f"start_url={request.url}",
        "-a", f"keyword={request.keyword}",  # Pass keyword to spider
        "-o", output_file
    ]
    
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if not os.path.exists(output_file):
            raise HTTPException(status_code=500, detail="Scraping failed or no data collected")

        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        os.remove(output_file)
        
        return {"status": "success", "data": data}

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Scraping operation timed out")
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Scrapy error: {e.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# @app.post("/scrape-links")
# async def scrape_links(request: ScrapeRequest):
#     unique_id = str(uuid.uuid4()) 
#     output_file = f"output_{unique_id}.json"
    
#     command = [
#         "scrapy", "runspider", "tradingagent/tradingagent/spiders/dynamic_link_spider.py",  # Make sure the path to the spider is correct
#         "-a", f"start_url={request.url}",
#         "-o", output_file
#     ]
    
#     try:
#         subprocess.run(command, check=True, capture_output=True, text=True)
        
#         if not os.path.exists(output_file):
#             raise HTTPException(status_code=500, detail="Scraping failed or no data collected.")
        
#         with open(output_file, "r", encoding="utf-8") as f:
#             data = json.load(f)
        
#         os.remove(output_file)  # Cleanup the file after reading
#         return {"status": "success", "data": data}
    
#     except subprocess.CalledProcessError as e:
#         raise HTTPException(status_code=500, detail=f"Scrapy error: {e.stderr}")
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    import main
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
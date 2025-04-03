import scrapy
from urllib.parse import urljoin, urlparse
from fastapi import HTTPException
import json
import os
import uuid
import subprocess


# Modified Scrapy spider
class DynamicSpider(scrapy.Spider):
    name = "dynamic_link_spider"

    def __init__(self, start_url=None, keyword=None, *args, **kwargs):
        super(DynamicSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword.lower() if keyword else None
        if start_url:
            self.start_urls = [start_url]
            parsed_url = urlparse(start_url)
            self.allowed_domains = [parsed_url.netloc]

    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 1,
        'LOG_LEVEL': 'ERROR',
    }

    def parse(self, response):
        # Extract all links with their anchor texts
        links = response.css('a')
        for link in links:
            href = link.css('::attr(href)').get()
            text = ' '.join(link.css('::text').getall()).strip()
            
            if href and not href.startswith(('javascript:', 'mailto:', 'tel:')):
                absolute_url = urljoin(response.url, href)
                
                # Check if keyword exists in URL path or fragment
                if self.keyword:
                    parsed = urlparse(absolute_url)
                    url_parts = f"{parsed.path}{parsed.fragment}".lower()
                    if self.keyword not in url_parts:
                        continue  # Skip links without keyword
                
                yield response.follow(
                    absolute_url,
                    callback=self.parse_page,
                    meta={'anchor_text': text}
                )

    def parse_page(self, response):
        # Extract text content (no further link following)
        text = ' '.join(response.css('body :not(script):not(style)::text').getall()).strip()
        cleaned_text = ' '.join(text.split())
        
        yield {
            'url': response.url,
            'anchor_text': response.meta.get('anchor_text', ''),
            'content': cleaned_text if cleaned_text else ''
        }
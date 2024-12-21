import requests
from typing import List, Dict, Optional
import os
from pathlib import Path
import logging
from urllib.parse import quote_plus

class MediaFetcher:
    """Handles fetching media from free sources like Pexels, Unsplash, and Pixabay"""
    
    def __init__(self, cache_dir: str = "static/video_assets/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize with free API keys if available
        self.pexels_api_key = os.getenv('PEXELS_API_KEY')
        self.pixabay_api_key = os.getenv('PIXABAY_API_KEY')
        
    def search_images(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for images across free sources"""
        results = []
        
        # Search Pexels
        if self.pexels_api_key:
            pexels_results = self._search_pexels(query, 'photo', max_results)
            results.extend(pexels_results)
            
        # Add more free sources here
        
        return results[:max_results]
    
    def search_videos(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for videos across free sources"""
        results = []
        
        # Search Pexels Videos
        if self.pexels_api_key:
            pexels_results = self._search_pexels(query, 'video', max_results)
            results.extend(pexels_results)
            
        return results[:max_results]
    
    def _search_pexels(self, query: str, media_type: str, max_results: int) -> List[Dict]:
        """Search Pexels API for photos or videos"""
        base_url = "https://api.pexels.com/v1/search" if media_type == 'photo' else "https://api.pexels.com/videos/search"
        
        headers = {
            'Authorization': self.pexels_api_key
        }
        
        params = {
            'query': query,
            'per_page': max_results
        }
        
        try:
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get(media_type + 's', []):
                result = {
                    'id': item['id'],
                    'url': item['url'],
                    'source': 'pexels',
                    'type': media_type,
                    'download_url': item['src']['original'] if media_type == 'photo' else item['video_files'][0]['link'],
                    'thumbnail': item['src']['tiny'] if media_type == 'photo' else item['image']
                }
                results.append(result)
                
            return results
            
        except Exception as e:
            logging.error(f"Error fetching from Pexels: {str(e)}")
            return []
    
    def download_media(self, url: str, filename: str) -> Optional[Path]:
        """Download and cache media file"""
        cache_path = self.cache_dir / filename
        
        if cache_path.exists():
            return cache_path
            
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(cache_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            return cache_path
            
        except Exception as e:
            logging.error(f"Error downloading media: {str(e)}")
            return None
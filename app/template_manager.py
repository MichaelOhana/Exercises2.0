import os
import requests
from flask import current_app, session
from app.config.canva_config import CANVA_DESIGN_API

class CanvaTemplateManager:
    def __init__(self, template_id):
        self.template_id = template_id
        self.access_token = session.get('canva_access_token')
        if not self.access_token:
            raise ValueError("No Canva access token found. Please authenticate first.")
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
    def get_template_details(self):
        """Get details about the template"""
        url = f"{CANVA_DESIGN_API}/{self.template_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def create_copy(self):
        """Create a copy of the template"""
        url = f"{CANVA_DESIGN_API}/{self.template_id}/copies"
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def update_placeholders(self, design_id, updates):
        """Update placeholders in a design"""
        url = f"{CANVA_DESIGN_API}/{design_id}/placeholders"
        
        # Format updates for Canva API
        placeholders = {
            "placeholders": [
                {
                    "key": key,
                    "text": value
                } for key, value in updates.items()
            ]
        }
        
        response = requests.patch(url, headers=self.headers, json=placeholders)
        response.raise_for_status()
        return response.json() 
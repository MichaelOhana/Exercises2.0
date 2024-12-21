import os
import requests
from flask import current_app

class CanvaIntegration:
    def __init__(self):
        self.api_key = os.getenv('CANVA_API_KEY')
        self.base_url = "https://api.canva.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def export_design(self, design_id, file_type="video"):
        """
        Export a design as video/image using Canva's REST API
        
        Args:
            design_id (str): The Canva design ID
            file_type (str): The export format (video, jpg, png, pdf)
            
        Returns:
            dict: Export result containing status and URLs
        """
        try:
            # Request design export
            url = f"{self.base_url}/designs/{design_id}/exports"
            payload = {
                "format": file_type,
                "options": {}
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()  # Raise exception for bad status codes
            
            export_data = response.json()
            
            # Check export status
            if export_data.get("status") == "completed":
                return {
                    "status": "success",
                    "urls": [export_data.get("url")]
                }
            else:
                return {
                    "status": "pending",
                    "message": f"Export status: {export_data.get('status')}",
                    "export_id": export_data.get("id")
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": str(e)
            }
            
    def check_export_status(self, design_id, export_id):
        """
        Check the status of a pending export
        """
        try:
            url = f"{self.base_url}/designs/{design_id}/exports/{export_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            export_data = response.json()
            
            if export_data.get("status") == "completed":
                return {
                    "status": "success",
                    "urls": [export_data.get("url")]
                }
            else:
                return {
                    "status": export_data.get("status"),
                    "message": f"Export still processing: {export_data.get('status')}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": str(e)
            }

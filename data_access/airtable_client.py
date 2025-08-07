import requests
import json
import logging
from typing import List, Dict, Optional
from config.airtable_config import HEADERS, BASE_ID

logger = logging.getLogger(__name__)


class AirtableClient:
    """Generic Airtable API client for CRUD operations"""
    
    def __init__(self):
        self.headers = HEADERS
        self.base_id = BASE_ID
    
    def fetch_records(self, table_name: str, filter_formula: Optional[str] = None) -> List[Dict]:
        """Fetch records from an Airtable table"""
        url = f"https://api.airtable.com/v0/{self.base_id}/{table_name}"
        params = {}
        if filter_formula:
            params["filterByFormula"] = filter_formula
            
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        return response.json().get("records", [])
    
    def create_record(self, table_name: str, fields: Dict) -> Dict:
        """Create a new record in an Airtable table"""
        url = f"https://api.airtable.com/v0/{self.base_id}/{table_name}"
        payload = {"fields": fields}
        
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def update_record(self, table_name: str, record_id: str, fields: Dict) -> Dict:
        """Update an existing record in an Airtable table"""
        url = f"https://api.airtable.com/v0/{self.base_id}/{table_name}/{record_id}"
        payload = {"fields": fields}
        
        response = requests.patch(url, headers=self.headers, json=payload)
        logger.debug(f"Update request URL: {url}")
        logger.debug(f"Update request payload: {payload}")
        logger.debug(f"Update response status: {response.status_code}")
        
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error Details: {e}")
            logger.error(f"Response content: {response.text}")
            raise
        
        logger.debug(f"Update response text: {response.text}")
        return response.json()
        
        return response.json()
    
    def delete_record(self, table_name: str, record_id: str) -> Dict:
        """Delete a record from an Airtable table"""
        url = f"https://api.airtable.com/v0/{self.base_id}/{table_name}/{record_id}"
        logger.info(f"Deleting record from {table_name} with ID: {record_id}")
        logger.debug(f"Delete URL: {url}")
        
        response = requests.delete(url, headers=self.headers)
        logger.debug(f"Delete response status: {response.status_code}")
        
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error Details: {e}")
            logger.error(f"Response content: {response.text}")
            raise
        
        logger.debug(f"Delete response text: {response.text}")
        return response.json()
        
        return response.json()
    
    def upsert_record(self, table_name: str, filter_formula: str, fields: Dict) -> Dict:
        """Upsert a record in an Airtable table"""
        records = self.fetch_records(table_name, filter_formula)
        logger.info(f"Upserting record in {table_name} with formula: {filter_formula}")
        logger.info(f"Found records: {len(records)}")
        
        if records:
            record_id = records[0]["id"]
            logger.info(f"Updating existing record with ID: {record_id}")
            logger.debug(f"Record structure: {records[0]}")
            return self.update_record(table_name, record_id, fields)
        else:
            logger.info("Creating new record")
            return self.create_record(table_name, fields)

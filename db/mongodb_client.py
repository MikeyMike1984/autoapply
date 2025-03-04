# file: db/mongodb_client.py
from pymongo import MongoClient
from typing import Dict, List, Any, Optional
from bson.objectid import ObjectId
from datetime import datetime

class MongoDBClient:
    """Client for interacting with MongoDB"""
    
    def __init__(self, connection_string: str, database_name: str):
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
    
    def insert_job(self, job_data: Dict[str, Any]) -> str:
        """Insert a job and return its ID"""
        result = self.db.jobs.insert_one(job_data)
        return str(result.inserted_id)
    
    def update_job(self, job_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a job document"""
        result = self.db.jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a job by ID"""
        result = self.db.jobs.find_one({"_id": ObjectId(job_id)})
        return result
    
    def get_jobs_for_processing(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get jobs that need resume generation"""
        cursor = self.db.jobs.find({
            "status.code": "analyzed",
            "analysis.match_score": {"$gt": 0.5}  # Only process jobs with decent match
        }).limit(limit)
        return list(cursor)
    
    def insert_resume(self, resume_data: Dict[str, Any]) -> str:
        """Insert a resume document and return its ID"""
        result = self.db.resumes.insert_one(resume_data)
        return str(result.inserted_id)
    
    def update_resume(self, resume_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a resume document"""
        result = self.db.resumes.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def get_resumes_for_job(self, job_id: str) -> List[Dict[str, Any]]:
        """Get all resumes for a specific job"""
        cursor = self.db.resumes.find({"job_id": job_id})
        return list(cursor)
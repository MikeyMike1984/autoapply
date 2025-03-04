# file: main.py
import asyncio
import json
import os
from dotenv import load_dotenv
from llm.provider import LLMProviderFactory
from db.mongodb_client import MongoDBClient
from services.resume_service import ResumeGenerationService

# Load environment variables
load_dotenv()

async def main():
    # Initialize LLM provider
    llm_provider = LLMProviderFactory.get_provider(
        os.getenv("LLM_PROVIDER", "ollama"), 
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.getenv("OLLAMA_MODEL", "llama3.1:8b-instruct")
    )
    
    # Initialize MongoDB client
    mongodb_client = MongoDBClient(
        connection_string=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
        database_name=os.getenv("MONGODB_DATABASE", "job_application_system")
    )
    
    # Initialize resume generation service
    resume_service = ResumeGenerationService(
        llm_provider=llm_provider,
        mongodb_client=mongodb_client,
        output_dir=os.getenv("OUTPUT_DIR", "./generated_resumes")
    )
    
    # Load professional profile
    with open('professional_profile.json', 'r') as f:
        professional_profile = json.load(f)
    
    # Process pending jobs
    results = await resume_service.process_pending_jobs(
        professional_profile=professional_profile,
        limit=10  # Process up to 10 jobs at a time
    )
    
    print(f"Generated {len(results)} resumes")
    for result in results:
        print(f"Job: {result['job_id']}, Match score: {result['match_score']}, Resume: {result['resume_path']}")

if __name__ == "__main__":
    asyncio.run(main())
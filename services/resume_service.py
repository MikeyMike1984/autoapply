# file: services/resume_service.py
import asyncio
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class ResumeGenerationService:
    """Main service for generating tailored resumes"""
    
    def __init__(
        self,
        llm_provider,
        mongodb_client,
        output_dir: str = "./generated_resumes"
    ):
        from services.job_analyzer import JobAnalyzer
        from services.experience_matcher import ExperienceMatcher
        from services.resume_template import ResumeTemplateEngine
        
        self.job_analyzer = JobAnalyzer(llm_provider)
        self.experience_matcher = ExperienceMatcher(llm_provider)
        self.template_engine = ResumeTemplateEngine()
        self.mongodb_client = mongodb_client
        self.output_dir = output_dir
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    async def process_job(
        self,
        job_id: str,
        professional_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a single job and generate a tailored resume"""
        
        # Get job details from database
        job_data = self.mongodb_client.get_job(job_id)
        if not job_data:
            raise ValueError(f"Job not found: {job_id}")
        
        job_description = job_data.get("description", "")
        job_title = job_data.get("title", "")
        company = job_data.get("company", {}).get("name", "")
        
        # If job already has analysis, use it; otherwise analyze the job
        if "analysis" in job_data:
            job_requirements = job_data["analysis"]
        else:
            job_requirements = await self.job_analyzer.analyze_job(job_description)
            
            # Update the job document with analysis
            self.mongodb_client.update_job(job_id, {
                "analysis": job_requirements,
                "status.code": "analyzed",
                "status.updated_at": datetime.utcnow()
            })
        
        # Match with professional experience
        matched_experiences = await self.experience_matcher.match_experiences(
            job_requirements, professional_profile
        )
        
        # Generate resume filename
        sanitized_company = company.replace(' ', '_').replace('/', '_')
        output_filename = f"{self.output_dir}/{job_id}_{sanitized_company}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Create resume
        self.template_engine.create_resume(
            {
                "personal_info": {
                    "name": f"{professional_profile['user']['name']['first']} {professional_profile['user']['name']['last']}",
                    "email": professional_profile['user']['contact']['email'],
                    "phone": professional_profile['user']['contact']['phone'],
                    "linkedin": professional_profile['user']['contact']['linkedin'],
                    "location": f"{professional_profile['user']['contact']['location']['city']}, {professional_profile['user']['contact']['location']['state']}"
                },
                "professional_summary": matched_experiences['professional_summary'],
                "skills": matched_experiences['skills_to_emphasize'],
                "experiences": matched_experiences['highlighted_experiences'],
                "education": professional_profile.get('education', []),
                "certifications": professional_profile.get('certifications', [])
            },
            output_path=output_filename
        )
        
        # Store resume info in database
        resume_id = self.mongodb_client.insert_resume({
            "job_id": job_id,
            "file": {
                "filename": os.path.basename(output_filename),
                "path": output_filename,
                "created_at": datetime.utcnow()
            },
            "customization": {
                "highlighted_skills": matched_experiences["skills_to_emphasize"],
                "highlighted_experiences": matched_experiences["highlighted_experiences"],
                "customized_summary": matched_experiences["professional_summary"],
                "tailoring_score": matched_experiences.get("match_score", 0.0)
            },
            "metadata": {
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "version": 1
            }
        })
        
        # Update job status
        self.mongodb_client.update_job(job_id, {
            "status.code": "resume_generated",
            "status.updated_at": datetime.utcnow(),
            "application.resume_id": resume_id,
            "application.match_score": matched_experiences.get("match_score", 0.0),
            "application.relevance_reasoning": matched_experiences.get("relevance_reasoning", "")
        })
        
        return {
            "job_id": job_id,
            "resume_id": resume_id,
            "resume_path": output_filename,
            "match_score": matched_experiences.get("match_score", 0.0),
            "match_explanation": matched_experiences.get("relevance_reasoning", "")
        }
    
    async def process_pending_jobs(
        self,
        professional_profile: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Process jobs that need resume generation"""
        
        # Get jobs that need processing
        jobs = self.mongodb_client.get_jobs_for_processing(limit)
        
        results = []
        for job in jobs:
            try:
                result = await self.process_job(
                    str(job["_id"]), professional_profile
                )
                results.append(result)
            except Exception as e:
                print(f"Error processing job {job['_id']}: {e}")
        
        return results
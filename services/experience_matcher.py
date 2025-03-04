# file: services/experience_matcher.py
from typing import Dict, List, Any

class ExperienceMatcher:
    """Matches job requirements with professional experience"""
    
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
    
    async def match_experiences(
        self, 
        job_requirements: Dict[str, Any],
        professional_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Match job requirements with professional experiences"""
        
        match_schema = {
            "title": "ExperienceMatch",
            "type": "object",
            "properties": {
                "highlighted_experiences": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "company": {"type": "string"},
                            "position": {"type": "string"},
                            "bullet_points": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    }
                },
                "skills_to_emphasize": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "professional_summary": {"type": "string"},
                "match_score": {"type": "number"},
                "relevance_reasoning": {"type": "string"}
            }
        }
        
        # System message with clear instructions
        system_message = """
        You are an expert resume writer who specializes in tailoring resumes to match job requirements.
        Your goal is to select experiences and skills that best match the job requirements.
        
        Follow these rules:
        1. Be truthful - only use experiences and skills that are in the candidate's profile
        2. Be specific - highlight concrete achievements with metrics when available
        3. Be relevant - focus on experiences most relevant to the job requirements
        4. Be concise - each bullet point should be clear and impactful
        5. Emphasize transferable skills for job requirements that don't have direct matches
        6. Write in a professional tone appropriate for a resume
        7. Quantify achievements whenever possible
        8. Use active language and action verbs
        9. Avoid generic statements without context
        10. Ensure the match score (0.0 to 1.0) accurately reflects how well the candidate's profile matches the requirements
        """
        
        # Extract relevant portions of professional profile for the prompt
        experiences = professional_profile.get("experiences", [])
        skills = professional_profile.get("skills", [])
        
        experiences_str = "\n\n".join([
            f"Company: {exp['company']}\n"
            f"Position: {exp['title']}\n"
            f"Duration: {exp.get('start_date', '')} to {exp.get('end_date', 'Present')}\n"
            f"Description: {exp.get('description', '')}\n"
            f"Achievements:\n" + "\n".join([f"- {a}" for a in exp.get('achievements', [])])
            for exp in experiences
        ])
        
        skills_str = ", ".join([skill["name"] for skill in skills])
        
        # Create a well-structured prompt with clear sections
        prompt = f"""
        ## Task
        Based on the job requirements and professional profile below, identify the most relevant experiences
        and skills to highlight on a tailored resume.
        
        ## Job Requirements
        Required Skills: {', '.join(job_requirements.get('required_skills', []))}
        Preferred Skills: {', '.join(job_requirements.get('preferred_skills', []))}
        Years Experience: {job_requirements.get('years_experience', 'Not specified')}
        Education: {job_requirements.get('education_requirements', 'Not specified')}
        Key Responsibilities: {', '.join(job_requirements.get('key_responsibilities', []))}
        Job Level: {job_requirements.get('job_level', 'Not specified')}
        
        ## Professional Profile
        Skills: {skills_str}
        
        Experiences:
        {experiences_str}
        
        ## Example Output
        For a Operations Management job requiring inventory control experience:
        
        ```json
        {
          "highlighted_experiences": [
            {
              "company": "Marley Spoon",
              "position": "National Warehouse Operations Manager",
              "bullet_points": [
                "Directed inventory teams across three U.S. facilities, overseeing 2 Shift Managers, 5 Team Leads, and 40-80 associates per site",
                "Achieved 17% improvement in inventory accuracy across facilities through implementing ICQA departments",
                "Conducted comprehensive time studies to develop realistic labor metrics, enabling accurate labor planning"
              ]
            },
            {
              "company": "Amazon",
              "position": "Operations Manager",
              "bullet_points": [
                "Led team of 2-3 Area Managers and 100-200 hourly associates, driving safety, quality, and performance metrics",
                "Implemented Lean Manufacturing and Six Sigma methodologies, increasing productivity by 20%",
                "Reduced workplace incidents by 15% through strategic safety initiatives"
              ]
            }
          ],
          "skills_to_emphasize": ["Operations Management", "Inventory Control", "Team Leadership", "Lean Manufacturing", "Process Improvement"],
          "professional_summary": "Results-driven Operations Leader with over 10 years of experience managing high-volume distribution centers and implementing inventory control systems. Proven expertise in leveraging Lean techniques and developing cross-functional teams to optimize warehouse operations and improve inventory accuracy.",
          "match_score": 0.85,
          "relevance_reasoning": "The candidate has extensive experience in operations management with a focus on inventory control and warehouse operations, directly matching the job requirements. Their achievements in improving inventory accuracy and implementing process improvements align perfectly with the role."
        }
        ```
        
        Now create a tailored resume content for the given job requirements and professional profile. Remember to include 3-5 bullet points for each experience that emphasize relevant achievements with metrics when possible.
        """
        
        return await self.llm_provider.generate_structured(
            prompt=prompt,
            output_schema=match_schema,
            system_message=system_message
        )
# file: services/job_analyzer.py
from typing import Dict, List, Any

class JobAnalyzer:
    """Analyzes job descriptions to extract key requirements"""
    
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
    
    async def analyze_job(self, job_description: str) -> Dict[str, Any]:
        """Extract key information from job description"""
        
        requirements_schema = {
            "title": "JobRequirements",
            "type": "object",
            "properties": {
                "required_skills": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "preferred_skills": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "years_experience": {
                    "type": "number"
                },
                "education_requirements": {
                    "type": "string"
                },
                "key_responsibilities": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "job_level": {
                    "type": "string"
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"}  
                }
            }
        }
        
        # System message with clear instructions
        system_message = """
        You are an expert job analyst who specializes in extracting key information from job descriptions.
        Follow these rules:
        1. Extract only what is explicitly stated in the job description
        2. For years of experience, provide a numeric value (use the minimum if a range is given)
        3. Be thorough and accurate in your analysis
        4. Include all relevant technical skills mentioned
        5. Don't add requirements that aren't in the description
        """
        
        # Prompt with clear sections and few-shot examples
        prompt = f"""
        ## Task
        Analyze the following job description and extract key information into structured format.
        
        ## Job Description
        {job_description}
        
        ## Information to Extract
        1. Required skills/technologies/qualifications
        2. Preferred/nice-to-have skills
        3. Years of experience required (numeric value)
        4. Education requirements (degree level)
        5. Key job responsibilities
        6. Job level (Entry, Mid, Senior, Executive)
        7. Important keywords from the description
        
        ## Example 1
        Job: Senior Software Engineer with 5+ years of experience in Python, Django, and AWS. Bachelor's degree in Computer Science required. Experience with React preferred.
        
        Result:
        ```json
        {
          "required_skills": ["Python", "Django", "AWS"],
          "preferred_skills": ["React"],
          "years_experience": 5,
          "education_requirements": "Bachelor's in Computer Science",
          "key_responsibilities": ["Software development", "System design"],
          "job_level": "Senior",
          "keywords": ["Python", "Django", "AWS", "Software Engineer"]
        }
        ```
        
        ## Example 2
        Job: Operations Manager needed to oversee warehouse operations. Must have 3-5 years of experience in logistics. MBA preferred but not required. Experience with inventory management systems is essential.
        
        Result:
        ```json
        {
          "required_skills": ["Logistics experience", "Inventory management systems"],
          "preferred_skills": ["MBA"],
          "years_experience": 3,
          "education_requirements": "Not specified",
          "key_responsibilities": ["Oversee warehouse operations"],
          "job_level": "Mid",
          "keywords": ["Operations Manager", "warehouse", "logistics", "inventory"]
        }
        ```
        
        Now analyze the provided job description and provide structured data in the same JSON format.
        """
        
        return await self.llm_provider.generate_structured(
            prompt=prompt,
            output_schema=requirements_schema,
            system_message=system_message
        )
import asyncio
import json
import os
from llm.provider import LLMProviderFactory
from services.job_analyzer import JobAnalyzer
from services.experience_matcher import ExperienceMatcher
from services.resume_template import ResumeTemplateEngine

# Sample professional profile for testing
PROFESSIONAL_PROFILE = {
    "user": {
        "name": {
            "first": "Mike",
            "last": "Reeves"
        },
        "contact": {
            "email": "mireeves40@gmail.com",
            "phone": "817-908-9168",
            "linkedin": "www.linkedin.com/in/michael-reeves-1a2b3c/",
            "location": {
                "city": "Fort Worth",
                "state": "TX"
            }
        },
        "title": "Senior Operations Manager"
    },
    "skills": [
        {"name": "Operations Management", "years": 10, "level": "Expert"},
        {"name": "Inventory Control", "years": 8, "level": "Expert"},
        {"name": "Team Leadership", "years": 12, "level": "Expert"},
        {"name": "Lean Manufacturing", "years": 7, "level": "Advanced"},
        {"name": "Six Sigma", "years": 5, "level": "Intermediate"},
        {"name": "ERP Systems", "years": 6, "level": "Advanced"},
        {"name": "SQL", "years": 4, "level": "Intermediate"},
        {"name": "Power BI", "years": 3, "level": "Intermediate"},
        {"name": "VBA", "years": 5, "level": "Advanced"},
        {"name": "Python", "years": 2, "level": "Beginner"},
        {"name": "Process Improvement", "years": 8, "level": "Expert"},
        {"name": "Strategic Planning", "years": 6, "level": "Advanced"},
        {"name": "Forecasting", "years": 7, "level": "Advanced"},
        {"name": "Budget Management", "years": 5, "level": "Advanced"},
        {"name": "Multi-site Management", "years": 4, "level": "Advanced"},
        {"name": "Amazon Vendor Central", "years": 3, "level": "Intermediate"},
        {"name": "Supply Chain Management", "years": 7, "level": "Advanced"},
        {"name": "Logistics", "years": 6, "level": "Advanced"},
        {"name": "Warehouse Management", "years": 8, "level": "Expert"},
        {"name": "Vendor Negotiations", "years": 5, "level": "Advanced"}
    ],
    "experiences": [
        {
            "company": "Marley Spoon",
            "title": "National Warehouse Operations Manager",
            "start_date": "December 2020",
            "end_date": "December 2022",
            "description": "Managed national inventory operations across three U.S. facilities.",
            "achievements": [
                "Directed inventory teams across three U.S. facilities (NJ, TX, CA), overseeing 2 Shift Managers, 5 Team Leads, and 40-80 associates at each site",
                "Conducted foundational time studies to develop realistic labor metrics, enabling accurate labor planning and setting clear performance expectations",
                "Partnered with finance and operations leadership to establish, staff, and train ICQA departments, achieving a 17% improvement in inventory accuracy across three facilities within two months",
                "Designed and executed enhanced cycle counting strategies, reconciling virtual and physical inventory across warehouses",
                "Championed the implementation of ERP systems, serving as NAV SME for the U.S., optimizing processes through system enhancements and training",
                "Managed relationships with third-party logistics providers (3PLs) to ensure efficient storage and shipping of products",
                "Reduced shipping and storage fees by 12% through process optimization and vendor negotiation",
                "Coordinated with e-commerce platforms including Amazon to ensure smooth operations and product availability"
            ]
        },
        {
            "company": "Android Industries",
            "title": "Program Launch Manager",
            "start_date": "June 2018",
            "end_date": "September 2020",
            "description": "Led large-scale program launch for automotive assembly operations.",
            "achievements": [
                "Directed a $30M program launch, consolidating two facilities and scaling operations from two to eight assembly lines for new vehicle production",
                "Managed the recruitment and onboarding of over 1,000 employees, including 300 contingent assemblers, 400 fulltime assemblers, 18 salaried managers, and 25 engineering staff",
                "Oversaw equipment installation and commissioning, ensuring alignment with operational and quality standards",
                "Developed SQL and Power BI dashboards, enhancing visibility into production, quality, and tooling performance",
                "Applied Lean and Six Sigma principles to streamline workflows, reducing waste and improving throughput",
                "Delivered weekly updates to senior leadership, translating operational insights into strategic decisions",
                "Created and implemented detailed forecasting models that improved inventory planning accuracy by 22%",
                "Established cross-functional team communication protocols that reduced product launch delays by 35%"
            ]
        },
        {
            "company": "Amazon",
            "title": "Operations Manager",
            "start_date": "November 2015",
            "end_date": "May 2018",
            "description": "Managed fulfillment center operations across multiple departments.",
            "achievements": [
                "Led a team of 2-3 Area Managers and 100-200 hourly associates within the outbound operation",
                "Responsible for driving the overall safety, quality, performance and customer experience of the shift",
                "Carried out supervisory responsibilities in accordance with the organization's policies and procedures",
                "Accountable for meeting and exceeding operational goals",
                "Strategic planning and forecasting; appraised performance; rewarded and disciplined employees; addressed staffing needs",
                "Mentored, trained and developed teammates for career progression and learning",
                "Developed and shared best practices across the shifts and network",
                "Managed inventory placement strategies to optimize fulfillment center capacity and reduce out-of-stocks",
                "Collaborated with Amazon Vendor Central teams to ensure smooth vendor relationships and product availability",
                "Reduced shipping issues by 28% through implementation of a systematic troubleshooting process"
            ]
        }
    ],
    "education": [
        {
            "degree": "Bachelor of Science",
            "field": "Industrial Engineering",
            "institution": "The University of Texas",
            "location": "Arlington, TX",
            "graduation_date": "2015"
        }
    ],
    "certifications": [
        {"name": "Lean Green Belt Certification", "year": 2018},
        {"name": "Lean Six Sigma Yellow Belt Certification", "year": 2016},
        {"name": "Certified AutoCAD Technician", "year": 2014},
        {"name": "Amazon Vendor Central Certification", "year": 2017},
        {"name": "Supply Chain Management Professional (SCMP)", "year": 2019}
    ]
}

async def test_with_job_posting():
    try:
        # Read job posting file
        with open('./The Senior E-Commerce Operations Manager.txt', 'r') as f:
            job_description = f.read()
        
        print("Job posting loaded successfully")
        
        # Initialize LLM provider
        llm_provider = LLMProviderFactory.get_provider(
            "ollama", 
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama3.1:8b-instruct")
        )
        
        # Initialize components
        job_analyzer = JobAnalyzer(llm_provider)
        experience_matcher = ExperienceMatcher(llm_provider)
        resume_engine = ResumeTemplateEngine(font_dir="./fonts", format_file="resume_pdf_format_data.json")
        
        # Step 1: Analyze job description
        print("1. Analyzing job description...")
        job_requirements = await job_analyzer.analyze_job(job_description)
        print("\nJob Requirements:")
        print(json.dumps(job_requirements, indent=2))
        
        # Save job requirements to file for reference
        with open('job_requirements_output.json', 'w') as f:
            json.dump(job_requirements, f, indent=2)
        
        # Step 2: Match experiences with job requirements
        print("\n2. Matching experiences with job requirements...")
        matched_experiences = await experience_matcher.match_experiences(
            job_requirements, 
            PROFESSIONAL_PROFILE
        )
        
        # Save matched experiences to file for reference
        with open('matched_experiences_output.json', 'w') as f:
            json.dump(matched_experiences, f, indent=2)
        
        print("\nMatched Experiences:")
        print(json.dumps({
            "match_score": matched_experiences.get("match_score"),
            "relevance_reasoning": matched_experiences.get("relevance_reasoning"),
            "skills_to_emphasize": matched_experiences.get("skills_to_emphasize")
        }, indent=2))
        
        # Step 3: Create the resume with matched experiences
        output_path = "./generated_ecommerce_ops_resume.pdf"
        print(f"\n3. Generating resume at {output_path}...")
        
        # Prepare resume data format
        resume_data = {
            "personal_info": {
                "name": f"{PROFESSIONAL_PROFILE['user']['name']['first']} {PROFESSIONAL_PROFILE['user']['name']['last']}",
                "job_title": "Senior E-Commerce Operations Manager",  # Use the job title from posting
                "email": PROFESSIONAL_PROFILE['user']['contact']['email'],
                "phone": PROFESSIONAL_PROFILE['user']['contact']['phone'],
                "linkedin": PROFESSIONAL_PROFILE['user']['contact']['linkedin'],
                "location": f"{PROFESSIONAL_PROFILE['user']['contact']['location']['city']}, {PROFESSIONAL_PROFILE['user']['contact']['location']['state']}"
            },
            "professional_summary": matched_experiences.get("professional_summary", ""),
            "skills": matched_experiences.get("skills_to_emphasize", []),
            "experiences": matched_experiences.get("highlighted_experiences", []),
            "education": [
                {
                    "degree": edu["degree"],
                    "field": edu["field"],
                    "institution": edu["institution"],
                    "location": edu["location"],
                    "date_range": f"{edu.get('graduation_date', '')}"
                } for edu in PROFESSIONAL_PROFILE.get("education", [])
            ],
            "certifications": [
                {"name": cert["name"]} for cert in PROFESSIONAL_PROFILE.get("certifications", [])
            ]
        }
        
        # Generate the resume
        try:
            resume_engine.create_resume(resume_data, output_path=output_path)
            print(f"Resume successfully generated at {output_path}")
        except Exception as e:
            print(f"Error generating resume: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_with_job_posting())
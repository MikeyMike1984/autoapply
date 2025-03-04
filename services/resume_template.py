# file: fixed_resume_template.py
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import json

class ResumeTemplateEngine:
    """Generates PDF resumes with consistent formatting based on resume_pdf_format_data.json"""
    
    def __init__(self, font_dir="./fonts", format_file="resume_pdf_format_data.json"):
        self.font_dir = font_dir
        self.format_file = format_file
        
        # Ensure font directory exists
        os.makedirs(font_dir, exist_ok=True)
        
        # Load formatting data
        self.format_data = self._load_format_data()
        
        # Register fonts - you'll need to download these files
        self._register_fonts()
        
        # Define styles based on the template
        self.styles = self._create_styles()
    
    def _load_format_data(self):
        """Load formatting data from JSON file"""
        try:
            with open(self.format_file, 'r') as f:
                format_data = json.load(f)
            return format_data
        except Exception as e:
            print(f"Error loading format data: {e}")
            # Return a minimal default format
            return {
                "document": {
                    "page_count": 3,
                    "page_sizes": [{"width": 612.0, "height": 792.0}],
                    "fonts": {
                        "AAAAAA+Calibri-Bold": {"count": 3},
                        "BAAAAA+Calibri": {"count": 4},
                        "CAAAAA+ArialMT": {"count": 3}
                    }
                }
            }
    
    def _register_fonts(self):
        """Register fonts for use in PDFs"""
        # Check if fonts exist, if not, use default fonts
        calibri_path = os.path.join(self.font_dir, "calibri.ttf")
        calibrib_path = os.path.join(self.font_dir, "calibrib.ttf")
        arial_path = os.path.join(self.font_dir, "arial.ttf")  # Added for bullet points
        
        try:
            if os.path.exists(calibri_path):
                pdfmetrics.registerFont(TTFont('Calibri', calibri_path))
            if os.path.exists(calibrib_path):
                pdfmetrics.registerFont(TTFont('CalibriB', calibrib_path))
                pdfmetrics.registerFont(TTFont('Calibri-Bold', calibrib_path))  # Register with name from JSON
            if os.path.exists(arial_path):
                pdfmetrics.registerFont(TTFont('Arial', arial_path))
                pdfmetrics.registerFont(TTFont('ArialMT', arial_path))  # Register with name from JSON
            
            if not (os.path.exists(calibri_path) and os.path.exists(calibrib_path)):
                # Fall back to standard fonts
                print("Some fonts not found, using default fonts where needed")
        except Exception as e:
            print(f"Error registering fonts: {e}")
    
    def _create_styles(self):
        """Create paragraph styles for the resume based on format data"""
        # Start with an empty stylesheet instead of getSampleStyleSheet()
        # to avoid conflicts with the default styles
        from reportlab.lib.styles import StyleSheet1
        styles = StyleSheet1()
        
        # Extract font information from format data
        blocks = self.format_data.get("document", {}).get("text_blocks", [])
        
        # Name style (based on first text block - Name)
        name_block = next((b for b in blocks if "Mike Reeves" in b["text"]), None)
        if name_block:
            styles.add(ParagraphStyle(
                name='Name',
                fontName=name_block.get("font", 'Calibri-Bold') if name_block.get("font", 'Calibri-Bold') in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold',
                fontSize=name_block.get("font_size", 14),
                alignment=TA_LEFT,
                spaceAfter=2  # Adjusted based on format
            ))
        else:
            # Default name style
            styles.add(ParagraphStyle(
                name='Name',
                fontName='Calibri-Bold' if 'Calibri-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold',
                fontSize=14,
                alignment=TA_LEFT,
                spaceAfter=2
            ))
        
        # Job Title style
        job_title_block = next((b for b in blocks if "Senior Operations Manager" in b["text"]), None)
        if job_title_block:
            styles.add(ParagraphStyle(
                name='JobTitle',
                fontName=job_title_block.get("font", 'Calibri-Bold') if job_title_block.get("font", 'Calibri-Bold') in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold',
                fontSize=job_title_block.get("font_size", 11),
                alignment=TA_LEFT,
                spaceAfter=2
            ))
        else:
            # Default job title style
            styles.add(ParagraphStyle(
                name='JobTitle',
                fontName='Calibri-Bold' if 'Calibri-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold',
                fontSize=11,
                alignment=TA_LEFT,
                spaceAfter=2
            ))
        
        # Contact info style
        contact_block = next((b for b in blocks if "gmail.com" in b["text"]), None)
        if contact_block:
            styles.add(ParagraphStyle(
                name='ContactInfo',
                fontName=contact_block.get("font", 'Calibri') if contact_block.get("font", 'Calibri') in pdfmetrics.getRegisteredFontNames() else 'Helvetica',
                fontSize=contact_block.get("font_size", 10),
                alignment=TA_LEFT,
                spaceAfter=16
            ))
        else:
            # Default contact info style
            styles.add(ParagraphStyle(
                name='ContactInfo',
                fontName='Calibri' if 'Calibri' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',
                fontSize=10,
                alignment=TA_LEFT,
                spaceAfter=16
            ))
        
        # Section heading style
        section_block = next((b for b in blocks if b["text"] == "Professional Summary" or b["text"] == "Skills"), None)
        if section_block:
            styles.add(ParagraphStyle(
                name='SectionHeading',
                fontName=section_block.get("font", 'Calibri-Bold') if section_block.get("font", 'Calibri-Bold') in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold',
                fontSize=section_block.get("font_size", 13),
                alignment=TA_LEFT,
                spaceAfter=4,
                spaceBefore=14
            ))
        else:
            # Default section heading style
            styles.add(ParagraphStyle(
                name='SectionHeading',
                fontName='Calibri-Bold' if 'Calibri-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold',
                fontSize=13,
                alignment=TA_LEFT,
                spaceAfter=4,
                spaceBefore=14
            ))
        
        # Body text style
        body_block = next((b for b in blocks if "years of experience" in b["text"]), None)
        if body_block:
            styles.add(ParagraphStyle(
                name='BodyText',
                fontName=body_block.get("font", 'Calibri') if body_block.get("font", 'Calibri') in pdfmetrics.getRegisteredFontNames() else 'Helvetica',
                fontSize=body_block.get("font_size", 11),
                alignment=TA_LEFT,
                spaceAfter=3
            ))
        else:
            # Default body text style
            styles.add(ParagraphStyle(
                name='BodyText',
                fontName='Calibri' if 'Calibri' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',
                fontSize=11,
                alignment=TA_LEFT,
                spaceAfter=3
            ))
        
        # Bold body text style
        bold_block = next((b for b in blocks if b["font"] == "Calibri-Bold" and b["font_size"] == 11), None)
        if bold_block:
            styles.add(ParagraphStyle(
                name='BoldBodyText',
                fontName=bold_block.get("font", 'Calibri-Bold') if bold_block.get("font", 'Calibri-Bold') in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold',
                fontSize=bold_block.get("font_size", 11),
                alignment=TA_LEFT,
                spaceAfter=3
            ))
        else:
            # Default bold body text style
            styles.add(ParagraphStyle(
                name='BoldBodyText',
                fontName='Calibri-Bold' if 'Calibri-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold',
                fontSize=11,
                alignment=TA_LEFT,
                spaceAfter=3
            ))
        
        # Bullet style
        bullet_block = next((b for b in blocks if b["text"] == "•"), None)
        if bullet_block:
            styles.add(ParagraphStyle(
                name='Bullet',
                fontName='ArialMT' if 'ArialMT' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',
                fontSize=bullet_block.get("font_size", 11),
                alignment=TA_LEFT,
                leftIndent=18,
                firstLineIndent=-18,
                bulletIndent=0,
                spaceAfter=3
            ))
        else:
            # Default bullet style
            styles.add(ParagraphStyle(
                name='Bullet',
                fontName='ArialMT' if 'ArialMT' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',
                fontSize=11,
                alignment=TA_LEFT,
                leftIndent=18,
                firstLineIndent=-18,
                bulletIndent=0,
                spaceAfter=3
            ))
        
        # Bullet content style (text after the bullet)
        styles.add(ParagraphStyle(
            name='BulletContent',
            fontName='Calibri' if 'Calibri' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',
            fontSize=11,
            alignment=TA_LEFT,
            leftIndent=18,
            spaceAfter=3
        ))
        
        # Date range style
        styles.add(ParagraphStyle(
            name='DateRange',
            fontName='Calibri-Bold' if 'Calibri-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold',
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=8
        ))
        
        return styles
    
    def create_resume(self, resume_data, output_path="resume.pdf"):
        """Create a PDF resume using the provided data and format from resume_pdf_format_data.json"""
        # Set margins based on format data
        page_sizes = self.format_data.get("document", {}).get("page_sizes", [])
        if page_sizes:
            # Use 1-inch margins by default, adjust if needed based on format data
            margin = 72  # 1 inch in points
            
            # Calculate indentation from format data
            text_blocks = self.format_data.get("document", {}).get("text_blocks", [])
            left_pos = min([block["position"]["x0"] for block in text_blocks]) if text_blocks else margin
            
            # Adjust margin slightly
            left_margin = left_pos if left_pos < margin else margin
        else:
            left_margin = 1 * inch
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=LETTER,
            leftMargin=left_margin,
            rightMargin=1*inch,
            topMargin=1*inch,
            bottomMargin=1*inch
        )
        
        elements = []
        
        # Add header with name and job title
        name = resume_data["personal_info"]["name"]
        elements.append(Paragraph(name, self.styles['Name']))
        
        # Add job title if provided
        if "job_title" in resume_data["personal_info"]:
            elements.append(Paragraph(resume_data["personal_info"]["job_title"], self.styles['JobTitle']))
        
        # Contact info on a single line
        contact_info = " | ".join([
            resume_data["personal_info"]["email"],
            resume_data["personal_info"]["phone"],
            resume_data["personal_info"]["linkedin"],
            resume_data["personal_info"]["location"]
        ])
        elements.append(Paragraph(contact_info, self.styles['ContactInfo']))
        
        # Professional Summary
        elements.append(Paragraph("Professional Summary", self.styles['SectionHeading']))
        
        # Format the summary with bold text as specified in the format data
        # We'll use a combination of regular and bold text based on the JSON format
        # For simplicity, we'll just apply some key terms in bold like in the example
        summary = resume_data["professional_summary"]
        bold_terms = [
            "Results-driven", "10 years of experience", "high-volume", "manufacturing", 
            "distribution operations", "Lean techniques, team development", "quality and process improvements",
            "operational excellence", "optimizing fulfillment", "building strong cross-functional collaboration"
        ]
        
        # Apply bold formatting to key terms
        for term in bold_terms:
            if term in summary:
                summary = summary.replace(term, f"<b>{term}</b>")
        
        elements.append(Paragraph(summary, self.styles['BodyText']))
        
        # Skills
        elements.append(Paragraph("Skills", self.styles['SectionHeading']))
        
        # Format skills with bullet points and bold categories like in the sample
        skills = resume_data["skills"]
        
        # Create formatted skills sections with categories in bold
        skill_categories = [
            ("Operations Management", "Fulfillment center operations, inventory control, staffing lifecycle, KPI-driven performance, multi-site management."),
            ("Leadership & Development", "Team leadership, coaching and mentoring, cross-functional collaboration, leadership bench strength."),
            ("Process Improvement", "Lean Manufacturing, Six Sigma principles, continuous improvement, process change initiatives."),
            ("Technical Skills", "SQL, Power BI, VBA, Python, ERP systems integration, advanced Excel, data-driven decision-making."),
            ("Strategic Execution", "Strategic planning, forecasting, budget management, cost optimization, quality and safety compliance.")
        ]
        
        # Use actual skills from resume_data if possible
        if isinstance(skills, list) and len(skills) >= 5:
            # Assuming skills list has at least 5 categories
            for i, (category, _) in enumerate(skill_categories[:len(skills)]):
                skill_text = f"<bullet>\u2022</bullet> <b>{category}</b>: {skills[i]}"
                elements.append(Paragraph(skill_text, self.styles['Bullet']))
        else:
            # Use the template categories
            for category, details in skill_categories:
                skill_text = f"<bullet>\u2022</bullet> <b>{category}</b>: {details}"
                elements.append(Paragraph(skill_text, self.styles['Bullet']))
        
        # Professional Experience
        elements.append(Paragraph("Professional Experience", self.styles['SectionHeading']))
        
        for exp in resume_data["experiences"]:
            # Company and position - format according to the sample
            elements.append(Paragraph(f"<b>{exp['position']}</b>", self.styles['BoldBodyText']))
            
            # Add date range on same line if available
            if "date_range" in exp:
                elements.append(Paragraph(f"<b>{exp['date_range']}</b>", self.styles['DateRange']))
            
            # Company name
            elements.append(Paragraph(f"{exp['company']}", self.styles['BodyText']))
            
            # Bullet points
            for bullet in exp["bullet_points"]:
                # Check if there are any terms to make bold in this bullet point
                bullet_text = bullet
                if "highlights" in exp and exp["highlights"]:
                    for highlight in exp["highlights"]:
                        if highlight in bullet:
                            bullet_text = bullet.replace(highlight, f"<b>{highlight}</b>")
                
                elements.append(Paragraph(f"<bullet>\u2022</bullet> {bullet_text}", self.styles['Bullet']))
                
            elements.append(Spacer(1, 6))  # Slight spacing between experiences
        
        # Education
        if resume_data.get("education"):
            elements.append(Paragraph("Education", self.styles['SectionHeading']))
            
            for edu in resume_data["education"]:
                degree_text = f"<b>{edu['degree']}</b> in {edu['field']}"
                elements.append(Paragraph(degree_text, self.styles['BoldBodyText']))
                elements.append(Paragraph(f"{edu['institution']}, {edu['location']} | {edu.get('date_range', '')}", self.styles['BodyText']))
                elements.append(Spacer(1, 4))
        
        # Certifications
        if resume_data.get("certifications"):
            elements.append(Paragraph("Certifications", self.styles['SectionHeading']))
            
            for cert in resume_data["certifications"]:
                cert_text = f"<bullet>\u2022</bullet> {cert['name']}"
                elements.append(Paragraph(cert_text, self.styles['Bullet']))
        
        # Build the PDF
        doc.build(elements)
        
        return output_path
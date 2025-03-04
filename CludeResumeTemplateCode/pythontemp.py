from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class ResumeGenerator:
    def __init__(self, output_path):
        # Register fonts
        pdfmetrics.registerFont(TTFont('Calibri', 'calibri.ttf'))
        pdfmetrics.registerFont(TTFont('CalibriB', 'calibrib.ttf'))
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
        
        # Document setup
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=LETTER,
            leftMargin=1*inch,
            rightMargin=1*inch,
            topMargin=1*inch,
            bottomMargin=1*inch
        )
        
        # Define styles
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
        # Content elements
        self.elements = []
    
    def _setup_styles(self):
        # Name style
        self.styles.add(ParagraphStyle(
            name='Name',
            fontName='CalibriB',
            fontSize=14,
            alignment=TA_LEFT,
            spaceAfter=6
        ))
        
        # Job title style
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            fontName='CalibriB',
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=6
        ))
        
        # Contact info style
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            fontName='Calibri',
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=16
        ))
        
        # Section heading style
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            fontName='CalibriB',
            fontSize=13,
            alignment=TA_LEFT,
            spaceAfter=8,
            spaceBefore=16
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='BodyText',
            fontName='Calibri',
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=6
        ))
        
        # Bullet style (main)
        self.styles.add(ParagraphStyle(
            name='Bullet',
            fontName='Calibri',
            fontSize=11,
            alignment=TA_LEFT,
            leftIndent=18,
            firstLineIndent=-18,
            bulletIndent=0,
            spaceAfter=3
        ))
        
        # Sub-bullet style
        self.styles.add(ParagraphStyle(
            name='SubBullet',
            fontName='Calibri',
            fontSize=11,
            alignment=TA_LEFT,
            leftIndent=36,
            firstLineIndent=-18,
            bulletIndent=18,
            spaceAfter=3
        ))
        
        # Job title bold
        self.styles.add(ParagraphStyle(
            name='JobTitleBold',
            fontName='CalibriB',
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=3
        ))
        
        # Date range
        self.styles.add(ParagraphStyle(
            name='DateRange',
            fontName='CalibriB',
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=8
        ))
    
    def add_header(self, name, title, contact_info):
        self.elements.append(Paragraph(name, self.styles['Name']))
        self.elements.append(Paragraph(title, self.styles['JobTitle']))
        self.elements.append(Paragraph(contact_info, self.styles['ContactInfo']))
    
    def add_section_heading(self, heading):
        self.elements.append(Paragraph(heading, self.styles['SectionHeading']))
    
    def add_paragraph(self, text):
        self.elements.append(Paragraph(text, self.styles['BodyText']))
    
    def add_job(self, title, company, date_range):
        self.elements.append(Paragraph(title, self.styles['JobTitleBold']))
        self.elements.append(Paragraph(company, self.styles['BodyText']))
        self.elements.append(Paragraph(date_range, self.styles['DateRange']))
    
    def add_bullet(self, text, is_sub_bullet=False):
        style = self.styles['SubBullet'] if is_sub_bullet else self.styles['Bullet']
        bullet_text = f"<bullet>\u2022</bullet> {text}"
        self.elements.append(Paragraph(bullet_text, style))
    
    def build(self):
        self.doc.build(self.elements)
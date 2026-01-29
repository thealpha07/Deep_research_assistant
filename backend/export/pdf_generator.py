"""
PDF Generator with IEEE Formatting
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether
)
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime
import os

from templates.ieee_format.ieee_template import IEEEFormat, DocumentStructure
from config import Config


class IEEEPDFGenerator:
    """Generate IEEE-formatted PDF documents"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or Config.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup styles
        self.styles = self._create_styles()
    
    def generate(self, research_data: dict, filename: str = None) -> str:
        """
        Generate PDF from research data
        
        Args:
            research_data: Dict with topic, synthesis, bibliography, metadata
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to generated PDF
        """
        if filename is None:
            topic_slug = research_data['topic'].replace(' ', '_')[:50]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"research_{topic_slug}_{timestamp}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            leftMargin=IEEEFormat.MARGIN_LEFT,
            rightMargin=IEEEFormat.MARGIN_RIGHT,
            topMargin=IEEEFormat.MARGIN_TOP,
            bottomMargin=IEEEFormat.MARGIN_BOTTOM
        )
        
        # Build content
        story = []
        
        # Title
        story.append(Paragraph(research_data['topic'], self.styles['Title']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Author and date
        author_text = "Deep Research Assistant"
        date_text = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(author_text, self.styles['Author']))
        story.append(Paragraph(date_text, self.styles['Author']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Parse and add content sections
        synthesis = research_data.get('synthesis', '')
        sections = self._parse_sections(synthesis)
        
        for i, (section_title, section_content) in enumerate(sections):
            # Section heading
            if IEEEFormat.USE_SECTION_NUMBERS and section_title.upper() != 'ABSTRACT':
                section_num = DocumentStructure.get_section_number(i)
                heading = f"{section_num}. {section_title.upper()}"
            else:
                heading = section_title.upper()
            
            story.append(Paragraph(heading, self.styles['Heading1']))
            story.append(Spacer(1, 0.1 * inch))
            
            # Section content
            paragraphs = section_content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), self.styles['BodyText']))
                    story.append(Spacer(1, 0.05 * inch))
        
        # Bibliography
        bibliography = research_data.get('bibliography', '')
        if bibliography:
            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph("REFERENCES", self.styles['Heading1']))
            story.append(Spacer(1, 0.1 * inch))
            
            # Parse references
            ref_lines = bibliography.split('\n')
            for line in ref_lines:
                if line.strip() and line.strip() != 'REFERENCES':
                    story.append(Paragraph(line.strip(), self.styles['Reference']))
                    story.append(Spacer(1, 0.05 * inch))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, 
                 onLaterPages=self._add_header_footer)
        
        return filepath
    
    def _create_styles(self):
        """Create custom styles for IEEE format"""
        styles = getSampleStyleSheet()
        
        # Define styles configuration
        style_configs = [
            {
                'name': 'Title',
                'parent': 'Heading1', 
                'fontSize': IEEEFormat.FONT_SIZE_TITLE,
                'textColor': colors.black,
                'spaceAfter': 12,
                'alignment': TA_CENTER,
                'fontName': 'Times-Bold'
            },
            {
                'name': 'Author',
                'parent': 'Normal',
                'fontSize': IEEEFormat.FONT_SIZE_AUTHORS,
                'textColor': colors.black,
                'alignment': TA_CENTER,
                'fontName': 'Times-Roman'
            },
            {
                'name': 'BodyText',
                'parent': 'Normal',
                'fontSize': IEEEFormat.FONT_SIZE_BODY,
                'leading': IEEEFormat.FONT_SIZE_BODY * 1.2,
                'alignment': TA_JUSTIFY,
                'fontName': 'Times-Roman',
                'spaceAfter': IEEEFormat.PARAGRAPH_SPACING
            },
            {
                'name': 'Heading1',
                'parent': 'Heading1',
                'fontSize': IEEEFormat.FONT_SIZE_SECTION,
                'textColor': colors.black,
                'spaceBefore': IEEEFormat.SECTION_SPACING_BEFORE,
                'spaceAfter': IEEEFormat.SECTION_SPACING_AFTER,
                'fontName': 'Times-Bold',
                'alignment': TA_CENTER
            },
            {
                'name': 'Abstract',
                'parent': 'Normal',
                'fontSize': IEEEFormat.FONT_SIZE_ABSTRACT,
                'leading': IEEEFormat.FONT_SIZE_ABSTRACT * 1.2,
                'alignment': TA_JUSTIFY,
                'fontName': 'Times-Italic',
                'leftIndent': IEEEFormat.ABSTRACT_INDENT,
                'rightIndent': IEEEFormat.ABSTRACT_INDENT
            },
            {
                'name': 'Reference',
                'parent': 'Normal',
                'fontSize': IEEEFormat.FONT_SIZE_REFERENCES,
                'leading': IEEEFormat.FONT_SIZE_REFERENCES * 1.2,
                'alignment': TA_LEFT,
                'fontName': 'Times-Roman',
                'leftIndent': IEEEFormat.REFERENCE_INDENT,
                'firstLineIndent': -IEEEFormat.REFERENCE_INDENT
            }
        ]

        for config in style_configs:
            name = config.pop('name')
            parent_name = config.pop('parent')
            
            if name in styles:
                style = styles[name]
                for key, value in config.items():
                    setattr(style, key, value)
            else:
                parent = styles[parent_name]
                styles.add(ParagraphStyle(name=name, parent=parent, **config))
        
        return styles
    
    def _parse_sections(self, text: str) -> list:
        """Parse text into sections"""
        sections = []
        current_section = None
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            # Check if line is a section heading
            if self._is_section_heading(line):
                # Save previous section
                if current_section:
                    sections.append((current_section, '\n'.join(current_content)))
                
                # Start new section
                current_section = line.strip().replace('#', '').strip()
                current_content = []
            else:
                if line.strip():
                    current_content.append(line)
        
        # Add last section
        if current_section:
            sections.append((current_section, '\n'.join(current_content)))
        
        return sections
    
    def _is_section_heading(self, line: str) -> bool:
        """Check if line is a section heading"""
        line = line.strip()
        
        # Check for markdown headings
        if line.startswith('#'):
            return True
        
        # Check for common section titles
        common_sections = [
            'abstract', 'introduction', 'background', 'methodology',
            'results', 'discussion', 'conclusion', 'references',
            'literature review', 'main findings', 'future work'
        ]
        
        return any(section in line.lower() for section in common_sections)
    
    def _add_header_footer(self, canvas_obj, doc):
        """Add header and footer to pages"""
        canvas_obj.saveState()
        
        # Footer with page number
        page_num = canvas_obj.getPageNumber()
        text = f"{page_num}"
        canvas_obj.setFont('Times-Roman', 9)
        canvas_obj.drawCentredString(
            IEEEFormat.PAGE_WIDTH / 2,
            0.5 * inch,
            text
        )
        
        canvas_obj.restoreState()

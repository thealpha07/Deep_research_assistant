"""
IEEE Format Template Specifications
"""

class IEEEFormat:
    """IEEE paper format specifications"""
    
    # Page settings
    PAGE_SIZE = 'letter'  # 8.5 x 11 inches
    PAGE_WIDTH = 8.5 * 72  # points
    PAGE_HEIGHT = 11 * 72  # points
    
    # Margins (in points, 1 inch = 72 points)
    MARGIN_TOP = 0.75 * 72
    MARGIN_BOTTOM = 1 * 72
    MARGIN_LEFT = 0.625 * 72
    MARGIN_RIGHT = 0.625 * 72
    
    # Column settings
    COLUMN_COUNT = 2
    COLUMN_GAP = 0.25 * 72
    
    # Calculate column width
    COLUMN_WIDTH = (PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT - COLUMN_GAP) / 2
    
    # Font settings
    FONT_FAMILY = 'Times-Roman'
    FONT_SIZE_BODY = 10
    FONT_SIZE_TITLE = 24
    FONT_SIZE_AUTHORS = 12
    FONT_SIZE_ABSTRACT = 9
    FONT_SIZE_SECTION = 10
    FONT_SIZE_SUBSECTION = 10
    FONT_SIZE_CAPTION = 9
    FONT_SIZE_REFERENCES = 9
    
    # Spacing
    LINE_SPACING = 1.0
    PARAGRAPH_SPACING = 6
    SECTION_SPACING_BEFORE = 12
    SECTION_SPACING_AFTER = 6
    
    # Section numbering
    USE_SECTION_NUMBERS = True
    SECTION_NUMBER_STYLE = 'I'  # Roman numerals
    
    # Abstract
    ABSTRACT_MAX_WORDS = 250
    ABSTRACT_INDENT = 0.25 * 72
    
    # Keywords
    KEYWORDS_LABEL = "Index Terms"
    
    # References
    REFERENCES_HEADING = "REFERENCES"
    REFERENCE_INDENT = 0.25 * 72
    
    @staticmethod
    def get_section_style():
        """Get section heading style"""
        return {
            'fontName': IEEEFormat.FONT_FAMILY,
            'fontSize': IEEEFormat.FONT_SIZE_SECTION,
            'fontWeight': 'bold',
            'spaceBefore': IEEEFormat.SECTION_SPACING_BEFORE,
            'spaceAfter': IEEEFormat.SECTION_SPACING_AFTER,
            'alignment': 'left'
        }
    
    @staticmethod
    def get_body_style():
        """Get body text style"""
        return {
            'fontName': IEEEFormat.FONT_FAMILY,
            'fontSize': IEEEFormat.FONT_SIZE_BODY,
            'leading': IEEEFormat.FONT_SIZE_BODY * IEEEFormat.LINE_SPACING,
            'alignment': 'justify',
            'spaceBefore': 0,
            'spaceAfter': IEEEFormat.PARAGRAPH_SPACING
        }
    
    @staticmethod
    def get_title_style():
        """Get title style"""
        return {
            'fontName': IEEEFormat.FONT_FAMILY,
            'fontSize': IEEEFormat.FONT_SIZE_TITLE,
            'fontWeight': 'bold',
            'alignment': 'center',
            'spaceBefore': 12,
            'spaceAfter': 12
        }
    
    @staticmethod
    def get_abstract_style():
        """Get abstract style"""
        return {
            'fontName': IEEEFormat.FONT_FAMILY,
            'fontSize': IEEEFormat.FONT_SIZE_ABSTRACT,
            'fontStyle': 'italic',
            'alignment': 'justify',
            'leftIndent': IEEEFormat.ABSTRACT_INDENT,
            'rightIndent': IEEEFormat.ABSTRACT_INDENT
        }


class DocumentStructure:
    """Standard IEEE paper structure"""
    
    SECTIONS = [
        'Abstract',
        'Introduction',
        'Background',
        'Methodology',
        'Results',
        'Discussion',
        'Conclusion',
        'References'
    ]
    
    @staticmethod
    def get_section_number(index: int) -> str:
        """Get section number in Roman numerals"""
        roman_numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
        if index < len(roman_numerals):
            return roman_numerals[index]
        return str(index + 1)

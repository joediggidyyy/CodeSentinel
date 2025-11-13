#!/usr/bin/env python3
"""
PDF Conversion Utilities for CodeSentinel
Provides professional markdown to PDF conversion with formatting preservation
"""

import re
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Frame, PageTemplate
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def parse_markdown_to_elements(md_content, doc_title="CodeSentinel Document"):
    """Parse markdown content into ReportLab elements with professional styling"""
    elements = []
    styles = getSampleStyleSheet()

    # Professional color scheme
    primary_blue = colors.HexColor('#1a365d')  # Dark navy blue
    secondary_blue = colors.HexColor('#2b77e6')  # Medium blue
    accent_blue = colors.HexColor('#4299e1')  # Light blue
    text_gray = colors.HexColor('#2d3748')  # Dark gray for text
    light_gray = colors.HexColor('#f7fafc')  # Very light gray for backgrounds
    border_gray = colors.HexColor('#e2e8f0')  # Light gray for borders

    # Enhanced styles with professional typography
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=28,
        fontName='Helvetica-Bold',
        spaceAfter=40,
        spaceBefore=20,
        alignment=TA_CENTER,
        textColor=primary_blue,
        underlineColor=secondary_blue,
        underlineWidth=2,
        underlineOffset=-2,
        borderColor=accent_blue,
        borderWidth=0,
        borderPadding=10,
    )

    heading1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Heading1'],
        fontSize=22,
        fontName='Helvetica-Bold',
        spaceAfter=25,
        spaceBefore=35,
        textColor=primary_blue,
        borderColor=border_gray,
        borderWidth=0,
        borderPadding=5,
        leftIndent=0,
    )

    heading2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontSize=18,
        fontName='Helvetica-Bold',
        spaceAfter=20,
        spaceBefore=30,
        textColor=secondary_blue,
        leftIndent=0,
    )

    heading3_style = ParagraphStyle(
        'Heading3',
        parent=styles['Heading3'],
        fontSize=14,
        fontName='Helvetica-Bold',
        spaceAfter=15,
        spaceBefore=25,
        textColor=text_gray,
        leftIndent=0,
    )

    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica',
        spaceAfter=12,
        spaceBefore=6,
        textColor=text_gray,
        alignment=TA_JUSTIFY,
        leading=14,  # Line height
        leftIndent=0,
        rightIndent=0,
    )

    code_style = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=9,
        backColor=light_gray,
        borderColor=border_gray,
        borderWidth=1,
        borderPadding=8,
        leftIndent=15,
        rightIndent=15,
        spaceAfter=15,
        spaceBefore=10,
        textColor=colors.HexColor('#1a202c'),
    )

    blockquote_style = ParagraphStyle(
        'Blockquote',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Oblique',
        backColor=colors.HexColor('#f0f9ff'),
        borderColor=accent_blue,
        borderWidth=3,
        borderPadding=12,
        leftIndent=20,
        rightIndent=20,
        spaceAfter=15,
        spaceBefore=10,
        textColor=colors.HexColor('#2c5282'),
    )

    # Add document title
    elements.append(Paragraph(doc_title, title_style))
    elements.append(Spacer(1, 30))

    # Split content into lines
    lines = md_content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Headers
        if line.startswith('# '):
            elements.append(PageBreak())  # Page break before main sections
            elements.append(Paragraph(line[2:], heading1_style))
        elif line.startswith('## '):
            elements.append(Spacer(1, 20))  # Extra space before subsections
            elements.append(Paragraph(line[3:], heading2_style))
        elif line.startswith('### '):
            elements.append(Spacer(1, 15))
            elements.append(Paragraph(line[4:], heading3_style))

        # Code blocks
        elif line.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            code_content = '\n'.join(code_lines)
            # Use pre-formatted text for code blocks
            elements.append(Paragraph(f'<font face="Courier" size="9">{code_content}</font>', code_style))

        # Blockquotes
        elif line.startswith('> '):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith('> '):
                quote_lines.append(lines[i].strip()[2:])
                i += 1
            i -= 1  # Adjust for the outer loop
            quote_content = ' '.join(quote_lines)
            elements.append(Paragraph(quote_content, blockquote_style))

        # Tables (enhanced support)
        elif '|' in line and i + 1 < len(lines) and '|' in lines[i + 1] and re.match(r'^\s*\|.*\|\s*$', lines[i + 1]):
            table_data = []
            # Header row
            header_cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if not header_cells:
                i += 1
                continue
            table_data.append(header_cells)

            # Separator row (skip)
            i += 1

            # Data rows
            i += 1
            max_cols = len(header_cells)
            while i < len(lines) and '|' in lines[i]:
                row_cells = [cell.strip() for cell in lines[i].split('|')[1:-1]]
                if row_cells and any(cell for cell in row_cells):
                    # Ensure all rows have the same number of columns
                    while len(row_cells) < max_cols:
                        row_cells.append('')
                    row_cells = row_cells[:max_cols]  # Truncate if too many
                    table_data.append(row_cells)
                else:
                    break
                i += 1
            i -= 1  # Adjust for the outer loop

            if len(table_data) > 1:
                # Calculate column widths based on content
                num_cols = len(header_cells)
                if num_cols > 0:
                    col_width = 15*cm / num_cols
                    table = Table(table_data, colWidths=[col_width] * num_cols)

                    # Build table style dynamically based on actual table size
                    table_style_commands = [
                        # Header styling
                        ('BACKGROUND', (0, 0), (-1, 0), primary_blue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),

                        # Body styling
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('TEXTCOLOR', (0, 1), (-1, -1), text_gray),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                        ('VALIGN', (0, 1), (-1, -1), 'TOP'),

                        # Grid styling
                        ('GRID', (0, 0), (-1, -1), 0.5, border_gray),
                        ('BOX', (0, 0), (-1, -1), 1, primary_blue),
                    ]

                    # Add alternating row colors safely
                    num_rows = len(table_data)
                    for row_idx in range(2, num_rows, 2):  # Start from row 2 (0-indexed), every other row
                        if row_idx < num_rows:
                            table_style_commands.append(('BACKGROUND', (0, row_idx), (-1, row_idx), colors.HexColor('#f8fafc')))

                    table_style = TableStyle(table_style_commands)
                    table.setStyle(table_style)
                    elements.append(Spacer(1, 15))
                    elements.append(table)
                    elements.append(Spacer(1, 15))

        # Lists
        elif line.startswith('- ') or line.startswith('* '):
            list_items = []
            while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                item_text = lines[i].strip()[2:]
                list_items.append(item_text)
                i += 1
            i -= 1  # Adjust for the outer loop

            bullet_style = ParagraphStyle(
                'Bullet',
                parent=normal_style,
                leftIndent=20,
                bulletIndent=10,
                spaceAfter=8,
            )

            for item in list_items:
                elements.append(Paragraph(f"• {item}", bullet_style))

        # Numbered lists
        elif re.match(r'^\d+\.\s', line):
            list_items = []
            while i < len(lines) and re.match(r'^\d+\.\s', lines[i].strip()):
                match = re.match(r'^\d+\.\s(.*)', lines[i].strip())
                if match:
                    item_text = match.group(1)
                    list_items.append(item_text)
                i += 1
            i -= 1  # Adjust for the outer loop

            for idx, item in enumerate(list_items, 1):
                numbered_style = ParagraphStyle(
                    f'Numbered{idx}',
                    parent=normal_style,
                    leftIndent=20,
                    spaceAfter=8,
                )
                elements.append(Paragraph(f"{idx}. {item}", numbered_style))

        # Regular paragraphs
        elif line:
            # Handle inline code and links
            line = re.sub(r'`([^`]+)`', r'<font face="Courier" size="9" color="#1a202c">\1</font>', line)
            # Convert markdown links to plain text (remove the URL part)
            line = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<font color="#2b77e6"><u>\1</u></font>', line)
            # Remove internal reference links like [text](#anchor)
            line = re.sub(r'\[([^\]]+)\]\(#([^)]+)\)', r'<font color="#2b77e6"><u>\1</u></font>', line)
            elements.append(Paragraph(line, normal_style))

        i += 1

    return elements


def create_professional_pdf_template(doc_title):
    """Create a professional PDF template with headers and footers"""

    def header_footer(canvas, doc):
        canvas.saveState()

        # Header
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.HexColor('#1a365d'))
        canvas.drawString(2.5*cm, 27.5*cm, doc_title)

        # Footer with page number
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#718096'))
        page_num = canvas.getPageNumber()
        canvas.drawRightString(18*cm, 1.5*cm, f"Page {page_num}")

        # Subtle border
        canvas.setStrokeColor(colors.HexColor('#e2e8f0'))
        canvas.setLineWidth(0.5)
        canvas.rect(2*cm, 2*cm, 16*cm, 25*cm, stroke=1, fill=0)

        canvas.restoreState()

    # Create frame and template
    frame = Frame(2.5*cm, 3*cm, 15*cm, 24*cm, id='normal')
    template = PageTemplate(id='professional', frames=frame, onPage=header_footer)

    return template


def convert_md_to_pdf(md_file_path, pdf_file_path):
    """Convert a markdown file to PDF with professional styling"""

    # Read markdown content
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Extract title from first header or filename
    title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    doc_title = title_match.group(1).strip() if title_match else Path(md_file_path).stem.replace('_', ' ')

    # Create PDF document with professional template
    doc = SimpleDocTemplate(
        pdf_file_path,
        pagesize=A4,
        rightMargin=2.5*cm,
        leftMargin=2.5*cm,
        topMargin=4*cm,
        bottomMargin=3*cm,
        title=doc_title,
        author="CodeSentinel",
        subject="Technical Documentation",
        creator="CodeSentinel PDF Generator"
    )

    # Add professional template
    template = create_professional_pdf_template(doc_title)
    doc.addPageTemplates([template])

    # Parse markdown to elements
    elements = parse_markdown_to_elements(md_content, doc_title)

    # Build PDF
    doc.build(elements)
    print(f"Successfully converted {md_file_path} to {pdf_file_path}")


def handle_pdf_command(args, sentinel):
    """Handle 'codesentinel pdf' command."""
    if not args.files:
        print("Error: No input files specified. Use 'codesentinel pdf --files file1.md file2.md'")
        return

    converted_count = 0
    for md_file in args.files:
        if not Path(md_file).exists():
            print(f"Warning: File {md_file} does not exist, skipping")
            continue

        if not md_file.lower().endswith('.md'):
            print(f"Warning: File {md_file} is not a markdown file, skipping")
            continue

        # Generate PDF filename
        pdf_file = str(Path(md_file).with_suffix('.pdf'))

        try:
            convert_md_to_pdf(md_file, pdf_file)
            converted_count += 1
        except Exception as e:
            print(f"Error converting {md_file}: {e}")

    print(f"PDF conversion complete. Converted {converted_count} files.")


def add_pdf_subparser(subparsers):
    """Add PDF conversion subcommand to the argument parser."""
    pdf_parser = subparsers.add_parser(
        'pdf',
        help='Convert markdown files to PDF format'
    )
    pdf_parser.add_argument(
        '--files',
        nargs='+',
        required=True,
        help='Markdown files to convert to PDF'
    )
    pdf_parser.set_defaults(func=handle_pdf_command)
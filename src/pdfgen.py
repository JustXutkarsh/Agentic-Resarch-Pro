from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY

def generate_pdf(summary, insights, pros_cons, citations, output_path="research_report.pdf"):
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    normal.spaceAfter = 12

    story = []

    # Title
    title = "<para align='center'><b><font size=16>Research Report</font></b></para>"
    story.append(Paragraph(title, normal))
    story.append(Spacer(1, 0.3 * inch))

    # Summary
    story.append(Paragraph("<b>1. Research Summary</b>", normal))
    story.append(Paragraph(summary.replace("\n", "<br/>"), normal))
    story.append(Spacer(1, 0.2 * inch))

    # Insights
    story.append(Paragraph("<b>2. Key Insights</b>", normal))
    if insights:
        for item in insights:
            story.append(Paragraph("• " + item, normal))
    else:
        story.append(Paragraph("No validated insights available.", normal))
    story.append(Spacer(1, 0.2 * inch))

    # Pros and Cons
    story.append(Paragraph("<b>3. Pros & Cons</b>", normal))
    story.append(Paragraph("<b>Pros:</b>", normal))
    for p in pros_cons.get("pros", []):
        story.append(Paragraph("• " + p, normal))

    story.append(Paragraph("<b>Cons:</b>", normal))
    for c in pros_cons.get("cons", []):
        story.append(Paragraph("• " + c, normal))
    story.append(Spacer(1, 0.2 * inch))

    # Citations
    story.append(Paragraph("<b>4. Citations</b>", normal))
    if citations:
        for url in citations:
            story.append(Paragraph("• " + url, normal))
    else:
        story.append(Paragraph("No citations available.", normal))

    doc = SimpleDocTemplate(output_path, pagesize=letter)
    doc.build(story)

    return output_path

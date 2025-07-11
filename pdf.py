from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import textwrap
from PIL import Image

def generate_branded_pdf(customer_logo_path, customer_name, silni_logo_path,
                         title, metadata, call_script_text, flowchart_img):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = inch * 0.75

    # Page 1: Branding + Main Title + Metadata Box
    silni_logo = ImageReader(silni_logo_path)
    cust_logo = ImageReader(customer_logo_path)
    c.drawImage(
        silni_logo,
        inch * 0.5,
        height - inch * 1,
        width=inch * 1.5,
        height=inch * 0.75,
        preserveAspectRatio=True,
    )
    c.drawImage(
        cust_logo,
        width - inch * 2,
        height - inch * 1,
        width=inch * 1.5,
        height=inch * 0.75,
        preserveAspectRatio=True,
    )
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - inch * 1.4, "Deal Closing Strategy Document")

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - inch * 2.1, customer_name)

    # Engagement Overview
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, height - inch * 3, "Engagement Overview")

    c.setFont("Helvetica", 12)
    text_lines = [
        f"Title: {title}",
        f"Objective: {metadata.get('objective', '')}",
        f"Framework used: {metadata.get('framework', '')}"
    ]

    y = height - inch * 3.4
    for line in text_lines:
        c.drawString(margin, y, line)
        y -= 14

    c.showPage()

    # Page 2+: Script content with clear headings
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - margin, "📞 Deal Closing Call Script")
    y = height - margin * 1.5

    c.setFont("Helvetica", 12)
    line_height = 14
    max_line_chars = 100

    wrapped_lines = []
    for paragraph in call_script_text.split('\n'):
        if not paragraph.strip() and (not wrapped_lines or wrapped_lines[-1] != ""):
            wrapped_lines.append("")
        elif paragraph.strip():
            lines = textwrap.wrap(paragraph, width=max_line_chars)
            if not lines and paragraph.strip():
                lines = [paragraph.strip()]
            wrapped_lines.extend(lines)
            wrapped_lines.append("")

    text_obj = c.beginText(margin, y)
    for line in wrapped_lines:
        if text_obj.getY() < margin + line_height:
            c.drawText(text_obj)
            c.showPage()
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width / 2, height - margin, "📞 Deal Closing Call Script (cont’d)")
            c.setFont("Helvetica", 12)
            text_obj = c.beginText(margin, height - margin * 1.5)
        text_obj.textLine(line)
    c.drawText(text_obj)
    c.showPage()

    # Final Page: Diagram
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - margin, "🧭 Deal Flowchart")

    # --- CORRECTED IMAGE DIMENSION RETRIEVAL ---
    pil_img = None
    if isinstance(flowchart_img, io.BytesIO):
        flowchart_img.seek(0)
        pil_img = Image.open(flowchart_img)

        # Ensure the image is in a format ReportLab can handle well (PNG is robust)
        temp_img_buffer = io.BytesIO()
        pil_img.save(temp_img_buffer, format="PNG")
        temp_img_buffer.seek(0)
        img_to_draw = ImageReader(temp_img_buffer) # This is the object to pass to drawImage
    else:
        # Fallback for other potential types, though app.py should ensure BytesIO
        img_to_draw = ImageReader(flowchart_img)


    # Get dimensions from the PIL Image object (pil_img)
    if pil_img:
        img_width_px, img_height_px = pil_img.size
    else:
        # Fallback if PIL image could not be opened (should not happen with BytesIO)
        # These values will determine scaling if PIL image wasn't successfully loaded.
        # It's better to ensure pil_img is always created successfully above.
        img_width_px = 800 # Default reasonable width in pixels
        img_height_px = 600 # Default reasonable height in pixels

    dpi = 96 # assumed DPI, standard for screen output. Adjust if your Graphviz renders at a different DPI.
    img_width_pt = (img_width_px / dpi) * 72 # Convert pixels to points (1 inch = 72 points)
    img_height_pt = (img_height_px / dpi) * 72


    max_img_width = width - 2 * margin
    max_img_height = height - 2 * margin - inch * 0.5
    scale = min(max_img_width / img_width_pt, max_img_height / img_height_pt, 1.0)

    img_width_scaled = img_width_pt * scale
    img_height_scaled = img_height_pt * scale
    x = (width - img_width_scaled) / 2
    y = (height - img_height_scaled) / 2 - inch * 0.25

    c.drawImage(img_to_draw, x, y, width=img_width_scaled, height=img_height_scaled)

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
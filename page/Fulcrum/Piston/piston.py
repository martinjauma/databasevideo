import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import blue
from reportlab.lib.utils import ImageReader
import json
import io
import os
from PIL import Image

def generate_pdf_with_angles(session_name, angles_info):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Rutas relativas a la carpeta del script
    logo_fulcrum_path = os.path.join("img", "fulcrum_logo.png")
    logo_sra_path = os.path.join("img", "sra_logo.png")
    logo_width = 1.5 * inch
    logo_height = 0.75 * inch

    # Dibujar logos si existen
    try:
        c.drawImage(ImageReader(logo_fulcrum_path), x=inch * 0.5, y=height - logo_height - 0.5 * inch, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        print(f"⚠️ No se pudo cargar fulcrum_logo.png: {e}")

    try:
        c.drawImage(ImageReader(logo_sra_path), x=width - logo_width - inch * 0.5, y=height - logo_height - 0.5 * inch, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        print(f"⚠️ No se pudo cargar sra_logo.png: {e}")

    # Título
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - inch, f"Partido: {session_name}")

    # Subtítulo
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(width / 2, height - inch - 20, "Links de videos (.mp4) por ángulo")

    # Links
    start_y = height - inch * 2
    line_height = 18
    margin_x = inch * 0.75
    c.setFont("Helvetica", 10)

    for idx, angle in enumerate(angles_info):
        y_pos = start_y - idx * line_height

        if y_pos < inch:
            c.showPage()
            y_pos = height - inch * 1.5
            c.setFont("Helvetica", 10)

        angle_name = angle["angle_name"]
        full_url = angle["angle_m3u8_url"].replace(".m3u8", ".mp4")

        display_url = full_url if len(full_url) <= 90 else full_url[:90] + "..."
        text = f"{angle_name}: {display_url}"

        c.setFillColor(blue)
        c.drawString(margin_x, y_pos, text)
        text_width = c.stringWidth(text, "Helvetica", 10)
        c.linkURL(full_url, (margin_x, y_pos - 2, margin_x + text_width, y_pos + 10), relative=0)

    # Footer
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Oblique", 9)
    c.drawRightString(width - inch * 0.5, 0.5 * inch, "Generado por Martín Jauma - Rugby Data")

    c.save()
    buffer.seek(0)
    return buffer


# 🌐 Streamlit UI
st.set_page_config(page_title="Generador PDF HLS", page_icon="🎬")

st.title("🎬 Generador de PDF desde JSON de HLS")
st.markdown("Cargá un JSON HLS de Piston Cloud")

json_input = st.text_area("📥 Pegá el JSON con los HLS", height=350, placeholder='Ejemplo:\n{\n  "session_name": "Argentina vs Chile",\n  "angles": [\n    {"angle_name": "Frontal", "angle_m3u8_url": "https://example.com/frontal.m3u8"},\n    {"angle_name": "Dron", "angle_m3u8_url": "https://example.com/dron.m3u8"}\n  ]\n}')

if st.button("🎯 Generar PDF"):
    if not json_input.strip():
        st.error("❌ Pegá el JSON para continuar.")
    else:
        try:
            data = json.loads(json_input)

            if "session_name" not in data or "angles" not in data:
                st.error("❌ El JSON no contiene los campos 'session_name' y 'angles'.")
            else:
                session_name = data["session_name"]
                angles = data["angles"]

                if not isinstance(angles, list) or not all("angle_m3u8_url" in angle and "angle_name" in angle for angle in angles):
                    st.error("❌ Cada ángulo debe contener 'angle_name' y 'angle_m3u8_url'.")
                else:
                    pdf_buffer = generate_pdf_with_angles(session_name, angles)
                    st.success(f"✅ PDF generado para {session_name}")
                    st.download_button("📄 Descargar PDF", data=pdf_buffer, file_name=f"{session_name}.pdf", mime="application/pdf")

        except json.JSONDecodeError:
            st.error("❌ El texto ingresado no es un JSON válido.")

import models
from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas
from io import BytesIO


class To2PdfManagerMixin(models.AbstractModel):

    _name = "res.document.sign"
    
    A4_WIDTH = 595.276
    A4_HEIGHT = 841.890
    SCALE_FACTOR_X = 0.95  # 95%
    SCALE_FACTOR_Y = 0.90  # 90%
    FOOTER_HEIGHT = A4_HEIGHT * 0.20  # El 10% de la página
    FOOTER_TEXT = "Firma: Lorenzo Gómez - Empresa TiOdoo"  # Personaliza este texto

    # Método que crea y añade el footer
    def create_footer():
        # Crear un archivo PDF en memoria con el footer
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=(A4_WIDTH, A4_HEIGHT))

        # Establecer el fondo rojo
        c.setFillColorRGB(1, 0, 0)  # Color de fondo rojo
        c.rect(0, 0, A4_WIDTH, FOOTER_HEIGHT, fill=1)  # Dibujar el rectángulo con fondo rojo

        # Estilo del texto (fuente blanca)
        c.setFillColorRGB(1, 1, 1)  # Color blanco para el texto
        c.setFont("Helvetica-Bold", 10)

        # Dibujar el texto del footer (centrado en el área del footer)
        c.drawString(A4_WIDTH / 2 - len(FOOTER_TEXT) * 3, FOOTER_HEIGHT / 2 - 5, FOOTER_TEXT)  # Ajustar la posición

        # Dibujar una línea divisoria en el footer (color negro)
        c.setStrokeColorRGB(0, 0, 0)  # Color negro para la línea
        c.setLineWidth(0.5)
        c.line(20, FOOTER_HEIGHT, A4_WIDTH - 20, FOOTER_HEIGHT)  # Línea horizontal en la parte inferior

        c.save()
        packet.seek(0)
        return packet


    # Método que reescala el pdf
    def scale_pdf_content(input_path, output_path):
        reader = PdfReader(input_path)
        writer = PdfWriter()

        # Crear footer
        footer_pdf = create_footer()
        footer_reader = PdfReader(footer_pdf)

        for i, page in enumerate(reader.pages):
            orig_width = float(page.mediabox.width)
            orig_height = float(page.mediabox.height)

            # Redimensionar solo la altura, no el ancho
            new_height = orig_height * SCALE_FACTOR_Y
            new_width = orig_width  # Mantener el ancho original

            # Centrado horizontal y alineado arriba verticalmente
            translate_x = (A4_WIDTH - new_width) / 2
            translate_y = A4_HEIGHT - new_height  # Alineado al margen superior

            # Aplicar transformación de escala (solo vertical) y traslación
            transformation = (
                Transformation()
                .scale(sx=1, sy=SCALE_FACTOR_X)  # No cambiamos el ancho (sx=1)
                .translate(tx=translate_x, ty=translate_y)  # Solo traslación vertical
            )
            page.add_transformation(transformation)

            # Crear una nueva página A4 en blanco
            new_page = writer.add_blank_page(width=A4_WIDTH, height=A4_HEIGHT)
            new_page.merge_page(page)

            # Añadir el footer (solo lo añades a la página, no hace falta modificar la página original)
            new_page.merge_page(footer_reader.pages[0])

        with open(output_path, "wb") as f:
            writer.write(f)

    if __name__ == "__main__":
        if len(sys.argv) != 3:
            print("Uso: py escalar_pdf.py entrada.pdf salida.pdf")
            sys.exit(1)

        scale_pdf_content(sys.argv[1], sys.argv[2])

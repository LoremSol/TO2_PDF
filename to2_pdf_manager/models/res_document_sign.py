import base64
from odoo import models
from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas
from io import BytesIO


class To2PdfManagerMixin(models.AbstractModel):
    _name = "res.document.sign"
    _description = "PDF Document Signature Manager"
    
    A4_WIDTH = 595.276
    A4_HEIGHT = 841.890
    SCALE_FACTOR_X = 0.95  # 95%
    SCALE_FACTOR_Y = 0.90  # 90%
    FOOTER_HEIGHT = A4_HEIGHT * 0.10  # El 10% de la página
    FOOTER_TEXT = "Firma: Lorenzo Gómez - Empresa TiOdoo"  # Personaliza este texto

    # Método que crea y añade el footer
    def create_footer(self):
        # Crear un archivo PDF en memoria con el footer
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=(self.A4_WIDTH, self.A4_HEIGHT))

        # Establecer el fondo rojo
        c.setFillColorRGB(1, 0, 0)  # Color de fondo rojo
        c.rect(0, 0, self.A4_WIDTH, self.FOOTER_HEIGHT, fill=1)  # Dibujar el rectángulo con fondo rojo

        # Estilo del texto (fuente blanca)
        c.setFillColorRGB(1, 1, 1)  # Color blanco para el texto
        c.setFont("Helvetica-Bold", 10)

        # Dibujar el texto del footer (centrado en el área del footer)
        c.drawString(self.A4_WIDTH / 2 - len(self.FOOTER_TEXT) * 3, self.FOOTER_HEIGHT / 2 - 5, self.FOOTER_TEXT)

        # Dibujar una línea divisoria en el footer (color negro)
        c.setStrokeColorRGB(0, 0, 0)  # Color negro para la línea
        c.setLineWidth(0.5)
        c.line(20, self.FOOTER_HEIGHT, self.A4_WIDTH - 20, self.FOOTER_HEIGHT)  # Línea horizontal en la parte inferior

        c.save()
        packet.seek(0)
        return packet

    # Método que reescala el pdf
    def scale_pdf_content(self, pdf_data):
        """
        Reescala un PDF y añade un pie de página
        
        :param pdf_data: Contenido del PDF en bytes (ya decodificado)
        :return: Contenido del PDF procesado en base64
        """
        # Convertir los bytes del PDF a un objeto BytesIO para que PdfReader pueda trabajar con él
        pdf_stream = BytesIO(pdf_data)
        reader = PdfReader(pdf_stream)
        writer = PdfWriter()

        # Crear footer
        footer_pdf = self.create_footer()
        footer_reader = PdfReader(footer_pdf)

        for i, page in enumerate(reader.pages):
            orig_width = float(page.mediabox.width)
            orig_height = float(page.mediabox.height)

            # Redimensionar solo la altura, no el ancho
            new_height = orig_height * self.SCALE_FACTOR_Y
            new_width = orig_width  # Mantener el ancho original

            # Centrado horizontal y alineado arriba verticalmente
            translate_x = (self.A4_WIDTH - new_width) / 2
            translate_y = self.A4_HEIGHT - new_height  # Alineado al margen superior

            # Aplicar transformación de escala (solo vertical) y traslación
            transformation = (
                Transformation()
                .scale(sx=1, sy=self.SCALE_FACTOR_Y)  # No cambiamos el ancho (sx=1)
                .translate(tx=translate_x, ty=translate_y)  # Solo traslación vertical
            )
            page.add_transformation(transformation)

            # Crear una nueva página A4 en blanco
            new_page = writer.add_blank_page(width=self.A4_WIDTH, height=self.A4_HEIGHT)
            new_page.merge_page(page)

            # Añadir el footer
            new_page.merge_page(footer_reader.pages[0])

        # Escribir el resultado en un BytesIO para devolver los bytes
        output_pdf = BytesIO()
        writer.write(output_pdf)
        output_pdf.seek(0)
        
        # Devolver el contenido en base64
        return base64.b64encode(output_pdf.getvalue())
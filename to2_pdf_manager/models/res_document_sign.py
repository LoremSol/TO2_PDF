import base64, io
from odoo import models
from pypdf import PdfReader, PdfWriter, Transformation
from io import BytesIO
import tempfile, os


class To2PdfManagerMixin(models.AbstractModel):
    _name = "res.document.sign"
    _description = "PDF Document Signature Manager"
    
    A4_WIDTH = 595.276
    A4_HEIGHT = 841.890
    SCALE_FACTOR_X = 0.95  # 95%
    SCALE_FACTOR_Y = 0.90  # 90%

    # Método que crea el footer a partir de las templates
    def create_footer(self, template_id):

        # 1. Intentar renderizar el template como HTML primero para verificar contenido
        try:
            # Construir la referencia al reporte
            report_template = "to2_sale_pdfs.report_" + template_id  # o el formato correcto que uses
            report = self.env.ref(report_template)

            # Importante: Intentar renderizar como HTML primero para verificar contenido
            html_bytes, _ = self.env['ir.actions.report']._render_qweb_html(report.id, [], data={})
            html_str = html_bytes.decode('utf-8')

            # Llamar a wkhtmltopdf manualmente
            pdf_bytes = self.env['ir.actions.report']._run_wkhtmltopdf(
                [html_str],
                specific_paperformat_args={
                    'page-height': '100',  # en mm si quieres footer bajo
                    'page-width': '210',
                    'margin-top': '0',
                    'margin-bottom': '0',
                    'margin-left': '0',
                    'margin-right': '0',
                })


            return BytesIO(pdf_bytes) if pdf_bytes else None

        except Exception as e:
            print(f"ERROR al renderizar el template: {str(e)}")
            return None

    def scale_pdf_content(self, pdf_data, template_id):
        """
        Reescala un PDF y añade un pie de página

        :param pdf_data: Contenido del PDF en bytes (ya decodificado)
        :param template_id: ID del template QWeb para el footer
        :return: Contenido del PDF procesado en base64
        """
        pdf_stream = BytesIO(pdf_data)
        reader = PdfReader(pdf_stream)
        writer = PdfWriter()

        # Crear footer como PDF desde el template
        footer_pdf = self.create_footer(template_id)
        footer_pdf.seek(0)
        footer_reader = PdfReader(footer_pdf)
        footer_page = footer_reader.pages[0]

        for i, page in enumerate(reader.pages):
            orig_width = float(page.mediabox.width)
            orig_height = float(page.mediabox.height)

            # Redimensionar solo la altura, no el ancho
            new_height = orig_height * self.SCALE_FACTOR_Y
            new_width = orig_width

            # Centrado horizontal y alineado arriba verticalmente
            translate_x = (self.A4_WIDTH - new_width) / 2
            translate_y = self.A4_HEIGHT * 0.12  # Deja espacio para el footer

            # Escalar y trasladar el contenido
            transformation = (
                Transformation()
                .scale(sx=1, sy=self.SCALE_FACTOR_Y)
                .translate(tx=translate_x, ty=translate_y)
            )
            page.add_transformation(transformation)

            # Crear una nueva página A4 en blanco
            new_page = writer.add_blank_page(width=self.A4_WIDTH, height=self.A4_HEIGHT)

            # Calculamos la posición del report inicial
            ty = -(self.A4_HEIGHT * 0.3)
            #new_page.merge_translated_page(page, tx=0, ty=ty)
            new_page.merge_page(page)

            #new_page.merge_page(page)

            # Añadir el footer ya renderizado
            footer_width = float(footer_page.mediabox.width)
            footer_height = float(footer_page.mediabox.height)

            # Calculamos la posición del footer
            ty = -(self.A4_HEIGHT * 0.7)
            tx = (self.A4_WIDTH - footer_width) / 2
            #ty = -610
            new_page.merge_translated_page(footer_page, tx=tx, ty=ty)


        output_pdf = BytesIO()
        writer.write(output_pdf)
        output_pdf.seek(0)

        return base64.b64encode(output_pdf.getvalue())

    # Función para obtener los adjuntos de un registro concreto.
    def get_attachments_for_record(self, model_name, record_id):
        if not model_name or not record_id:
            return self.env['ir.attachment']  # Devuelve un recordset vacío

        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', model_name),
            ('res_id', '=', record_id)
        ])
        
        self.merge_pdfs_and_create_attachment(attachments)

    def merge_pdfs_and_create_attachment(self, attachments, filename = None):
        """
        Recibe una lista de registros ir.attachment,
        genera un attachment nuevo con el PDF combinado
        """
        save_filename = f"{filename}.pdf" if filename else "merged_document.pdf"
        pdf_attachments = attachments.filtered(lambda a: a.mimetype == 'application/pdf')

        if not pdf_attachments:
            return False

        writer = PdfWriter()

        # Procesamos cada PDF y lo añadimos al nuevo mergeado
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_output:
            for attachment in pdf_attachments:
                pdf_bytes = base64.b64decode(attachment.datas)
                pdf_stream = io.BytesIO(pdf_bytes)
                reader = PdfReader(pdf_stream)
                for page in reader.pages:
                    writer.add_page(page)

            writer.write(tmp_output)
            tmp_output.close()

            with open(tmp_output.name, "rb") as f:
                merged_pdf = f.read()

            os.unlink(tmp_output.name)

        # Creamos el attachment
        merged_attachment = self.env['ir.attachment'].create({
            'name': save_filename,
            'datas': base64.b64encode(merged_pdf),
            'res_model': pdf_attachments[0].res_model,
            'res_id': pdf_attachments[0].res_id,
            'mimetype': 'application/pdf',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{merged_attachment.id}', #?download=true
            'target': 'self',
        }
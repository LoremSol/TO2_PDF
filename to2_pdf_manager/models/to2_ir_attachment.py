import base64
from odoo import models

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    
    def pdf_resize_and_footed(self):
        # Llama al método de to2_pdf_manager
        manager = self.env['res.document.sign']
        for attachment in self:
            # Aseguramos que attachment.datas es decodificado antes de pasarlo
            pdf_data = base64.b64decode(attachment.datas)
            signed_pdf = manager.scale_pdf_content(pdf_data)
            
            self.env['ir.attachment'].create({
                'name': f"{attachment.name}_signed.pdf",
                'type': 'binary',
                'datas': signed_pdf,  # El contenido base64 del PDF escalado
                'res_model': attachment.res_model,
                'res_id': attachment.res_id,
                'mimetype': 'application/pdf',
                'description': f"{attachment.name}_SIGNED",
            })

        return True
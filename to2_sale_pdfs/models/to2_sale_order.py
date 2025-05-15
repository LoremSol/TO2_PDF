import base64

from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    attachment_ids = fields.One2many(
        'ir.attachment',
        'res_id',
        domain=[('res_model', '=', 'sale.order')],
    )


    def save_report_as_attachment(self):
        self.ensure_one()
        report = self.env.ref('sale.action_report_saleorder')
        pdf_content, _ = report._render_qweb_pdf(report.id)
        attachment_vals = {
            'name': f'Order_{self.name}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
        }
        attachment = self.env['ir.attachment'].create(attachment_vals)
        return attachment
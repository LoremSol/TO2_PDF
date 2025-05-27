import base64

from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    document_ids = fields.One2many(
        'to2.order.document',
        'order_id',
        )
    
    def action_merge_attachments(self):
        for order in self:
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'sale.order'),
                ('res_id', '=', order.id),
                ('mimetype', '=', 'application/pdf'),
            ])
            return self.env['res.document.sign'].get_attachments_for_record(self._name , order.id)
        #self.env['res.document.sign'].merge_pdfs_and_create_attachment(attachments)
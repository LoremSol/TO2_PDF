from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    attachment_id = fields.One2Many(
        'ir.attachment',
        'res_id',
        domain=[('res_model', '=', 'sale.order')],
        string='Documentos adjuntos'
    )
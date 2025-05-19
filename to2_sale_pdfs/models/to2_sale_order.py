import base64

from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    document_ids = fields.One2many(
        'to2.order.document',
        'order_id',
        )
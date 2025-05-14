from odoo import models

class To2IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    _inherit = ['ir.attachment', 'res.document.sign']
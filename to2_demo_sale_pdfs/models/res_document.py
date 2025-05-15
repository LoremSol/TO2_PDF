from odoo import models, fields

class To2OrderDocument(models.Model):

    _name = "to2.order.document"
    _description = "Attachments for an order"

    name = fields.Char(string="Name")

    order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=True,
        ondelete='cascade'
    )

    attachment_id = fields.Many2one(
        'ir.attachment',
        string='Attachment',
        required=True,
        ondelete='cascade'
    )


    def action_convert_attachment(self):

        self.attachment_id.pdf_resize_and_footed()
from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = "stock.move"
    
    @api.model
    def create(self, vals_list):
        
         # Odoo a veces llama con un solo diccionario, no una lista
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
            
        for vals in vals_list:
            if vals.get('sale_line_id'):
                sale_line = self.env['sale.order.line'].browse(vals['sale_line_id'])
                vals['name'] = sale_line.name
        return super().create(vals_list)
    
    
class StockPicking(models.Model):
    _inherit = "stock.picking"
    operator = fields.Many2one(
        'res.partner',
        string='Operated by',
        ondelete='set null'
    )
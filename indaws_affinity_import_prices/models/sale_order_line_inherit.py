from odoo import fields, models, api


class Sale_Order_Line_Inherit(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('discount')
    def _onchange_product_discount(self):
        for rec in self:
            rec.write({'discount': 0.0})

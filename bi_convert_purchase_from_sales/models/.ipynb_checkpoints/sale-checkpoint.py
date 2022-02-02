from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp

    
class sale_order(models.Model):
    _inherit = 'sale.order'
    
    purchase_related_ids = fields.One2many('purchase.order', 'sale_related_id', string="Related purchase orders", readonly=True)
    
    
class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    purchase_price = fields.Float(
        string='Cost', compute="_compute_purchase_price_adapt",
        digits='Product Price', store=True, readonly=False,
        groups="base.group_user")

    @api.depends('product_id', 'company_id', 'currency_id', 'product_uom')
    def _compute_purchase_price_adapt(self):
        for line in self:
            line.purchase_price = 1

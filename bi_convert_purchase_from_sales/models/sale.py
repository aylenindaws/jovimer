from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp


class sale_order(models.Model):
    _inherit = 'sale.order'

    purchase_related_ids = fields.One2many('purchase.order', 'sale_related_id', string="Related purchase orders",
                                           readonly=True)


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    purchase_price = fields.Float(
        string='Cost', compute="_compute_purchase_price_adapt",
        digits='Product Price', store=True, readonly=False,
        groups="base.group_user")
    supplier_id = fields.Many2one('res.partner', string="Supplier")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.product_id.seller_ids:
            seller_ids = self.product_id.seller_ids.mapped('name')
            if seller_ids:
                self.supplier_id = seller_ids[0]

    @api.depends('product_id', 'company_id', 'currency_id', 'product_uom')
    def _compute_purchase_price_adapt(self):
        for line in self:
            if line.product_id.seller_ids:
                line.purchase_price = line.product_id.seller_ids[0].price

# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models, _
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class PurchaseOrderLineWizard(models.TransientModel):
    _name = 'purchase.order.line.wizard'
    _description = "Cuenta de Venta"

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    product_id = fields.Many2one('product.product', string="Product")
    state = fields.Selection(selection=[("draft", "Draft"), ("created", "Created")], default="draft", copy=False)
    display_type = fields.Selection([('line_section', "Section"),('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    product_uom_category_id = fields.Many2one('uom.category', related='product_id.uom_id.category_id')
    product_qty = fields.Float(string='Quantity', required=True)
    date_planned = fields.Datetime(string='Scheduled Date', default=datetime.today())
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')
    order_id = fields.Many2one('sale.order', string='Order Reference', ondelete='cascade', index=True)
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    product_subtotal = fields.Float(string="Sub Total", compute='_compute_total')
    purchase_price = fields.Float(string="Purchase price")
    qty_received_method = fields.Selection([('manual', 'Manual')], string="Received Qty Method")
    qty_received = fields.Float(string="Received Qty", digits=dp.get_precision('Product Unit of Measure'), copy=False)
    qty_invoiced = fields.Float(string="Billed Qty", digits=dp.get_precision('Product Unit of Measure'), store=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes',domain=['|', ('active', '=', False), ('active', '=', True)])
    account_analytic_id = fields.Many2one('account.analytic.account', string='Expediente')
    analytic_tag_ids = fields.Many2many("account.analytic.tag", string="Etiquetas Analiticas", tracking=True)
    name = fields.Char(string="Description")

    @api.model
    def default_get(self, default_fields):
        res = super(PurchaseOrderLineWizard, self).default_get(default_fields)
        return res
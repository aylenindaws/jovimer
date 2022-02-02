# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self.order_line:
            if order.product_id:
                product_qty = 0
                if not order.display_type:
                    product_qty = 0 if order.product_id.product_tmpl_id.stock_available_website == '' else float(order.product_id.product_tmpl_id.stock_available_website.split(' ')[0])
                if product_qty <= 0:
                    if not order.product_id.label_line_ids:
                        label = self.env['product.label.line'].create({
                            'product_tmpl_id': order.product_id.product_tmpl_id.id,
                            'website_id': self.env['website'].search([('name','=','Affinity')], limit=1).id,
                            'label': self.env['product.label'].search([('name','=','Vendido')], limit=1).id,
                        })
                        order.product_id.label_line_ids = [(6, 0, label.ids)]
                    else:
                        for rec in order.product_id.label_line_ids:
                            order.product_id.label_line_ids = [(1, rec.id, {
                                'website_id': self.env['website'].search([('name', '=', 'Affinity')], limit=1).id,
                                'label': self.env['product.label'].search([('name', '=', 'Vendido')], limit=1).id,
                            })]
                item = self.pricelist_id.item_ids.filtered(lambda x:x.applied_on == "1_product" and x.product_tmpl_id==order.product_id.product_tmpl_id)
                if item:
                    item_product_qty = 0 if item.product_tmpl_id.stock_available_website == '' else float(item.product_tmpl_id.stock_available_website.split(' ')[0])
                    if item_product_qty <= 0:
                        item.sudo().unlink()
        return res

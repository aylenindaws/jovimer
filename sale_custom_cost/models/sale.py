# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    cost_real = fields.Float(string='Coste Real', digits='Discount')
    cost_real_total = fields.Float(string='Total Cost Real', compute="sub_total")

    @api.depends('cost_real', 'product_uom_qty')
    def sub_total(self):
        ''' calculate cost real total from cost real amount and qty of product'''
        for rec in self:
            rec.cost_real_total = rec.cost_real * rec.product_uom_qty
            # rec.purchase_price = rec.product_id.seller_ids and rec.product_id.seller_ids[0].price

    def _prepare_invoice_line(self, **optional_values):
        invoice_line = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        invoice_line.update({'cost_real': self.cost_real})
        invoice_line.update({'cost_real_total': self.cost_real_total})
        return invoice_line

    # @api.onchange('product_id', 'price_unit', 'product_uom', 'product_uom_qty', 'tax_id')
    # def _onchange_discount(self):
    #     if not (self.product_id and self.product_uom and
    #             self.order_id.partner_id and self.order_id.pricelist_id and
    #             self.order_id.pricelist_id.discount_policy == 'without_discount' and
    #             self.env.user.has_group('product.group_discount_per_so_line')):
    #         return
    #
    #     self.discount = 0.0
    #
    #     product = self.product_id.with_context(
    #         lang=self.order_id.partner_id.lang,
    #         partner=self.order_id.partner_id,
    #         quantity=self.product_uom_qty,
    #         date=self.order_id.date_order,
    #         pricelist=self.order_id.pricelist_id.id,
    #         uom=self.product_uom.id,
    #         fiscal_position=self.env.context.get('fiscal_position')
    #     )
    #
    #     product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=self.product_uom.id)
    #
    #     price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
    #     new_list_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, self.order_id.pricelist_id.id)
    #     self.price_unit = price
    #     if new_list_price != 0:
    #         if self.order_id.pricelist_id.currency_id != currency:
    #             # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
    #             new_list_price = currency._convert(
    #                 new_list_price, self.order_id.pricelist_id.currency_id,
    #                 self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())
    #         discount = (new_list_price - price) / new_list_price * 100
    #         if (discount > 0 and new_list_price > 0) or (discount < 0 and new_list_price < 0):
    #             self.discount = 0.0
    #             self.price_unit = price

class SaleOrder(models.Model):
    _inherit = "sale.order"

    margin_real = fields.Float(string='Margen Real', compute="total_marign",
                               store=True)
    incoterm_completo = fields.Char(string="Incoterm completo", compute='_get_incoterm')
    margin_real_percentage = fields.Float("Margin (%)", compute='total_marign', store=True)

    @api.depends('incoterm', 'partner_id')
    def _get_incoterm(self):
        for record in self:
            incoterm_completo = ''
            if record.incoterm:
                incoterm_completo = record.incoterm.name
                if record.partner_shipping_id.city:
                    incoterm_completo = str(incoterm_completo) + ' ' + str(record.partner_shipping_id.city)
            record.incoterm_completo = incoterm_completo

    @api.depends('order_line.cost_real_total', 'amount_total')
    def total_marign(self):
        ''' calculate margin total from cost real amount and amount total'''
        margin_real = 0.0
        for order in self:
            for line in order.order_line:
                margin_real += line.cost_real_total
            order.margin_real = order.amount_untaxed - margin_real
            if order.amount_total:
                order.margin_real_percentage = order.margin_real / order.amount_untaxed

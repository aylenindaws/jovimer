# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)



class product_supplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    transport_cost = fields.Float('Transport / kg cost', related="name.transport_cost")
    margin = fields.Float('Margin (%)', related="name.margin")
    not_update_prices = fields.Boolean('No actualizar precios', related="name.not_update_prices")
    cantidad = fields.Float('Stock supplier')
    price_entregado = fields.Float(compute="_value_prices_product", string="Precio entregado")
    price_sale_recommend = fields.Float(compute="_value_prices_product", string="Precio recomendado")


    @api.depends('margin', 'transport_cost', 'price', 'product_id.weight', 'product_tmpl_id.weight')
    def _value_prices_product(self):
        for record in self:
            price_entregado = 0.0
            price_sale_recommend = 0.0
            weight = 0.0
            if record.product_id:
                if record.product_id.weight > 0:
                    weight = record.product_id.weight
            if weight <= 0.0:
                if record.product_tmpl_id:
                    if record.product_tmpl_id.weight > 0:
                        weight = record.product_tmpl_id.weight

            record.price_entregado = record.price + (record.transport_cost * weight)
            record.price_sale_recommend = 0.0
            if record.margin < 100:
                record.price_sale_recommend = record.price_entregado / (1 - record.margin / 100)

    inc_cost = fields.Float(digits=(6, 2), string='Cost increase (%)', compute='_calculate_cost_increase')
    product_code = fields.Char(string='Product code', compute='_calculate_cost_increase')
    min_supplier_id = fields.Many2one('res.partner', string='Min cost supplier', compute='_calculate_cost_increase', readonly=True)
    min_cost = fields.Float(digits=(6, 2), string='Min cost', compute='_calculate_cost_increase')
    average_cost = fields.Float(digits=(8, 4), string="Average cost", compute='_calculate_cost_increase', readonly=True)
    median_cost = fields.Float(digits=(8, 4), string="Median cost", compute='_calculate_cost_increase', readonly=True)
    variation_median_cost = fields.Float(digits=(8, 4), string="Variation Median cost (%)", compute='_calculate_cost_increase', readonly=True)
    date_min_cost = fields.Date(string="Fecha precio", compute='_calculate_cost_increase', readonly=True)

    @api.depends('product_tmpl_id')
    def _calculate_cost_increase(self):
        for record in self:
            price = 0.0
            inc = 0.0

            if record.product_tmpl_id:
                record.product_code = record.product_tmpl_id.default_code
                record.min_cost = record.product_tmpl_id.min_cost
                record.date_min_cost = record.product_tmpl_id.date_min_cost
                record.median_cost = record.product_tmpl_id.median_cost
                record.average_cost = record.product_tmpl_id.average_cost
                record.min_supplier_id = None
                if record.product_tmpl_id.min_supplier_id:
                    record.min_supplier_id = record.product_tmpl_id.min_supplier_id.id

                # calculo incremento
                dif = record.price_entregado - record.median_cost
                variation_median_cost = 0.0
                if record.median_cost > 0:
                    variation_median_cost = (dif / record.median_cost) * 100
                record.variation_median_cost = variation_median_cost

            price = record.price_entregado
            if record.product_tmpl_id.min_cost > 0.0:
                if price > record.product_tmpl_id.min_cost:
                    inc = ((price - record.product_tmpl_id.min_cost) / record.product_tmpl_id.min_cost) * 100
            record.inc_cost = inc
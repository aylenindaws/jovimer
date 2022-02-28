# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import odoo.addons.decimal_precision as dp
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bulge = fields.Float(string='Bultos', store=True, copy=True)
    caliber = fields.Many2one('jovimer.calibre', string="Calibre", store=True, copy=True, ondelete='set null')
    category = fields.Many2one('jovimer.categoria', string="Categoria", store=True, copy=True, ondelete='set null')
    partner_code = fields.Char(string='Codigo Cliente')
    confection = fields.Many2one('jovimer.confeccion', string='Confección', store=True, copy=True, ondelete='set null')
    display_name = fields.Char(string='Display Name', readonly=True)
    container = fields.Many2one('jovimer.envase', string='Envase', store=True, copy=True, ondelete='set null')
    invoice_id = fields.Many2one('account.move', string='ALB/FACT', store=True, copy=True, ondelete='set null')
    invoice_line_id = fields.Many2one('account.move.line', string='Lin ALB/FACT', store=True, copy=True, ondelete='set null')
    kg_net_bulge = fields.Float(string='KG/NET Confección', store=True, copy=True)
    brand = fields.Many2one('jovimer.marca', string='Marca', store=True, copy=True, ondelete='set null')
    name = fields.Char(string='Nombre', store=True, copy=True, required=False)
    not_active = fields.Boolean('NO Activo', store=True, copy=True, tracking=True)
    not_calculate_lumps = fields.Boolean('No Calcula Bultos', store=True, copy=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', store=True, copy=True, ondelete='set null')
    label_templates = fields.Many2one('jovimer.etiquetas.plantilla', string='P. Etiquetas', store=True, copy=True, ondelete='set null')
    week_price = fields.Integer(string='Semana', store=True, copy=True, ondelete='set null', help='Semana a la que se aplica el precio atendiendo a la fecha de llegada del Pedido')
    product_id = fields.Many2one('product.product', string='Producto', store=True, copy=True, ondelete='set null')
    cost = fields.Float(string='Coste', store=True, copy=True)
    pvp_type = fields.Many2one('uom.uom', string='PVP/Tipo', store=True, copy=True, ondelete='set null', domain=[('invisible','=','NO')])
    transport = fields.Float(string='Transporte', store=True, copy=True)
    sale = fields.Float(string='Venta', store=True, copy=True)
    sale_id = fields.Many2one('sale.order', string='Pedido', store=True, copy=True, ondelete='set null')
    sale_line_id = fields.Many2one('sale.order.line', string='Lin Pedido', store=True, copy=True, ondelete='set null')
    week = fields.Char(string='Semana', store=True, copy=True)
    uom_type = fields.Many2one('uom.uom', string='Tipo Medida', store=True, copy=True, ondelete='set null', domain=[('invisible','=','NO')])
    palet_type = fields.Many2one('jovimer.palet', string='Tipo Palet', store=True, copy=True, ondelete='set null', domain=[('invisible','=','NO')])
    uom_invoice = fields.Many2one('uom.uom', string='Ud Albaran/Factura', store=True, copy=True, ondelete='set null', domain=[('invisibleudvta','=','SI')])
    variety = fields.Many2one('jovimer.variedad', string='Variedad', store=True, copy=True, ondelete='set null')

    @api.onchange('confection.bulge_euro_palet')
    def _compute_bulge_euro_palet(self):
        for item in self:
            item.bulge = item.confection.bulge_euro_palet
        return {}

    @api.onchange('confection.bulge_grand_palet')
    def _compute_bulge_grand_palet(self):
        for item in self:
            item.bulge = item.confection.bulge_grand_palet
        return {}

    @api.onchange('confection.kg_net_bulge')
    def _compute_kg_net_bulge(self):
        for item in self:
            item.kg_net_bulge = item.confection.kg_net_bulge
        return {}

    def calcula_bultos(self):
        for item in self:
            if item.not_calculate_lumps == True:
                return {}
            else:
                item.bulge = item.confection.bulge_euro_palet
                return {}
            
class ProductTemplate(models.Model):
    _inherit = 'product.supplierinfo'

    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)
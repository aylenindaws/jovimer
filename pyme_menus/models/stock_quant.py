# -*- coding: utf-8 -*-

from odoo import models, fields, api

class preciospedidos(models.Model):
    _inherit = 'stock.quant'

    description = fields.Char(related="location_id.description",string="Descripción")
    tipo_movimiento = fields.Selection([('E', 'E'), ('S', 'S')], related="location_id.tipo_movimiento", string="Tipo movimiento", readonly="1")
    visible = fields.Boolean(related="location_id.visible", string="Visible", readonly="1")
    
    

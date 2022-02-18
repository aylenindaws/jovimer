# -*- coding: utf-8 -*-

from odoo import models, fields, api

class preciospedidos(models.Model):
    _inherit = 'stock.move.line'

    description = fields.Char(related="location_dest_id.description",string="Descripción")
    tipo_movimiento = fields.Selection([('E', 'E'), ('S', 'S')], related="location_id.tipo_movimiento", string="Tipo movimiento", readonly="1")
    

# -*- coding: utf-8 -*-

from odoo import models, fields, api

class preciospedidos(models.Model):
    _inherit = 'stock.location'

    description = fields.Char(string="Descripción")
    tipo_movimiento = fields.Selection([('E', 'E'), ('S', 'S')], string='Tipo movimiento')
    visible = fields.Boolean('Visible')
    
    
    

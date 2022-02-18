# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError

class DiariosContables(models.Model):
    # Herencia de la tabla de ventas
    _inherit = 'account.journal'
    
    # Añadir el estado Pedido a ventas
    habitual = fields.Boolean(string='Habitual')
    description = fields.Text(string='Descripcion', translate=True)
   

   
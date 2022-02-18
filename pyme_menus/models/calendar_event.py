# -*- coding: utf-8 -*-

from odoo import models, fields, api

class eventoCalendario(models.Model):
    # Herencia de la tabla de ventas
    _inherit = 'calendar.event'

    # Añadir el estado Pedido a ventas
    partner = fields.Many2one('res.partner', string='Entidad Asociada', copy=True, auto_join=True)
    project_count = fields.Integer(string='Project Count')
    code = fields.Integer(string='Code')
    tag_ids = fields.Integer(string='Tags')
    company_id = fields.Integer(string='cp')
    currency_id = fields.Integer(string='cp')
    state = fields.Integer(string='cp')
    etiquetas_calendario = fields.Many2many('etiquetas_relacion', 'etiquetas_calendario', 'calendario_name', string='Tipo de Etiquetas')
	


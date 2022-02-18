# -*- coding: utf-8 -*-

from odoo import models, fields, api
	
class Message_Customexp(models.Model):
    _inherit = "mail.message"
    
    expediente = fields.Many2one('jovimer_expedientes', string='Expediente')
    expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya', store=True)
    expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name', store=True)
    expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie', store=True) 
# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    dossier_id = fields.Many2one('jovimer.expedientes', string='expediente', store=True, copy=True, ondelete='set null')
    country_id = fields.Many2one(string="Pais Destino", comodel_name='res.country', required=True, default=lambda x: x.env.company.country_id.id, help="Country for which this report is available.")
    close_sale = fields.Boolean(string='Pedido Cerrado')
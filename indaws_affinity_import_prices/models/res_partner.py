# -*- coding: utf-8 -*-

from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = 'res.partner'

    transport_cost = fields.Float('Transport / kg cost')
    margin = fields.Float('Margin (%)')
    not_update_prices = fields.Boolean('No actualizar precios')
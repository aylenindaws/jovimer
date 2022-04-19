# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    otras_facturas = fields.Boolean('Otras facturas')
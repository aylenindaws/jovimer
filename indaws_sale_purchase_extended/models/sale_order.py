# -*- coding: utf-8 -*-
import os.path

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import subprocess
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    dossier_id = fields.Many2one('jovimer.expedientes', string='expediente', store=True, copy=True, ondelete='set null')
    palets = fields.Float(string='C. Compra', store=True, copy=True)
    paletsv = fields.Float(string='C. Venta', store=True, copy=True)
    platform = fields.Char(string='Plataforma')
    edi_file = fields.Many2one('ir.attachment', string="Fichero EDI", store=True, copy=True, ondelete='set null', domain="[('mimetype','=','text/plain')]")
    date_end = fields.Date(string='Fecha de Salida')
    date_start = fields.Date(string='Fecha de Llegada')
    time_start = fields.Char(string='Hora de Llegada')
    conforms_lot = fields.Many2one('jovimer.conflote', string="Conforma LOTE", store=True, copy=True, ondelete='set null')
    lote_char = fields.Char(string='Lote', store=True, copy=True)
    close_sale = fields.Boolean(string='Pedido Cerrado')

    def update_edi_file(self, default=None):
        id = str(self.id)
        path = 'static/sh/importaedi_pedido.sh'
        dir = os.path.dirname(__file__)
        file_dir = dir.replace('models','')
        args = [file_dir+path, id, "&"]
        subprocess.call(args)
        return {}
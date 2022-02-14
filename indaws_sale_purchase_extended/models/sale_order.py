# -*- coding: utf-8 -*-
import base64
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
        for item in self:
            count = 0
            aux_txt = base64.b64decode(item.edi_file.datas).decode('utf-8', 'ignore').split('\n')
            item.order_line.unlink()
            for linea in aux_txt:
                count+=1
                if count==1:
                    if '96AORDERSP' in linea:
                        _logger.info('Fichero EDI Valido para su procesamiento')
                    else:
                        _logger.info('Fichero EDI Valido para su procesamiento')
                        id_edi_jovimer = linea[4:17]
                        break
                elif count==2:
                    id_edi_cliente = linea[27:40]
                    fecha_pedido = linea[18:26]
                    fecha_llegada = linea[112:120]
                else:
                    product_id = self.env['product.template'].search([("partner_code", "=", linea[35:42])])
                    quantity = linea[65:71]
                    und = linea[72:75]
                    product_description = linea[75:125]
                    product_conv = linea[555]
                    if 'CT' in und:
                        id_und = 24
                    elif 'PCE' in und:
                        id_und = 1
                    elif 'KGM' in und:
                        id_und = 27
                    else:
                        id_und = 1
                    item.order_line.create(
                        {
                            "order_id": item.id,
                            "product_id": product_id.id,
                            "product_uom_qty":quantity,
                            "name":product_description,
                            "price_unit": product_id.lst_price,
                            'currency_id': 1,
                        }
                    )
        return
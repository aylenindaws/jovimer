# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    fechasalida = fields.Date(string='Fecha de Pedido / Salida')
    fechallegada = fields.Date(string='Fecha de Llegada')
    horallegada = fields.Char(string='Hora de Llegada', help='Permite caracteres Alfanuméricos')
    campanya = fields.Char(string='Serie / Campaña', help='Número Expediente')
    expediente = fields.Many2one('jovimer.expedientes', string='Expediente')
    pedidocerrado = fields.Boolean(string='Pedido Cerrado', related='expediente.order_close')
    expediente_serie = fields.Selection('jovimer.expedientes', related='expediente.campanya')
    expediente_serien = fields.Many2one('jovimer.expedientes.series', related='expediente.serie')
    expediente_num = fields.Integer('jovimer.expedientes', related='expediente.name')
    mododecobro = fields.Many2one('payment.acquirer', string='Modo de Cobros')
    conformalote = fields.Many2one('jovimer.conflote', string='Conforma LOTE')
    obspedido = fields.Text(string='Observaciones PEdido')
    description = fields.Char(string='Desc.')
    estadodesc = fields.Char(string='Estado Desc.')
    att = fields.Char(string='Attención de:')
    consignatario = fields.Char(string='Consignatario/Plataforma')
    destino = fields.Boolean(string='Para Almacén')
    destinodonde = fields.Char(string='Donde Está')
    saleorder = fields.Many2one('sale.order', string='Venta Relacionada')
    partnersale = fields.Many2one('res.partner', related='saleorder.partner_id', store=True)
    obspartnersale = fields.Text(string='Observaciones Cliente')
    viajegenerado = fields.Boolean(string='Viaje')
    totaleuro = fields.Float(string='Palet')
    totalgr = fields.Float(string='GR Palet')
    estadocrear = fields.Boolean(string='Finalizada Creacion')
    paisdestino = fields.Many2one('res.country', string='Pais Destino')
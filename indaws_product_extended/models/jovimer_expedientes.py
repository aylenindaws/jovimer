# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)

class JovimerExpedientes(models.Model):
    _name = 'jovimer.expedientes'
    _description = 'Expedientes'
    _order = "name asc"

    name = fields.Integer(string='Número', help='Número Expediente')
    #partner_id = fields.Many2one('res.partner', string='Cliente', related='order_id.partner_id')
    #download_partner_id = fields.Many2one('res.partner', string='Direccion Descarga', related='order_id.partner_shipping_id')
    #date_end = fields.Date(string='Fecha de Salida', related='order_id.fechasalida')
    #date_start = fields.Date(string='Fecha de Llegada', related='order_id.fechallegada')
    time_arrive = fields.Char(string='Hora de Llegada', help='Permite caracteres Alfanuméricos')
    registration = fields.Char(string='Matrícula', help='Permite varias')
    transport_int_partner_id = fields.Many2one('res.partner', string='Transporte Internacional')
    transport_nat_partner_id = fields.Many2one('res.partner', string='Transporte Nacional')
    international_transport_price = fields.Float(string='Precio Transporte Internacional')
    national_transport_price = fields.Float(string='Precio Transporte Nacional')
    payment = fields.Text(string='Abono')
    order = fields.Boolean(string='Pedidos')
    logistic = fields.Boolean(string='Logística')
    invoice = fields.Boolean(string='Facturación')
    liquidation = fields.Boolean(string='Liquidaciones')
    sale_account = fields.Boolean(string='Cuenta de Ventas')
    output = fields.Boolean(string='Salidas')
    no_bio = fields.Boolean(string='NO BIO')
    observations = fields.Text(string='Observaciones')
    num_prev = fields.Integer(string='Número Anterior', help='Número Expediente')
    series_id = fields.Many2one('jovimer.expedientes.series', string='Serie')
    series_name = fields.Char('Serie Char')
    #dossier_name = fields.Char('Expediente', compute='_compute_fields_combination')
    campaign = fields.Selection([('J22', 'J22'),('J20', 'J20'),('PR20', 'PR20'),('CO20', 'CO20'),('J21', 'J21'),('PR21', 'PR21'),('CO21', 'CO21')], string='Campaña', default='J22')
    import_true = fields.Boolean(string='Importado')
    #order_id = fields.One2many('sale.order', 'dossier_id', string='Pedidos venta')
    #purchase_id = fields.One2many('purchase.order', 'dossier_id', string='Pedidos venta')
    #invoice_id = fields.One2many('account.move', 'dossier_id', string='Facturas Venta')
    #invoice_line_id = fields.One2many('account.move.line', 'dossier_id', string='Facturas Compra', domain=[('typefact', '=', 'in_invoice')])
    #travel_id = fields.One2many('jovimer.viajes', 'dossier_id', string='Viajes')
    #ctn = fields.One2many('jovimer.ctn', 'dossier_id', string='Control Trans Nacional')
    #cti = fields.One2many('jovimer.cti', 'dossier_id', string='Control Trans Internacional')
    #claims = fields.One2many('jovimer.reclamaciones', 'dossier_id', string='Etiquetas')
    #label_id = fields.One2many('jovimer.etiquetas', 'dossier_id', string='Etiquetas')
    #order_close = fields.Boolean(string='Pedido Cerrado', related='order_id.pedidocerrado')

    #@api.depends('serie', 'name')
    #def _compute_fields_combination(self):
    #    for test in self:
    #        test.dossier_name = test.serie.name + '-' + str(test.name)

    @api.model
    def create(self, vals):
        serie = self.campanya
        numero = self.name
        vals['cliente'] = 3495
        result = super(JovimerExpedientes, self).create(vals)
        return result
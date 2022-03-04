# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)


class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    expediente = fields.Many2one('account.analytic.account', string='Expediente')
    tipoviaje = fields.Selection([
        ('NACIONAL', 'NACIONAL'), ('INTERNACIONAL', 'INTERNACIONAL'), ('INTERNACIONALD', 'INTERNACIONAL DIRECTO')
    ], string='Tipo de Viaje')
    fechaformalizado = fields.Date(string='Fecha Formalizado')
    referencia = fields.Integer(string='Ref Interna')
    name = fields.Char(string='Número de Orden')
    matricula = fields.Char(string='Matricula')
    referenciatxt = fields.Char(string='Referencia')
    contactochofer = fields.Char(string='Contacto Chófer')
    temperatura = fields.Char(string='Temperatura')
    tempfijoauto = fields.Char(string='Fijo / Auto')
    tempdoblesimple = fields.Char(string='Doble/Simpel')
    importe = fields.Float('Importe')
    transportista = fields.Many2one('res.partner', string='Transportista', domain="[('trasnportista','=', True)]")
    paleteur = fields.Float(string='Eur')
    paletgr = fields.Float(string='Gr')
    apilables = fields.Char(string='Apilables')
    combina = fields.Boolean(string='Combina')
    #ctn = fields.Many2many('jovimer_ctn', string='Control Transporte Nacional')
    #cti = fields.Many2many('jovimer_cti', string='Control Transporte Internacional')
    #ctno2m = fields.One2many('jovimer_ctn', 'orcarga', string='Control Transporte Nacional')
    #ctio2m = fields.One2many('jovimer_cti', 'viaje', string='Control Transporte Internacional')
    #ordenrecoalma = fields.One2many('jovimer_ordenrecalm', 'viaje', string='Orden Recogida Almacén')
    #cmr = fields.Many2many('jovimer_cmr', string='CMR')
    #ordencarga = fields.One2many('jovimer_ordencarga', 'viaje', string='Ordenes de Carga')
    observaciones = fields.Text(string='Observaciones')
    destinointerior = fields.Selection([
        ('Plataforma XERESA', 'Plataforma XERESA'), ('Perpignan', 'Perpignan'), ('Barcelona', 'Barcelona')
    ], string='Destino Interior')
    almacenorigen = fields.Many2one('res.partner', string='Almacén Origen', domain="[('name','=ilike', 'JOVIMER')]")
    destinoor = fields.Many2one('res.partner', string='Destino Cliente', domain="[('customer','=', True)]")
    fechallegadanacional = fields.Date(string='Fecha LLegada Nacional')
    fechallegadainternacional = fields.Date(string='Fecha Llegada Internacional')
    #orcargacab = fields.One2many('jovimer_ordencargacab', 'viajerel', string='Orden Carga Cabecera')
    #orcargacabprint = fields.One2many('jovimer_ordencargacabprint', 'viajerel', string='Impresion Orden de Carga')
    productos = fields.Text(string='Productos')
    preparafactura = fields.Boolean(string='Prep Factura')
    facturado = fields.Boolean(string='Facturado')
    facturarel = fields.Many2one(string='account.invoice')
    #resumencabe = fields.One2many('jovimer_viajeresumen', 'viaje', string='Resumen Cliente')
    #resumenlin = fields.One2many('jovimer_viajeresumenlin', 'viaje', string='Resumen Lineas')
    #grupajes = fields.One2many('jovimer_grupajes', 'name', string='Grupajes')
    proveedores = fields.Text(string='Proveedores')
    #linealbcompra = fields.Many2many('account.move.line', string='Lineas de Albarán')#,domain="[('diariofactura','=', 9)]")
    #almacenxeresa = fields.Many2many('account.move.line', string='Almacen Xeresa')
    nunlinlinealbcompra = fields.Char(string='Num. Lineas')
    nunlinalmacenxeresa = fields.Char(string='Num. Lineas')
    state = fields.Selection([
        ('draft', 'BORRADOR'),
        ('online', 'EN CURSO'),
        ('cancel', 'ENCANCELADOCURSO'),
        ('done', 'CERRADO')
    ], string='Estado', default='draft')

    def cambiadestinos(self):
        destinoor = self.destinoor
        lineas = ""
        for lineasalbaranes in self.linealbcompra:
            lineas += str(lineasalbaranes.id) + ","
            lineasalbaranes.plataformadestino = destinoor
        return {}
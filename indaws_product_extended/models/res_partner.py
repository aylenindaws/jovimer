# -*- coding: utf-8 -*-
import base64
import os.path

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, time, timedelta
import subprocess
import logging
import datetime

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    trasnportista = fields.Boolean(string='Transportista')
    obspedidos = fields.Text(string='Observaciones Pedidos')
    obsfactura = fields.Text(string='Observaciones Facturas/Albaranes')
    noimprimepal = fields.Boolean(string='NO Imprime Tipo Palet')
    zonatrasinterior = fields.Many2one('res.country.state', string='Zona Transporte Interior')
    gln = fields.Char(string='GLN')
    rgseaa = fields.Char(string='RGSEAA')
    fechabaja = fields.Date(string='Fecha Baja')
    conformalote = fields.Many2one('jovimer.conflote', string='Conforma LOTE', store=True)
    comisionvta = fields.Float(string='Comision %')
    plantillaetiquetas = fields.Char(string='Plantilla Etiquetas')
    fechaalta = fields.Date(string='Fecha Alta')
    asegurado = fields.Boolean(string='Asegurado')
    aseguradocompania = fields.Char(string='Compañia Asegurado')
    acreedor = fields.Boolean(string='Acreedor')
    mododecobro = fields.Many2one('payment.acquirer', string='Modo de Cobros')
    mododepago = fields.Many2one('payment.acquirer', string='Modo de Pago')
    unidaddeventa = fields.Many2one('uom.uom', string='Unidad de Venta', domain=[('invisible', '=', 'NO')])
    unidaddepedido = fields.Many2one('uom.uom', string='Unidad de Pedido', domain=[('invisible', '=', 'NO')])
    responsablecompras = fields.Char(string='Responsable Compras')
    pvpeur = fields.Float(string='PVP / Palet EURO')
    pvpgr = fields.Float(string='PVP / Palet GR')
    limitepalet = fields.Float(string='Limite por Completo')
    viajecompleto = fields.Float(string='Precio VIaje Completo')
    nomfiscal = fields.Char(string='Nombre Fiscal Contable')
    cta = fields.Char(string='Cuenta Contable Cliente')
    ctap = fields.Char(string='Cuenta Contable Proveedor')
    dtoclienter = fields.Float(string='Descuento Cliente')
    partnerfiscal = fields.Many2one('res.partner', string='Partner Fiscal')
    zonatransporte = fields.Many2one('res.country.state', string='Zona Transporte')
    emailctaventa = fields.Char(string='Email Cuenta de Venta')
    quierebr = fields.Boolean(string='Con KG Brutos')
    paisdestinointrastat = fields.Many2one('res.country', string='Pais Destino INTRASTAT')
    nobio = fields.Boolean(string='Entidad NO BIO')
    edinumber = fields.Char(string='Número EDI')
    prefijoalbaranes = fields.Char(string='Prefijo Albaranes', help="Prefijo Albaranes de Proveedor")
    prefijofacturas = fields.Char(string='Prefijo Facturas', help="Prefijo Facturas de Proveedor")
    noactivo = fields.Boolean(string='No Seleccionable VENTAS/COMPRAS')
    seriefacturasvta = fields.Many2one('account.journal', string='Serie Facturas para Ventas')
    seriefacturascomp = fields.Many2one('account.journal', string='Serie Facturas para Compras')
    ubicacionalmacen = fields.Boolean(string='Ubicación de Almacén')
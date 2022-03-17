# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import json
import os
import sys

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Expediente')

    def action_confirm(self):
        for item in self:
            for record in item.move_ids_without_package:
                record.supplier_id = record.sale_line_id.supplier_id
                record.client_id = record.sale_line_id.partner_id
                record.variedad = record.sale_line_id.variedad
                record.confeccion = record.sale_line_id.confeccion
                record.envase = record.sale_line_id.envase
                record.cantidadpedido = record.sale_line_id.cantidadpedido
                record.tipouom = record.sale_line_id.tipouom
                record.costetrans = record.sale_line_id.costetrans
                record.analytic_account_id = record.sale_line_id.order_id.analytic_account_id
        res = super(StockPicking, self).action_confirm()

    @api.model
    def create(self, vals):
        if not 'analytic_account_id' in vals:
            sale = self.env['sale.order'].search([('name', 'ilike', vals['origin'])])
            if sale:
                vals['analytic_account_id'] = sale.analytic_account_id.id
            else:
                purchase = self.env['purchase.order'].search([('name', 'ilike', vals['origin'])])
                if purchase:
                    vals['analytic_account_id'] = purchase.account_analytic_id.id
                else:
                    account_analytic = self.env['account.analytic.account'].search([('name', 'ilike', vals['origin'])])
                    if account_analytic:
                        vals['analytic_account_id'] = account_analytic.id
        result = super(StockPicking, self).create(vals)
        return result

    def write(self, vals):
        result = super(StockPicking, self).write(vals)
        if not self.analytic_account_id and not 'analytic_account_id' in vals:
            sale = self.env['sale.order'].search([('name', 'ilike', self.origin)])
            if sale:
                vals['analytic_account_id'] = sale.analytic_account_id.id
            else:
                purchase = self.env['purchase.order'].search([('name', 'ilike', self.origin)])
                if purchase:
                    vals['analytic_account_id'] = purchase.account_analytic_id.id
                else:
                    account_analytic = self.env['account.analytic.account'].search([('name', 'ilike', self.origin)])
                    if account_analytic:
                        vals['analytic_account_id'] = account_analytic.id
            self.write(vals)
        return result


class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    expediente = fields.Many2one('account.analytic.account', string='Expediente')
    tipoviaje = fields.Selection([
        ('NACIONAL', 'NACIONAL'), ('INTERNACIONAL', 'INTERNACIONAL')
    ], string='Tipo de Viaje')
    fechaformalizado = fields.Date(string='Fecha Formalizado')
    referencia = fields.Integer(string='Ref Interna')
    name = fields.Char(string='Número de Orden')
    matricula = fields.Char(string='Matricula')
    referenciatxt = fields.Char(string='Referencia')
    contactochofer = fields.Char(string='Contacto Chófer')
    temperatura = fields.Integer(string='Temperatura')
    tempfijoauto = fields.Char(string='Fijo / Auto')
    tempdoblesimple = fields.Char(string='Doble/Simpel')
    importe = fields.Float('Importe')
    transportista = fields.Many2one('res.partner', string='Transportista')
    paleteur = fields.Float(string='Eur')
    paletgr = fields.Float(string='Gr')
    apilables = fields.Char(string='Apilables')
    combina = fields.Boolean(string='Combina')
    # ctn = fields.Many2many('jovimer_ctn', string='Control Transporte Nacional')
    # cti = fields.Many2many('jovimer_cti', string='Control Transporte Internacional')
    # ctno2m = fields.One2many('jovimer_ctn', 'orcarga', string='Control Transporte Nacional')
    # ctio2m = fields.One2many('jovimer_cti', 'viaje', string='Control Transporte Internacional')
    # ordenrecoalma = fields.One2many('jovimer_ordenrecalm', 'viaje', string='Orden Recogida Almacén')
    # cmr = fields.Many2many('jovimer_cmr', string='CMR')
    # ordencarga = fields.One2many('jovimer_ordencarga', 'viaje', string='Ordenes de Carga')
    observaciones = fields.Text(string='Observaciones')
    destinointerior = fields.Selection([
        ('Plataforma XERESA', 'Plataforma XERESA'), ('Perpignan', 'Perpignan'), ('Barcelona', 'Barcelona')
    ], string='Destino Interior')
    almacenorigen = fields.Many2one('res.partner', string='Almacén Origen', domain="[('name','=ilike', 'JOVIMER')]")
    destinoor = fields.Many2one('res.partner', string='Destino Cliente')
    fechallegadanacional = fields.Date(string='Fecha LLegada Nacional')
    fechallegadainternacional = fields.Date(string='Fecha Llegada Internacional')
    # orcargacab = fields.One2many('jovimer_ordencargacab', 'viajerel', string='Orden Carga Cabecera')
    # orcargacabprint = fields.One2many('jovimer_ordencargacabprint', 'viajerel', string='Impresion Orden de Carga')
    productos = fields.Text(string='Productos')
    preparafactura = fields.Boolean(string='Prep Factura')
    facturado = fields.Boolean(string='Facturado')
    facturarel = fields.Many2one(string='account.invoice')
    # resumencabe = fields.One2many('jovimer_viajeresumen', 'viaje', string='Resumen Cliente')
    # resumenlin = fields.One2many('jovimer_viajeresumenlin', 'viaje', string='Resumen Lineas')
    # grupajes = fields.One2many('jovimer_grupajes', 'name', string='Grupajes')
    proveedores = fields.Text(string='Proveedores')
    # linealbcompra = fields.Many2many('account.move.line', string='Lineas de Albarán')#,domain="[('diariofactura','=', 9)]")
    # almacenxeresa = fields.Many2many('account.move.line', string='Almacen Xeresa')
    nunlinlinealbcompra = fields.Char(string='Num. Lineas')
    nunlinalmacenxeresa = fields.Char(string='Num. Lineas')
    exp_picking_ids = fields.One2many('stock.picking', 'batch_id', string='Pickings',
                                      compute="_compute_exp_picking_ids")

    @api.depends("picking_ids", "expediente")
    def _compute_exp_picking_ids(self):
        for item in self:
            if item.expediente:
                item.exp_picking_ids = self.env['stock.picking'].search(
                    ['|', ('analytic_account_id', '=', item.expediente.id), ('analytic_account_id', '=', False)])
            else:
                item.exp_picking_ids = self.env['stock.picking'].search([('id', '!=', 0)])

    def cambiadestinos(self):
        destinoor = self.destinoor
        lineas = ""
        for lineasalbaranes in self.linealbcompra:
            lineas += str(lineasalbaranes.id) + ","
            lineasalbaranes.plataformadestino = destinoor
        return {}

    def _sanity_check(self):
        _logger.error('Pass')
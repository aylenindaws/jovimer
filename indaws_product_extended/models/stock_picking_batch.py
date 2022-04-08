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
    paleteur = fields.Float(string='Eur', compute="_compute_palet_type")
    paletgr = fields.Float(string='Gr', compute="_compute_palet_type")
    totalbultos = fields.Float(string='Total Bultos', compute="_compute_palet_type")

    def _compute_palet_type(self):
        for item in self:
            item.paleteur = 0
            item.paletgr = 0
            item.totalbultos = 0
            for record in item.move_ids_without_package:
                item.write({'paleteur': record.paleteur})
                item.write({'paletgr': record.paletgr})
                item.write({'totalbultos': record.totalbultos})

    def action_confirm(self):
        for item in self:
            for record in item.move_ids_without_package:
                record.supplier_id = record.sale_line_id.supplier_id
                record.client_id = record.sale_line_id.partner_id
                record.variedad = record.sale_line_id.variedad
                record.confeccion = record.sale_line_id.confeccion
                record.envase = record.sale_line_id.envase
                record.cantidadpedido = record.sale_line_id.cantidadpedido
                record.product_uom_qty = record.sale_line_id.product_uom_qty
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
        for item in self:
            if not item.analytic_account_id and not 'analytic_account_id' in vals:
                sale = self.env['sale.order'].search([('name', 'ilike', item.origin)])
                if sale:
                    vals['analytic_account_id'] = sale.analytic_account_id.id
                else:
                    purchase = self.env['purchase.order'].search([('name', 'ilike', item.origin)])
                    if purchase:
                        vals['analytic_account_id'] = purchase.account_analytic_id.id
                    else:
                        account_analytic = self.env['account.analytic.account'].search([('name', 'ilike', item.origin)])
                        if account_analytic:
                            vals['analytic_account_id'] = account_analytic.id
                item.write(vals)
        return result


class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    expediente_ids = fields.Many2many('account.analytic.account',
                                      relation="stock_picking_account_analytic_rel",
                                      column1="stock_picking_batch_id",
                                      column2="account_analytic_id",
                                      string='Expediente')
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
    paleteur = fields.Float(string='Eur', compute="_compute_exp_picking_ids", default=0)
    paletgr = fields.Float(string='Gr', compute="_compute_exp_picking_ids", default=0)
    totalbultos = fields.Float(string='Total Bultos', compute="_compute_exp_picking_ids", default=0)
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
    txt01 = fields.Text(string='1- Remitente')
    txt02 = fields.Text(string='2- Consignatario')
    txt03 = fields.Text(string='3- Lugar de Entrega')
    txt04 = fields.Text(string='4- Lugar y Fecha Carga')
    txt05 = fields.Text(string='5- Documentos Anexos')
    txt06 = fields.Text(string='6- Marca')
    txt07 = fields.Text(string='7- Bultos')
    txt08 = fields.Text(string='8- Envase')
    txt09 = fields.Text(string='9- Producto')
    txt10 = fields.Text(string='10- Num Estad.')
    txt11 = fields.Text(string='11- Peso')
    txt12 = fields.Text(string='12- Palets')
    txt13 = fields.Text(string='13- Intrucciones Remitente')
    txt131 = fields.Text(string='txt131')
    txt132 = fields.Text(string='txt132')
    txt133 = fields.Text(string='txt133')
    txt14 = fields.Text(string='14- Forma de Pago')
    txt15 = fields.Text(string='15- Reembolso')
    txt16 = fields.Text(string='16- porteador')
    txt17 = fields.Text(string='17- Porteadores Sucesivos')
    txt18 = fields.Text(string='18- Reservas')
    txt19 = fields.Text(string='19- Estipulacioones particulares')
    txt21 = fields.Text(string='21- Formalizado')
    txt21b = fields.Text(string='21b - Fecha Formalizado')
    txt22 = fields.Text(string='22- Firma y Sello Remitente')
    txt23 = fields.Text(string='23- Firma y Sello Transportista')
    txt241 = fields.Text(string='24- Recobro Mercancia')
    txt242 = fields.Text(string='24b- Recobro fecha')

    @api.depends("picking_ids", "expediente_ids")
    def _compute_exp_picking_ids(self):
        for item in self:
            if item.expediente_ids:
                item.exp_picking_ids = self.env['stock.picking'].search(
                    [('analytic_account_id', 'in', item.expediente_ids.ids)])
            else:
                item.exp_picking_ids = self.env['stock.picking'].search([('id', '!=', 0)])
            item.paleteur = 0
            item.paletgr = 0
            item.totalbultos = 0
            for record in item.picking_ids:
                item.paleteur += record.paleteur
                item.paletgr += record.paletgr
                item.totalbultos += record.totalbultos

    def cambiadestinos(self):
        destinoor = self.destinoor
        lineas = ""
        for lineasalbaranes in self.linealbcompra:
            lineas += str(lineasalbaranes.id) + ","
            lineasalbaranes.plataformadestino = destinoor
        return {}

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/' and ('tipoviaje' in vals and vals['tipoviaje'] == 'INTERNACIONAL'):
            vals['name'] = self.env['ir.sequence'].next_by_code('picking.batch') or '/'
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('picking.batch.ln') or '/'
        return super().create(vals)

    def _sanity_check(self):
        _logger.error('Pass')

    def action_indaws_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template = self.env.ref('indaws_product_extended.email_template_picking')
        ctx = {
            'default_model': 'stock.picking.batch',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template.id),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def action_creacmr(self, default=None):
        for item in self:
            item.id
            item.transportista
            item.transportista.name
            item.matricula
            item.temperatura
            item.name
            for linea in aux_txt:
                count += 1
                if count == 1:
                    if '96AORDERSP' in linea:
                        _logger.info('Fichero EDI Valido para su procesamiento')
                        id_edi_jovimer = linea[3:16]
                    else:
                        _logger.info('Fichero EDI NO Valido para su procesamiento')
                        break
                elif count == 2:
                    id_edi_cliente = linea[26:39]
                    fecha_pedido = linea[17:25]
                    fecha_llegada = linea[111:119]
                else:
                    if 'L' == linea[0:1]:
                        if not self.partner_id:
                            raise ValidationError(
                                'Ingrese un valor valido para cliente, para poder continuar con la importación')
                        template = self.env['jovimer.partner.code'].search(
                            [('name', '=', linea[34:41]), ('partner_id', '=', self.partner_id.id)], limit=1)
                        if not template:
                            raise ValidationError(
                                ("Cree el codigo de cliente %s en la tabla de referencia") % linea[34:41])
                        product_id = self.env['product.product'].search(
                            [('product_tmpl_id', '=', template.template_id)], limit=1)
                        und = linea[72:75]
                        product_description = linea[75:125]
                        if 'CT' in und:
                            id_und = 24
                        elif 'PCE' in und:
                            id_und = 1
                        elif 'KGM' in und:
                            id_und = 27
                        else:
                            id_und = 1
                        if linea[65:71].replace(' ', '') is '' or linea[65:71].replace(' ', '') is False:
                            quantity = 0
                        else:
                            quantity = float(linea[65:71].replace(' ', ''))
                        item.order_line.create(
                            {
                                "order_id": item.id,
                                "product_id": product_id.id,
                                "product_uom_qty": quantity,
                                "name": product_description,
                                "price_unit": product_id.lst_price if product_id.lst_price is not False else 0,
                                'currency_id': 1,
                            }
                        )
        return
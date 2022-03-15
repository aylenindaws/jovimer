# -*- coding: utf-8 -*-
import base64
import os.path

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import datetime, date, time, timedelta
import odoo.addons.decimal_precision as dp
import subprocess
import logging
import datetime

_logger = logging.getLogger(__name__)


class ModelSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _calc_palets(self):
        numpalets = 0.0
        try:
            for line in self.multicomp:
                numpalets += float(line.numpalets)
                self.paletsc = numpalets
        except:
            self.paletsc = 0

    def _calc_compra(self):
        try:
            order = self.id
            self.env.cr.execute(""" select avg(pvpcompra) from jovimer_lineascompra where orderline='%s'""" % (order))
            result = self.env.cr.fetchone()
            preciocompra = 'NO'
            return preciocompra
        except:
            preciocompra = 1
            return preciocompra

    @api.depends('bultos', 'cantidadpedido')
    def _compute_totalbultos(self):
        try:
            totalbultos = self.bultos * self.cantidadpedido
        except:
            totalbultos = 1
        return totalbultos

    @api.depends('product_uom_qty', 'price_unit')
    def _get_total(self):
        for saleline in self:
            saleline.pvpres2 = saleline.price_subtotal - saleline.pvpcoste - saleline.pvptrans

    expediente = fields.Many2one('jovimer.expedientes', string='Expediente', related='order_id.expediente', store=True)
    expediente_serie = fields.Selection('jovimer.expedientes', related='expediente.campanya', store=True)
    expediente_serien = fields.Many2one('jovimer.expedientes.series', related='expediente.serie')
    expediente_num = fields.Integer('jovimer.expedientes', related='expediente.name', store=True)
    bultos = fields.Float(string='Bultos x Palet')
    price_trans = fields.Float(string='Precio por kg de transporte', compute='on_change_km_transporte')
    totalbultos = fields.Float(string='Total Bultos', compute='_compute_totalbultos', store=True)
    partner_id = fields.Many2one('res.partner', string='Partner', related='order_id.partner_id', store=True)
    kgnetbulto = fields.Float(string='Kg/Net Bulto')
    unidadesporbulto = fields.Float(string='Unidades por Bulto')
    unidabulto = fields.Many2one('uom.uom', string='Ud Vta', domain=[('invisibleudvta', '=', 'SI')])
    variedad = fields.Many2one('jovimer.variedad', string='Variedad')
    calibre = fields.Many2one('jovimer.calibre', string='Calibre')
    categoria = fields.Many2one('jovimer.categoria', string='Categoria')
    confeccion = fields.Many2one('jovimer.confeccion', string='Confección')
    unidadesporbultor = fields.Float(string='Unidades por Bulto', related='confeccion.uom_for_bulge')
    udfacturacion = fields.Many2one('uom.uom', string='Ud Albaran/Factura')
    envase = fields.Many2one('jovimer.envase', string='Envase')
    marca = fields.Many2one('jovimer.marca', string='Marca')
    name = fields.Char(string='Nombre')
    nocalcbultos = fields.Boolean(string='No Calcula Bultos', related='product_id.not_calculate_lumps')
    partner = fields.Many2one('res.partner', string='Cliente')
    cantidadpedidoi = fields.Integer(string='Palets')
    cantidadpedido = fields.Float(string='Palets Venta', digits=None, default=0)
    cantidadpedidoorig = fields.Float(string='Palets Venta')
    unidadpedido = fields.Many2one('uom.uom', string='Unidad Pedido', domain=[('invisiblecp', '=', 'SI')])
    product = fields.Many2one('product.product', string='Producto')
    pvpcoste = fields.Float(string='Coste')
    pvptipo = fields.Many2one('uom.uom', string='PVP/Tipo', domain=[('invisible', '=', 'NO')])
    pvptrans = fields.Float(string='Transporte')
    pvpvta = fields.Float(string='Venta')
    pvpres = fields.Float(string='Resultado')
    pvpres2 = fields.Float(string='Resultado', compute='_get_total')
    tipouom = fields.Many2one('jovimer.palet', string='Tipo Medida')
    discount_supplier = fields.Float(string='Descuento proveedor (%)', digits=dp.get_precision('Discount'), default=lambda self: self.supplier_id.default_supplierinfo_discount)
    # multicomp = fields.One2many('jovimer.lineascompra', 'orderline', string='Lineas de Compra')
    # reclamacion = fields.One2many('jovimer.reclamaciones', 'detalledocumentos', string='Reclamaciones')
    # reclamaciones = fields.Many2one('jovimer.reclamaciones', string='Reclamaciones')
    paletsc = fields.Float(string='Compra', compute='_calc_palets', store=True)
    provisionales = fields.Many2many('purchase.order.line', string='Provisionales',
                                     domain=[('expediente_serie', '=', 'PR21'), ('state', 'in', ['done', 'purchase'])],
                                     limit=2)
    provisionaleso2m = fields.One2many('purchase.order.line', 'asignacionj', string="Provisionales")
    viajedirecto = fields.Boolean(string="Viaje Directo")
    plantillaetiqueta = fields.Many2one('jovimer.etiquetas.plantilla', string='Plantilla Etiqueta')
    etiqueta = fields.Many2one('jovimer.etiquetas', string='Etiqueta')
    etiquetatxt = fields.Text(string='Etiqueta Resultante Bulto')
    etiquetatxtu = fields.Text(string='Etiqueta Resultante Unidad')
    proveedores = fields.Char(string='Proveedores')
    pvpmediocompra = fields.Char(string='P.Compra')
    precioscompra = fields.Text(string='Datos de la Compra')
    asignacionlineac = fields.Many2one('purchase.order.line', string='Linea Para Asignar', limit=1)
    edideslin = fields.Text(string='Detalles Linea EDI')
    statusrecla = fields.Selection([
        ('OK', 'OK'),
        ('RECLAMADA', 'RECLAMADA'),
        ('DEVUELTA', 'DEVUELTA'),
    ], string='Estado', default='OK')
    not_active = fields.Boolean('NO Activo', related='product_id.not_active')
    costetrans = fields.Float(string='Transporte')
    uom_po_id = fields.Many2one('uom.uom', 'Ud Compra', required=True,
                                help="Default unit of measure used for purchase orders. It must be in the same category as the default unit of measure.")

    def recalculalinea(self):
        variedad = self.product_id.variety
        calibre = self.product_id.caliber
        categoria = self.product_id.category
        confeccion = self.product_id.confection
        envase = self.product_id.container
        marca = self.product_id.brand
        bultos = self.product_id.bulge
        label = self.env['jovimer.partner.code'].search([('product_id', '=', self.product_id.id), (
        'partner_id', '=', self.partner_id.id)]) if self.product_id and self.partner_id else False
        self.tipouom = self.product_id.palet_type
        self.product_id = self.product_id.id
        self.variedad = variedad
        self.calibre = calibre
        self.categoria = categoria
        self.confeccion = confeccion
        self.envase = envase
        self.marca = marca
        self.bultos = bultos
        self.unidadpedido = self.product_id.palet_type
        self.unidabulto = self.product_id.confection.uom_bulto
        self.kgnetbulto = self.product_id.confection.kg_net_bulge
        self.unidadesporbulto = self.product_id.confection.uom_for_bulge
        self.product_uom = self.product_id.uom_type
        self.plantillaetiqueta = label if label else False
        if self.product_id:
            purchase_line = self.env['product.supplierinfo'].search([('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)], limit=1)
            supplier = purchase_line.name
            if supplier:
                self.uom_po_id = purchase_line.product_uom.id
                self.purchase_price = purchase_line.price
                self.discount_supplier = purchase_line.discount
                self.supplier_id = supplier
                self.costetrans = supplier.transport_cost
            else:
                self.uom_po_id = False
                self.purchase_price = False
                self.discount_supplier = False
                self.supplier_id = False
                self.costetrans = False
        return {}

    @api.onchange('product_id')
    def on_change_plantilla(self):
        variedad = self.product_id.variety
        calibre = self.product_id.caliber
        categoria = self.product_id.category
        confeccion = self.product_id.confection
        envase = self.product_id.container
        marca = self.product_id.brand
        bultos = self.product_id.bulge
        label = self.env['jovimer.partner.code'].search([('product_id', '=', self.product_id.id), (
        'partner_id', '=', self.partner_id.id)]) if self.product_id and self.partner_id else False
        self.tipouom = self.product_id.palet_type
        self.product_id = self.product_id.id
        self.variedad = variedad
        self.calibre = calibre
        self.categoria = categoria
        self.confeccion = confeccion
        self.envase = envase
        self.marca = marca
        self.bultos = bultos
        self.unidadpedido = self.product_id.uom_type
        self.unidabulto = self.product_id.confection.uom_bulto
        self.kgnetbulto = self.product_id.confection.kg_net_bulge
        self.unidadesporbulto = self.product_id.confection.uom_for_bulge
        self.product_uom = self.product_id.uom_type
        self.plantillaetiqueta = label if label else False
        #supplier_list = self.env['getsale.orderdata'].search([('order_id','=',self.id)]).mapped('partner_id')
        if self.product_id:
            purchase_line = self.env['product.supplierinfo'].search([('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)], limit=1)
            supplier = purchase_line.name
            if supplier:
                self.uom_po_id = purchase_line.product_uom.id
                self.purchase_price = purchase_line.price
                self.discount_supplier = supplier.default_supplierinfo_discount
                self.supplier_id = supplier
                self.costetrans = supplier.transport_cost
            else:
                self.uom_po_id = False
                self.purchase_price = False
                self.discount_supplier = False
                self.supplier_id = False
                self.costetrans = False
        return {}

    @api.onchange('supplier_id')
    def onchange_supplier_id(self):
        for item in self:
            if item.supplier_id:
                item.discount_supplier = item.supplier_id.default_supplierinfo_discount
                item.costetrans = item.supplier_id.transport_cost
            else:
                item.discount_supplier = False
                item.costetrans = False

    def buscaprovisionales(self):
        idline = self.id
        self.provisionaleso2m = False
        provisionaleso2m = self.provisionaleso2m.search(
            [('expediente_serie', '=', 'PR21'), ('state', 'in', ['done', 'purchase'])])
        if provisionaleso2m:
            for line in provisionaleso2m:
                line.asignacionj = idline
        else:
            raise UserError("NADA")
        return {}

    @api.onchange('price_unit')
    def on_change_pvpres(self):
        self.pvpres = self.price_subtotal - self.pvpcoste

    @api.onchange('cantidadpedido', 'bultos', 'kgnetbulto', 'unidabulto', 'unidadesporbultor', 'product_uom')
    def on_change_cantidadpedido(self):
        self.totalbultos = self.cantidadpedido * float(self.bultos)
        if self.product_uom.name == 'Bultos':
            self.product_uom_qty = float(self.cantidadpedido) * float(self.bultos)
        if self.product_uom.name == 'Kg':
            self.product_uom_qty = float(self.cantidadpedido) * float(self.bultos) * float(self.kgnetbulto)
        if self.product_uom.name == 'Unidades':
            self.product_uom_qty = float(self.cantidadpedido) * float(self.bultos) * float(self.unidadesporbultor)
        if self.product_uom.name == 'Palets':
            self.product_uom_qty = float(self.cantidadpedido)
        self.pvpres = self.price_subtotal - self.pvpcoste
        return {}

    def on_change_cantidadpedido_purchase(self):
        product_uom_qty = 0
        if self.product_uom.name == 'Bultos':
            product_uom_qty = float(self.cantidadpedido) * float(self.bultos)
        if self.product_uom.name == 'Kg':
            product_uom_qty = float(self.cantidadpedido) * float(self.bultos) * float(self.kgnetbulto)
        if self.product_uom.name == 'Unidades':
            product_uom_qty = float(self.cantidadpedido) * float(self.bultos) * float(self.unidadesporbultor)
        if self.product_uom.name == 'Palets':
            product_uom_qty = float(self.cantidadpedido)
        return product_uom_qty

    @api.depends('cantidadpedido','bultos','kgnetbulto')
    def on_change_km_transporte(self):
        if self.cantidadpedido and self.bultos and self.kgnetbulto:
            price_trans = self.costetrans/(float(self.cantidadpedido) * float(self.bultos) * float(self.kgnetbulto))
        else:
            price_trans = self.costetrans
        self.price_trans = price_trans
        return price_trans

    @api.onchange('confeccion')
    def on_change_confeccion(self):
        self.bultos = self.product_id.bulge
        self.kgnetbulto = self.product_id.confection.kg_net_bulge
        return {}

    @api.onchange('product_uom_qty')
    def on_change_name(self):
        cantidadpedido = self.cantidadpedido or 0
        bultos = self.bultos or 0
        cantidad = self.product_uom_qty or 0
        unidabulto = self.unidabulto
        if str(unidabulto.id) == "24":
            cantidadtotal = float(cantidadpedido) * float(bultos)
            if float(cantidadtotal) < float(cantidad):
                raise AccessError(
                    "Has sobrepasado la cantidad de Bultos por palet en cantidad. Debes corregirlo en Numero de Palets o Numero de Bultos por palet")
                self.product_uom_qty = 0

    def calcula_cantidad(self):
        orderid = self.order_id.id
        totalbultos = self.totalbultos or 0
        if totalbultos == 0:
            self.totalbultos = self.cantidadpedido * float(self.bultos)
        if self.product_uom.name == 'Bultos':
            self.product_uom_qty = float(self.cantidadpedido) * float(self.bultos)
        if self.product_uom.name == 'Kg':
            self.product_uom_qty = float(self.cantidadpedido) * float(self.bultos) * float(self.kgnetbulto)
        if self.product_uom.name == 'Unidades':
            self.product_uom_qty = float(self.cantidadpedido) * float(self.bultos) * float(self.unidadesporbultor)
        if self.product_uom.name == 'Palets':
            self.product_uom_qty = float(self.cantidadpedido)
        self.pvpres = self.price_subtotal - self.pvpcoste
        self.env.cr.execute(""" select sum(price_subtotal) from sale_order_line where order_id='%s'""" % (orderid))
        resultv = self.env.cr.fetchone()
        pricesubtot = resultv[0] or 0
        self.order_id.amount_untaxed = pricesubtot
        self.env.cr.execute(""" select sum(pvpcoste) from sale_order_line where order_id='%s'""" % (orderid))
        resultc = self.env.cr.fetchone()
        pricecoste = resultc[0] or 0
        self.order_id.coste = pricecoste
        self.order_id.amount_untaxed = pricesubtot
        self.order_id.resultado = float(pricesubtot) - float(pricecoste)
        return {}

    def action_cerrarreclamacion(self, default=None):
        self.write({'statusrecla': 'OK'})
        return {}

    def sale_abredetalle_form2(self):
        context = {'parent': self.order_id.id}
        context['view_buttons'] = True
        view = {
            'name': _('Details'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'readonly': True,
            'res_id': self.id,
            'context': context
        }
        return view

    def sale_abredetalle_form(self, context=None):
        idlin = self.id
        parent = self.order_id.id
        partnerid = self.order_id.partner_id.id
        context = {'parent': self.order_id, 'partner_id': partnerid, 'order_id': parent}
        return {
            'name': ('Pyme - Lineas de Venta'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order.line',
            'view_id': False,
            'res_id': idlin,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }

    def creaasignacioncomp(self):
        fechaoperacion = datetime.today()
        saleorderline = self.id
        numpalets = self.cantidadpedido
        unidadpedido = self.unidadpedido.id
        bultos = self.bultos
        purchaseorderline = self.asignacionlineac.id
        pvpcompra = self.asignacionlineac.price_unit
        tipoprecio = self.asignacionlineac.product_uom.id
        purchasepartner = self.asignacionlineac.partner_id.id
        expedienteo = self.asignacionlineac.order_id.expediente.id
        expediente_serieo = self.asignacionlineac.order_id.expediente.campanya
        expediente_numo = self.asignacionlineac.order_id.expediente.name
        expediente = self.order_id.expediente.id
        expediente_serie = self.order_id.expediente.campanya
        expediente_num = self.order_id.expediente.name
        nameasig = "" + str(expediente_serieo) + "/" + str(expediente_numo) + " para " + str(
            expediente_serie) + "/" + str(expediente_num) + ". LineaVenta: " + str(saleorderline) + "."
        orderline_obj = self.env['jovimer_asignaciones']
        invoice = orderline_obj.create({
            'saleorderlinedestino': saleorderline,
            'purchaseorderline': purchaseorderline,
            'fechaoperacion': fechaoperacion,
            'name': nameasig,
            'cantidad': numpalets,
            'unidad': unidadpedido,
        })
        invoice = int(invoice[0])
        self.asignado = True
        self.idasignacion = invoice
        linorderline_obj = self.env['jovimer_lineascompra']
        lincompra = linorderline_obj.create({
            'orderline': saleorderline,
            'fechacompra': fechaoperacion,
            'name': purchasepartner,
            'asignado': True,
            'idasignacion': invoice,
            'comision': 6,
            'numpalets': numpalets,
            'bultos': bultos,
            'pvpcompra': pvpcompra,
            'unidad': tipoprecio,
            'asignacion': expedienteo,
            'asignacionlinea': purchaseorderline,
        })
        lincompra = int(lincompra[0])
        self.asignacionlineac = False
        view = {
            'name': _('Asignaciones'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'jovimer_asignaciones',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': invoice
        }
        return view

    @api.onchange('price_unit','costetrans','purchase_price','discount_supplier','price_subtotal','discount')
    def onchange_margin(self):
        self.margin = self.price_unit - self.costetrans - self.purchase_price - (self.discount_supplier*self.price_subtotal) - (self.discount*self.price_subtotal)
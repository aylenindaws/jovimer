# -*- coding: utf-8 -*-
import subprocess

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ModelSaleOrderLine(models.Model):
    # Herencia de la tabla de ventas
    _inherit = 'purchase.order.line'

    def _compute_total_weight(self):
        self.totalbultos = 0
        for rec in self:
            bultos = 0
            if rec.product_id:
                bultos = rec.bultos or 0.0
                palets = rec.cantidadpedido or 0.0
                totalbultos = palets * bultos
                rec.totalbultos = totalbultos

    expediente = fields.Many2one('jovimer_expedientes', string='Expediente')
    expedienteo = fields.Many2one('jovimer_expedientes', string='Expediente', related='order_id.expediente')
    expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya', store=True)
    expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie', store=True)
    expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name', store=True)
    expediente_serieo = fields.Selection('jovimer_expedientes', related='expedienteo.campanya', store=True)
    expediente_serieno = fields.Many2one('jovimer_expedientes.series', related='expediente.serie', store=True)
    expediente_numo = fields.Integer('jovimer_expedientes', related='expedienteo.name', store=True)
    pedidocerrado = fields.Boolean(string='Pedido Cerrado', related='expediente.pedidocerrado')
    asignado = fields.Boolean(string='Asignado')
    idasignacion = fields.Many2one('jovimer_asignaciones', string='ID Asignación')
    asignacionj = fields.Many2one('sale.order.line', string='Asignación',
                                  related='idasignacion.saleorderlinedestino', store=True)
    libreasignada = fields.Float(string='Libres')
    comision = fields.Float(string='Comision')
    bultos = fields.Float(string='Bultos')
    totalbultos = fields.Float(string='Total Bultos', compute='_compute_total_weight')
    unidabulto = fields.Many2one('uom.uom', string='Tipo Medida')
    plantilla = fields.Many2one('jovimer_plantillaproductos', string='Plantilla de Producto')
    variedad = fields.Many2one('jovimer_variedad', string='Variedad')
    calibre = fields.Many2one('jovimer_calibre', string='Calibre')
    categoria = fields.Many2one('jovimer_categoria', string='Categoria')
    confeccion = fields.Many2one('jovimer_confeccion', string='Confección')
    envase = fields.Many2one('jovimer_envase', string='Envase')
    marca = fields.Many2one('jovimer_marca', string='Marca')
    name = fields.Char(string='Nombre')
    nocalcbultos = fields.Boolean(string='No Calcula Bultos')
    kgnetbulto = fields.Float(string='Kg/Net Bulto')
    partner = fields.Many2one('res.partner', string='Cliente')
    cantidadpedido = fields.Float(string='Cantidad Pedido')
    cantidadasignada = fields.Float(string='Cantidad Original')
    unidadasignada = fields.Many2one('uom.uom', string='Ud. Asig.')
    estaasignada = fields.Boolean(string='Asignado')
    expedienteorigen = fields.Many2one('jovimer_expedientes', string='Expediente Origen')
    unidadpedido = fields.Many2one('uom.uom', string='Unidad Pedido', domain=[('invisible', '=', 'NO')])
    product = fields.Many2one('product.product', string='Producto')
    pvpcoste = fields.Float(string='Coste')
    pvptipo = fields.Many2one('uom.uom', string='PVP/Tipo')
    pvptrans = fields.Float(string='Transporte')
    pvpvta = fields.Float(string='Venta')
    tipouom = fields.Many2one('uom.uom', string='Tipo Medida')
    multicomp = fields.One2many('jovimer_lineascompra', 'orderline', string='Lineas de Compra')
    saleorderline = fields.Many2one('sale.order.line', string='Lineas de Venta')
    lotecomp = fields.Char(string='Lote', related='saleorderline.order_id.reslote')
    reclamacion = fields.One2many('jovimer_reclamaciones', 'detalledocumentos', string='Reclamaciones')
    reclamaciones = fields.Many2one('jovimer_reclamaciones', string='Reclamaciones')
    viajedirecto = fields.Boolean(string="Viaje Directo")
    viajerel = fields.Many2one('jovimer_viajes', string='Viaje')
    destino = fields.Boolean(string='Para Almacén', related='order_id.destino', store=True)
    destinodonde = fields.Char(string='Donde Está', related='order_id.destinodonde', store=True)
    fechasalida = fields.Date(string='Fecha Salida', related='order_id.fechasalida')
    etiquetau = fields.Text(string='Etiqueta Unidad')
    lineafacturacompra = fields.Many2one('account.invoice', string='Albarán')
    lineaalbarancompra = fields.Many2one('account.invoice.line', string='Linea Albarán')
    albarancomprarel = fields.Many2one('account.invoice', string='Albarán Compra',
                                       related='lineaalbarancompra.invoice_id')
    etiquetab = fields.Text(string='Etiqueta BUlto')
    facturado = fields.Boolean(string='Prepara Albaran Factura')
    plantillaetiquetasc = fields.Many2one('jovimer_etiquetas_plantilla', string='Plantilla Etiquetas')
    idgeneraalbaranes = fields.Many2one('jovimer_generaalbaranes', string='ID Genera Albaranes')
    jovimer_lineascompra = fields.Many2one('jovimer_lineascompra', string='Linea Origen Compra')
    statusrecla = fields.Selection([
        ('OK', 'OK'),
        ('RECLAMADA', 'RECLAMADA'),
        ('DEVUELTA', 'DEVUELTA'),
    ], string='Estado', default='OK')

    @api.multi
    @api.onchange('plantilla')
    def on_change_plantilla(self):
        expediente = self.order_id.expediente.id
        productid = self.plantilla.product.id
        variedad = self.plantilla.variedad
        calibre = self.plantilla.calibre
        categoria = self.plantilla.categoria
        confeccion = self.plantilla.confeccion
        envase = self.plantilla.envase
        marca = self.plantilla.marca
        bultos = self.plantilla.bultos
        unidadpedido = self.plantilla.tipouom.id
        self.plantillaetiquetasc = self.plantilla.plantillaetiquetas
        self.unidadpedido = unidadpedido
        self.product_id = productid
        self.variedad = variedad
        self.calibre = calibre
        self.categoria = categoria
        self.confeccion = confeccion
        self.envase = envase
        self.marca = marca
        self.bultos = bultos
        self.kgnetbulto = self.plantilla.confeccion.kgnetobulto
        self.expediente = expediente
        return {}

    @api.multi
    def action_crearreclamacioncr(self, default=None):
        ## self.write({'statusrecla': 'RECLAMADA'})
        id = str(self.id)
        args = ["/opt/jovimer12/bin/creareclamacion_compra.bash", id, "&"]
        subprocess.call(args)
        return {}

    @api.multi
    def cargar_tablet(self, default=None):
        idmensaje = self.id
        viewname = "Cargar Linea"
        self.env.cr.execute(
            "select id from ir_ui_view where name LIKE '%view_recepcionptabletcarga_form%' and type='form' ORDER BY id DESC LIMIT 1")
        result = self.env.cr.fetchone()
        record_id = int(result[0])
        view = {
            'name': (viewname),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order.line',
            'view_id': record_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'flags': {'initial_mode': 'view'},
            'res_id': idmensaje}
        return view

    @api.multi
    def action_cerrarreclamacion(self, default=None):
        self.write({'statusrecla': 'OK'})
        return {}

    def asignaj(self):
        asignacion = self.asignacionj
        order_id = self.asignacionj.order_id
        product_id = self.product_id
        ## raise UserError("Has pinchado para añadir en: " + str(order_id) + "")
        vals = {
            'order_id': order_id,
            'product_id': product_id,
        }
        self.env['sale.order.line'].create(vals)
        ## return {'type': 'ir.actions.client', 'tag': 'reload',}

    @api.multi
    def action_creact(self, default=None):
        return {}
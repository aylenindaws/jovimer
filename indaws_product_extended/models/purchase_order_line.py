# -*- coding: utf-8 -*-
import subprocess

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.http import request
import logging
import odoo.addons.decimal_precision as dp

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

    type_state = fields.Selection([
        ('draft', 'Pendiente de revisar'),
        ('revised', 'Revisado'),
        ('grinding', 'Rectificado'),
    ], string='Estado', default='draft')
    expediente = fields.Many2one('jovimer.expedientes', string='Expediente')
    expedienteo = fields.Many2one('jovimer.expedientes', string='Expediente', related='order_id.expediente')
    expediente_serie = fields.Selection('jovimer.expedientes', related='expediente.campanya', store=True)
    expediente_serien = fields.Many2one('jovimer.expedientes.series', related='expediente.serie', store=True)
    expediente_num = fields.Integer('jovimer.expedientes', related='expediente.name', store=True)
    expediente_serieo = fields.Selection('jovimer.expedientes', related='expedienteo.campanya', store=True)
    expediente_serieno = fields.Many2one('jovimer.expedientes.series', related='expediente.serie', store=True)
    expediente_numo = fields.Integer('jovimer.expedientes', related='expedienteo.name', store=True)
    pedidocerrado = fields.Boolean(string='Pedido Cerrado', related='expediente.order_close')
    asignado = fields.Boolean(string='Asignado')
    # idasignacion = fields.Many2one('jovimer.asignaciones', string='ID Asignación')
    asignacionj = fields.Many2one('sale.order.line',
                                  string='Asignación')  # , related='idasignacion.saleorderlinedestino', store=True)
    libreasignada = fields.Float(string='Libres')
    comision = fields.Float(string='Comision')
    bultos = fields.Float(string='Bultos')
    totalbultos = fields.Float(string='Total Bultos', compute='_compute_total_weight')
    unidabulto = fields.Many2one('uom.uom', string='Tipo Medida')
    plantilla = fields.Many2one('product.template', string='Plantilla de Producto')
    variedad = fields.Many2one('jovimer.variedad', string='Variedad')
    calibre = fields.Many2one('jovimer.calibre', string='Calibre')
    categoria = fields.Many2one('jovimer.categoria', string='Categoria')
    confeccion = fields.Many2one('jovimer.confeccion', string='Confección')
    envase = fields.Many2one('jovimer.envase', string='Envase')
    marca = fields.Many2one('jovimer.marca', string='Marca')
    name = fields.Char(string='Nombre')
    nocalcbultos = fields.Boolean(string='No Calcula Bultos')
    kgnetbulto = fields.Float(string='Kg/Net Bulto')
    partner = fields.Many2one('res.partner', string='Cliente')
    cantidadpedido = fields.Float(string='Cantidad Pedido')
    cantidadasignada = fields.Float(string='Cantidad Original')
    unidadasignada = fields.Many2one('uom.uom', string='Ud. Asig.')
    estaasignada = fields.Boolean(string='Asignado')
    expedienteorigen = fields.Many2one('jovimer.expedientes', string='Expediente Origen')
    unidadpedido = fields.Many2one('uom.uom', string='Unidad Pedido', domain=[('invisible', '=', 'NO')])
    product = fields.Many2one('product.product', string='Producto')
    pvpcoste = fields.Float(string='Coste')
    pvptipo = fields.Many2one('uom.uom', string='PVP/Tipo')
    pvptrans = fields.Float(string='Transporte')
    pvpvta = fields.Float(string='Venta')
    tipouom = fields.Many2one('jovimer.palet', string='Tipo Medida')
    # multicomp = fields.One2many('jovimer.lineascompra', 'orderline', string='Lineas de Compra')
    saleorderline = fields.Many2one('sale.order.line', string='Lineas de Venta')
    lotecomp = fields.Char(string='Lote', related='saleorderline.order_id.reslote')
    reclamacion_id = fields.Many2one('jovimer.reclamaciones', string='Reclamaciones')
    # reclamaciones = fields.Many2one('jovimer.reclamaciones', string='Reclamaciones')
    viajedirecto = fields.Boolean(string="Viaje Directo")
    # viajerel = fields.Many2one('jovimer.viajes', string='Viaje')
    destino = fields.Boolean(string='Para Almacén', related='order_id.destino', store=True)
    destinodonde = fields.Char(string='Donde Está', related='order_id.destinodonde', store=True)
    fechasalida = fields.Date(string='Fecha Salida', related='order_id.fechasalida')
    etiquetau = fields.Text(string='Etiqueta Unidad')
    lineafacturacompra = fields.Many2one('account.move', string='Albarán')
    lineaalbarancompra = fields.Many2one('account.move.line', string='Linea Albarán')
    # albarancomprarel = fields.Many2one('account.invoice', string='Albarán Compra', related='lineaalbarancompra.invoice_id')
    etiquetab = fields.Text(string='Etiqueta BUlto')
    facturado = fields.Boolean(string='Prepara Albaran Factura')
    plantillaetiquetasc = fields.Many2one('jovimer.etiquetas.plantilla', string='Plantilla Etiquetas')
    # idgeneraalbaranes = fields.Many2one('jovimer.generaalbaranes', string='ID Genera Albaranes')
    # jovimer_lineascompra = fields.Many2one('jovimer.lineascompra', string='Linea Origen Compra')
    statusrecla = fields.Selection([
        ('OK', 'OK'),
        ('RECLAMADA', 'RECLAMADA'),
        ('DEVUELTA', 'DEVUELTA'),
    ], string='Estado de Rectificacion', default='OK')
    discount = fields.Float(
        string='Discount (%)', digits=dp.get_precision('Discount'),
    )
    track = fields.Text('Cambios Realizados')
    reclamation = fields.Boolean(string='Reclamacion Creada')

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

    def action_crearreclamacioncr(self, default=None):
        ## self.write({'statusrecla': 'RECLAMADA'})
        id = str(self.id)
        args = ["/opt/jovimer12/bin/creareclamacion_compra.bash", id, "&"]
        subprocess.call(args)
        return {}

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
        ## return {'type': 'ir.actions.client', 'tag': 'reload',}

    def action_creact(self, default=None):
        return {}

    @api.depends('discount')
    def _compute_amount(self):
        return super()._compute_amount()

    def _prepare_compute_all_values(self):
        vals = super()._prepare_compute_all_values()
        vals.update({'price_unit': self._get_discounted_price_unit()})
        return vals

    _sql_constraints = [
        ('discount_limit', 'CHECK (discount <= 100.0)',
         'Discount must be lower than 100%.'),
    ]

    def _get_discounted_price_unit(self):
        """Inheritable method for getting the unit price after applying
        discount(s).

        :rtype: float
        :return: Unit price after discount(s).
        """
        self.ensure_one()
        if self.discount:
            return self.price_unit * (1 - self.discount / 100)
        return self.price_unit

    def _get_stock_move_price_unit(self):
        """Get correct price with discount replacing current price_unit
        value before calling super and restoring it later for assuring
        maximum inheritability.

        HACK: This is needed while https://github.com/odoo/odoo/pull/29983
        is not merged.
        """
        price_unit = False
        price = self._get_discounted_price_unit()
        if price != self.price_unit:
            # Only change value if it's different
            price_unit = self.price_unit
            self.price_unit = price
        price = super()._get_stock_move_price_unit()
        if price_unit:
            self.price_unit = price_unit
        return price

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        """
        Check if a discount is defined into the supplier info and if so then
        apply it to the current purchase order line
        """
        res = super()._onchange_quantity()
        if self.product_id:
            date = None
            if self.order_id.date_order:
                date = self.order_id.date_order.date()
            seller = self.product_id._select_seller(
                partner_id=self.partner_id, quantity=self.product_qty,
                date=date, uom_id=self.product_uom)
            self._apply_value_from_seller(seller)
        return res

    @api.model
    def _apply_value_from_seller(self, seller):
        """Overload this function to prepare other data from seller,
        like in purchase_triple_discount module"""
        if not seller:
            return
        self.discount = seller.discount

    def revised_funtion(self):
        self.type_state = 'revised'

    def grinding_funtion(self):
        context_name = self.env.context.get('params')
        purchase_order_id = context_name.get('id')
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "indaws_product_extended.purchase_order_line_form_action_indaws")
        form_view = [(self.env.ref('indaws_product_extended.jovimer_purchase_order_line_view_form').id, 'form')]
        action['views'] = form_view
        action['context'] = {
            'default_order_line_id': self.id,
            'default_product_id': self.product_id.id,
            'default_product_qty': self.product_qty,
            'default_price_unit': self.price_unit,
            'default_qty_received': self.qty_received,
            'default_qty_invoiced': self.qty_invoiced,
            'default_discount': self.discount,
            'default_track': self.track
        }
        return action

    def create_reclamation_funtion(self):
        form_view = self.env.ref('indaws_product_extended.jovimer_reclamaciones_view_cuenta_venta_form')
        reclamation_id = self.env['jovimer.reclamaciones'].search([("detalledocumentoscompra", "=", self.id)], limit=1)
        return {
            'name': _('Reclamacion'),
            'res_model': 'jovimer.reclamaciones',
            'res_id': reclamation_id.id,
            'views': [(form_view.id, 'form'), ],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_detalledocumentoscompra': self.id,
                'default_expediente': self.expediente.id
            }
        }

    def create_reclamation_funtion_old(self):
        reclamation_id = self.env['jovimer.reclamaciones'].search([("detalledocumentoscompra", "=", self.id)], limit=1).id
        context_name = self.env.context.get('params')
        purchase_order_id = context_name.get('id')
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "indaws_product_extended.purchase_reclamation_form_action_indaws")
        form_view = [(self.env.ref('indaws_product_extended.jovimer_reclamaciones_view_form').id, 'form')]
        action['views'] = form_view
        action['res_id'] = reclamation_id
        return action

    def draft_funtion(self):
        if not self.facturado:
            self.type_state = 'draft'
        else:
            raise ValidationError('Esta linea de pedido ya se encuentra Facturada')

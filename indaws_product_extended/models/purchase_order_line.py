# -*- coding: utf-8 -*-
import subprocess

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.http import request
import logging
import odoo.addons.decimal_precision as dp
import math
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
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
    # asignado = fields.Boolean(string='Asignado')
    # libreasignada = fields.Float(string='Libres')
    # comision = fields.Float(string='Comision')

    # expediente = fields.Many2one('jovimer.expedientes', string='Expediente', related='sale_line_id.expediente')
    # expediente_serie = fields.Selection('jovimer.expedientes', related='expediente.campanya')
    # expediente_serien = fields.Many2one('jovimer.expedientes.series', related='expediente.serie')
    # expediente_num = fields.Integer('jovimer.expedientes', related='expediente.name')
    # pedidocerrado = fields.Boolean(string='Pedido Cerrado', related='expediente.order_close')

    bultos = fields.Float(string='Bultos', related='sale_line_id.bultos')
    totalbultos = fields.Float(string='Total Bultos', compute='_compute_total_weight')
    unidabulto = fields.Many2one('uom.uom', string='Tipo Medida', related='sale_line_id.unidabulto')
    variedad = fields.Many2one('jovimer.variedad', string='Variedad', related='sale_line_id.variedad')
    calibre = fields.Many2one('jovimer.calibre', string='Calibre', related='sale_line_id.calibre')
    categoria = fields.Many2one('jovimer.categoria', string='Categoria', related='sale_line_id.categoria')
    confeccion = fields.Many2one('jovimer.confeccion', string='Confección', related='sale_line_id.confeccion')
    envase = fields.Many2one('jovimer.envase', string='Envase', related='sale_line_id.envase')
    marca = fields.Many2one('jovimer.marca', string='Marca', related='sale_line_id.marca')
    kgnetbulto = fields.Float(string='Kg/Net Bulto', related='sale_line_id.kgnetbulto')
    tipouom = fields.Many2one('jovimer.palet', string='Tipo Medida', related='sale_line_id.tipouom')
    # unidadpedido = fields.Many2one('uom.uom', string='Unidad Pedido', domain=[('invisible', '=', 'NO')])
    # pvpcoste = fields.Float(string='Coste', related='sale_line_id.pvpcoste')
    # pvptipo = fields.Many2one('uom.uom', string='PVP/Tipo', related='sale_line_id.pvptipo')
    # pvptrans = fields.Float(string='Transporte', related='sale_line_id.pvptrans')
    # pvpvta = fields.Float(string='Venta', related='sale_line_id.pvpvta')
    cantidadpedido = fields.Float(string='Cantidad Pedido', related='sale_line_id.cantidadpedido')
    lotecomp = fields.Char(string='Lote', related='sale_line_id.order_id.reslote')

    reclamacion_id = fields.Many2one('jovimer.reclamaciones', string='Reclamaciones')
    reclamation = fields.Boolean(string='Reclamacion Creada')

    facturado = fields.Boolean(string='Prepara Albaran Factura')

    statusrecla = fields.Selection([
        ('OK', 'OK'),
        ('RECLAMADA', 'RECLAMADA'),
        ('DEVUELTA', 'DEVUELTA'),
    ], string='Estado de Rectificacion', default='OK')
    discount = fields.Float(
        string='Discount (%)', digits=dp.get_precision('Discount'),
    )
    track = fields.Text('Cambios Realizados')

    product_qty = fields.Float('Cantidad', compute='_compute_product_qty',
                                digits=dp.get_precision('Product Unit of Measure'), store=True, copy=False)


    @api.depends('product_uom_qty')
    def _compute_product_qty(self):
        for item in self:
            item.product_qty = item.product_uom_qty
    # @api.onchange('plantilla')
    # def on_change_plantilla(self):
    #     expediente = self.order_id.expediente.id
    #     productid = self.plantilla.product.id
    #     variedad = self.plantilla.variedad
    #     calibre = self.plantilla.calibre
    #     categoria = self.plantilla.categoria
    #     confeccion = self.plantilla.confeccion
    #     envase = self.plantilla.envase
    #     marca = self.plantilla.marca
    #     bultos = self.plantilla.bultos
    #     unidadpedido = self.plantilla.tipouom.id
    #     self.plantillaetiquetasc = self.plantilla.plantillaetiquetas
    #     self.unidadpedido = unidadpedido
    #     self.product_id = productid
    #     self.variedad = variedad
    #     self.calibre = calibre
    #     self.categoria = categoria
    #     self.confeccion = confeccion
    #     self.envase = envase
    #     self.marca = marca
    #     self.bultos = bultos
    #     self.kgnetbulto = self.plantilla.confeccion.kgnetobulto
    #     self.expediente = expediente
    #     return {}

    # def action_crearreclamacioncr(self, default=None):
    #     ## self.write({'statusrecla': 'RECLAMADA'})
    #     id = str(self.id)
    #     args = ["/opt/jovimer12/bin/creareclamacion_compra.bash", id, "&"]
    #     subprocess.call(args)
    #     return {}

    # def cargar_tablet(self, default=None):
    #     idmensaje = self.id
    #     viewname = "Cargar Linea"
    #     self.env.cr.execute(
    #         "select id from ir_ui_view where name LIKE '%view_recepcionptabletcarga_form%' and type='form' ORDER BY id DESC LIMIT 1")
    #     result = self.env.cr.fetchone()
    #     record_id = int(result[0])
    #     view = {
    #         'name': (viewname),
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'purchase.order.line',
    #         'view_id': record_id,
    #         'type': 'ir.actions.act_window',
    #         'target': 'new',
    #         'flags': {'initial_mode': 'view'},
    #         'res_id': idmensaje}
    #     return view

    def action_cerrarreclamacion(self, default=None):
        self.write({'statusrecla': 'OK'})
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
                'default_expediente': self.account_analytic_id.id,
                'default_cliente': self.partner_id.id
            }
        }

    def draft_funtion(self):
        if not self.facturado:
            self.type_state = 'draft'
        else:
            raise ValidationError('Esta linea de pedido ya se encuentra Facturada')

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        vals = super(PurchaseOrderLine, self)._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
        product_uom_qty = self.product_qty / self.sale_line_id.kgnetbulto
        if product_uom.rounding == 1:
            # If rounding of the uom is 1, upper round
            product_uom_qty = math.ceil(product_uom_qty)
        else:
            product_uom_qty = float_round(product_uom_qty, precision_rounding=product_uom.rounding)
        vals['product_uom_qty'] = product_uom_qty
        return vals

    def on_change_cantidadpedido_purchase(self, unidad_venta, unidad_compra):
        product_uom_qty = self.product_uom_qty
        if unidad_venta == 'Bultos' and unidad_compra == 'Kg':
            product_uom_qty = float(self.product_uom_qty) * float(self.kgnetbulto)
        if unidad_venta == 'Bultos' and unidad_compra == 'Unidades':
            product_uom_qty = float(self.product_uom_qty) * float(self.unidadesporbultor)
        if unidad_venta == 'Kg' and unidad_compra == 'Unidades':
            product_uom_qty = (float(self.product_uom_qty) * float(self.kgnetbulto)) / float(self.unidadesporbultor)
        if unidad_venta == 'Kg' and unidad_compra == 'Bultos':
            product_uom_qty = float(self.product_uom_qty) / float(self.kgnetbulto)
        if unidad_venta == 'Unidades' and unidad_compra == 'Bultos':
            product_uom_qty = float(self.product_uom_qty) / float(self.unidadesporbultor)
        if unidad_venta == 'Unidades' and unidad_compra == 'Kg':
            product_uom_qty = (float(self.product_uom_qty) * float(self.bultos)) / float(self.kgnetbulto)
        return product_uom_qty

    @api.depends('move_ids.state', 'move_ids.product_uom_qty', 'move_ids.product_uom')
    def _compute_qty_received(self):
        # pre-calculation of quantities for transfer
        from_stock_lines = self.filtered(lambda order_line: order_line.qty_received_method == 'stock_moves')
        for line in self:
            if line.qty_received_method == 'stock_moves':
                total = 0.0
                # In case of a BOM in kit, the products delivered do not correspond to the products in
                # the PO. Therefore, we can skip them since they will be handled later on.
                for move in line.move_ids.filtered(lambda m: m.product_id == line.product_id):
                    if move.state == 'done' and line.product_uom.factor==1 and move.product_uom.factor==1:
                        if move.location_dest_id.usage == "supplier":
                            if move.to_refund:
                                total -= line.on_change_cantidadpedido_purchase(line.product_uom,move.product_uom)
                        elif move.origin_returned_move_id and move.origin_returned_move_id._is_dropshipped() and not move._is_dropshipped_returned():
                            # Edge case: the dropship is returned to the stock, no to the supplier.
                            # In this case, the received quantity on the PO is set although we didn't
                            # receive the product physically in our stock. To avoid counting the
                            # quantity twice, we do nothing.
                            pass
                        elif (move.location_dest_id.usage == "internal" and move.to_refund and move.location_dest_id not in self.env["stock.location"].search([("id", "child_of", move.warehouse_id.view_location_id.id)])):
                            total -= line.on_change_cantidadpedido_purchase(line.product_uom,move.product_uom)
                        else:
                            total += line.on_change_cantidadpedido_purchase(line.product_uom,move.product_uom)
                line._track_qty_received(total)
                line.qty_received = total
        if line.qty_received == 0:
            super(PurchaseOrderLine, self)._compute_qty_received()
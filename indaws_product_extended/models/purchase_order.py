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
    att = fields.Char(string='Atención de:')
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
    account_analytic_id = fields.Many2one('account.analytic.account', string='Expediente')
    validate_line = fields.Boolean(string='Revisado', compute="_compute_validate_line", store="True")

    @api.depends("order_line.type_state")
    def _compute_validate_line(self):
        for item in self:
            item.validate_line = True
            for line in item.order_line:
                if line.type_state == 'draft':
                    item.validate_line = False

    def action_create_invoice(self):
        for item in self:
            for line in item.order_line:
                if line.type_state == 'draft':
                    raise ValidationError('La linea con id: ' + str(
                        line.id) + ' No se encuentra Validada\n se requiere una Validacion completa de la orden')
            super(PurchaseOrder, item).action_create_invoice()

    @api.model
    def create(self, vals):
        result = super(PurchaseOrder, self).create(vals)
        if result.sale_related_id:
            if not result.fechasalida:
                result.fechasalida = result.sale_related_id.fechasalida
            if not result.fechallegada:
                result.fechallegada = result.sale_related_id.fechallegada
            if not result.horallegada:
                result.horallegada = result.sale_related_id.horallegada
            if not result.account_analytic_id:
                result.account_analytic_id = result.sale_related_id.analytic_account_id
        return result

    def action_claim_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template = self.env.ref('indaws_product_extended.email_template_cuenta_venta')
        ctx = {
            'default_model': 'purchase.order',
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
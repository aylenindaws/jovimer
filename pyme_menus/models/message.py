# -*- coding: utf-8 -*-

from odoo import models, fields, api
	
class Message_Customprv(models.Model):
    _inherit = "mail.message"
    
    venta_pr = fields.Many2one('sale.order', string='Presupuesto de Venta', domain=[('type_doc','=', 'Presupuesto')], help='Pr VTA')
    venta_pv = fields.Many2one('sale.order', string='Presupuesto de Venta', domain=[('type_doc','=', 'Pedido')], help='Pedido VTA')
    venta_ab = fields.Many2one('sale.order', string='Albaran de Venta', domain=[('type_doc','=', 'Albaran')], help='Ab COM')
    compra_pr = fields.Many2one('purchase.order', string='Presupuesto de Compra', domain=[('type_doc','=', 'Presupuesto')], help='Pr COM')
    compra_pv = fields.Many2one('purchase.order', string='Pedido de Compra', domain=[('type_doc','=', 'Pedido')], help='Pv COM')
    compra_ab = fields.Many2one('purchase.order', string='Albaran de Compra', domain=[('type_doc','=', 'Albaran')], help='Ab COM')
    cobro = fields.Many2one('account.payment', string='Registro Cobros', domain=[('partner_type', '=', 'customer')], help='Cobros')
    pago = fields.Many2one('account.payment', string='Registro Pagos', domain=[('partner_type', '=', 'supplier')], help='Pagos')
    ## expediente = fields.Many2one('jovimer_expedientes', string='Expediente')
    ## expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya')
    ## expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name') 


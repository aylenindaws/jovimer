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


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_total_coste(self):
        for rec in self:
            coste = 0
            venta = 0
            trans = 0
            venta = rec.amount_untaxed
            for line in rec.order_line:
                if line.product_id:
                    coste += line.pvpcoste or 0.0
            rec.coste = coste
            rec.resultado = venta - coste

    purchase_related_ids = fields.One2many('purchase.order', 'sale_related_id', string="Related purchase orders",
                                           readonly=False)
    # Campos Pesonalizados en pedidos de Venta
    fechasalida = fields.Date(string='Fecha de Salida')
    fechallegada = fields.Date(string='Fecha de Llegada')
    horallegada = fields.Char(string='Hora de Llegada', help='Permite caracteres Alfanuméricos')
    campanya = fields.Char(string='Serie / Campaña', help='Número Expediente')
    expediente = fields.Many2one('jovimer.expedientes', string='Expediente')
    expediente_serie = fields.Selection('jovimer.expedientes', related='expediente.campanya', store=True)
    expediente_serien = fields.Many2one('jovimer.expedientes.series', related='expediente.serie')
    expediente_num = fields.Integer('jovimer.expedientes', related='expediente.name', store=True)
    mododecobro = fields.Many2one('payment.acquirer', string='Modo de Cobros')
    conformalote = fields.Many2one('jovimer.conflote', string='Conforma LOTE', store=True)
    reslote = fields.Char(string='Lote')
    obspedido = fields.Text(string='Observaciones PEdido')
    description = fields.Char(string='Desc.')
    palets = fields.Float(string='C. Compra', compute='_compute_paletsc')
    paletsv = fields.Float(string='C. Venta')
    refcliente = fields.Char(string='Referencia Pedido Cliente', help='Referencia Cliente')
    plataforma = fields.Char(string='Plataforma', help='Plataforma Destino')
    etiquetas = fields.One2many('jovimer.etiquetas', 'order_id', string='Etiquetas del Pedido')
    estadopalets = fields.Boolean(string='Estado Palets')
    faltanpalets = fields.Float(string='Faltan')
    pedcompra = fields.Many2many('purchase.order', string='Pedidos de Compra')
    regcalidad = fields.Text(string='Registro de Calidad')
    moneda = fields.Many2one('res.currency', string='Moneda')
    costetrans = fields.Float(string='Transporte')
    coste = fields.Float(string='Compra', compute='_compute_total_coste')
    resultado = fields.Float(string='Resultado')
    pedidocerrado = fields.Boolean(string='Pedido Cerrado')
    serieexpnuevo = fields.Many2one('jovimer.expedientes.series', string="Serie Expediente")  # , default=12)
    numexpnuevo = fields.Integer(string="Número Expediente")
    edi_file_binary = fields.Binary(attachment=False, string="Fichero EDI", store=True, copy=True, ondelete='set null')
    edi_file = fields.Many2one('ir.attachment', string="Fichero EDI", store=True, copy=True, ondelete='set null',
                               domain="[('mimetype','=','text/plain')]")

    def update_edi_file(self, default=None):
        for item in self:
            count = 0
            aux_txt = base64.b64decode(item.edi_file.datas).decode('ascii', 'ignore').split('\n')
            item.order_line.unlink()
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
                        product_id = self.env['product.template'].search([('partner_code', '=', linea[34:41])], limit=1)
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

    @api.onchange('edi_file_binary')
    def _onchange_field_edi(self):
        for record in self:
            if record.edi_file_binary:
                record.edi_file = self.env['ir.attachment'].create({
                    'name': ("EDI IMPORT " + str(record.id)),
                    'type': 'binary',
                    'datas': record.edi_file_binary,
                    'res_model': record._name,
                    'res_id': record.id
                })

    def cambiar_expediente(self, default=None):
        expediente = self.expediente.id
        order_id = self.id
        view = {
            'name': _('Cambio de Expediente en Pedido de Compra'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'jovimer_wizardsaleexp',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_expediente': expediente, 'default_order_id': order_id}
        }
        return view

    def action_calcpedido(self, default=None):
        for lines in self.order_line:
            calculo = lines.calcula_cantidad()
        return {}

    def creaexpediente(self, default=None):
        id = str(self.id)
        numexpnuevo = self.numexpnuevo
        serieexpnuevoid = self.serieexpnuevo.id
        serieexpnuevoname = self.serieexpnuevo.name
        buscaexp = self.env['jovimer_expedientes'].search_count(
            [('name', '=', numexpnuevo), ('serie', '=', serieexpnuevoid)])
        if buscaexp != 0:
            raise UserError(
                "El Número de Expediente ya existe o no se puede Usar:" + str(serieexpnuevoname) + "-" + str(
                    numexpnuevo) + ".")
            return {}
        else:
            expediente_obj = self.env['jovimer_expedientes']
            expedientenuevo = expediente_obj.create({
                'serie': serieexpnuevoid,
                'name': numexpnuevo})
            self.write({'expediente': expedientenuevo.id})
            return {}

    @api.onchange('conformalote', 'fechallegada', 'fechasalida')
    def onchange_conformalote(self):
        self.ensure_one()
        confname = str(self.conformalote.name)
        fechallegada = str(self.fechallegada)
        fechasalida = str(self.fechasalida)

        if confname == "LO PONE EL CLIENTE":
            self.reslote = ' '

        if confname == "SEMANA/DIA LLEGADA":
            try:
                weekday = self.fechallegada.strftime("%w")
                if str(weekday) == "0":
                    weekday = "7"
                else:
                    weekday = str(weekday)

                year = fechallegada.split('-')[0]
                month = fechallegada.split('-')[1]
                day = fechallegada.split('-')[2]
                dt = date(int(year), int(month), int(day))
                wk = dt.isocalendar()[1]
                self.reslote = str(wk) + '/' + str(weekday.zfill(2))
            except:
                self.reslote = 'Faltan datos'
        if confname == "SEMANA/DIA SALIDA":
            try:
                weekday = self.fechasalida.strftime("%w")
                if str(weekday) == "0":
                    weekday = "7"
                else:
                    weekday = str(weekday)

                year = fechasalida.split('-')[0]
                month = fechasalida.split('-')[1]
                day = fechasalida.split('-')[2]
                dt = date(int(year), int(month), int(day))
                wk = dt.isocalendar()[1]
                self.reslote = str(wk) + '/' + str(weekday.zfill(2))
            except:
                self.reslote = 'Faltan datos'

        if confname == "SEMANA/AÑO LLEGADA":
            try:
                year = fechallegada.split('-')[0]
                month = fechallegada.split('-')[1]
                day = fechallegada.split('-')[2]
                dt = date(int(year), int(month), int(day))
                wk = dt.isocalendar()[1]
                self.reslote = str(wk) + '/' + str(year)
            except:
                self.reslote = 'Faltan datos'

        if confname == "SEMANA/DIA LLEGADA-3":
            try:
                diaresto = 3
                ahora = datetime.datetime.strptime(fechallegada, '%Y-%m-%d')
                hace3diastime = str(ahora - timedelta(days=diaresto))
                hace3diastime2 = ahora - timedelta(days=diaresto)
                hace3dias = hace3diastime.split(' ')[0]
                weekday = hace3diastime2.strftime("%w")
                year = hace3dias.split('-')[0]
                month = hace3dias.split('-')[1]
                day = hace3dias.split('-')[2]
                dt = date(int(year), int(month), int(day))
                wk = dt.isocalendar()[1]
                resultado = str(weekday.zfill(2))
                if resultado == '00':
                    resultado = '07'
                self.reslote = str(wk) + '/' + str(resultado)
            except:
                self.reslote = 'Faltan datos'

        if confname == "SEMANA/DIA LLEGADA-1":
            try:
                diaresto = 1
                ahora = datetime.datetime.strptime(fechallegada, '%Y-%m-%d')
                hace3diastime = str(ahora - timedelta(days=diaresto))
                hace3diastime2 = ahora - timedelta(days=diaresto)
                hace3dias = hace3diastime.split(' ')[0]
                weekday = hace3diastime2.strftime("%w")
                year = hace3dias.split('-')[0]
                month = hace3dias.split('-')[1]
                day = hace3dias.split('-')[2]
                dt = date(int(year), int(month), int(day))
                wk = dt.isocalendar()[1]
                self.reslote = str(wk) + '/' + str(weekday.zfill(2))
            except:
                self.reslote = 'Faltan datos'

        if confname == "DIA/MES/AÑO LLEGADA":
            try:
                year = fechallegada.split('-')[0]
                month = fechallegada.split('-')[1]
                day = fechallegada.split('-')[2]
                dt = date(int(year), int(month), int(day))
                wk = dt.isocalendar()[1]
                self.reslote = str(day) + '/' + str(month) + '/' + str(year)
            except:
                self.reslote = 'Faltan datos'

        if confname == "FECHA LLEGADA -4 DIAS":
            try:
                ahora = datetime.strptime(fechallegada, '%Y-%m-%d')
                hace4 = ahora - timedelta(days=4)
                dt_string = hace4.strftime("%d/%m/%Y")
                self.reslote = str(dt_string)
            except:
                self.reslote = 'Faltan datos'

        if confname == "DIA/MES/AÑO SALIDA":
            try:
                ahora = datetime.strptime(fechasalida, '%Y-%m-%d')
                dt_string = ahora.strftime("%d/%m/%Y")
                self.reslote = str(dt_string)
            except:
                self.reslote = 'Faltan datos'

        if confname == "SEMANA/DIA LLEGADA +1":
            try:
                ahora = datetime.strptime(fechallegada, '%Y-%m-%d')
                hace4 = ahora + timedelta(days=1)
                weekday = hace4.strftime("%w")
                if str(weekday) == "0":
                    weekday = "7"
                else:
                    weekday = str(weekday)
                year = fechallegada.split('-')[0]
                month = fechallegada.split('-')[1]
                day = fechallegada.split('-')[2]
                dt = date(int(year), int(month), int(day))
                wk = dt.isocalendar()[1]
                self.reslote = str(wk) + '/' + str(weekday.zfill(2))
            except:
                self.reslote = 'Faltan datos'
        return {}

    def _compute_paletsc(self):
        numpalets = 0.0
        try:
            for line in self.order_line.multicomp:
                numpalets += line.numpalets or 0.0
            self.palets = numpalets
        except:
            self.palets = 0
        numpaletsv = 0.0
        try:
            for linev in self.order_line:
                numpaletsv += linev.cantidadpedido or 0.0
            self.paletsv = numpaletsv
        except:
            self.palets = 0

    def calcpalets(self):
        order = self.id
        self.env.cr.execute(""" select sum(numpalets) from jovimer_lineascompra where order_id='%s'""" % (order))
        result = self.env.cr.fetchone()
        palets = result[0]
        self.palets = palets
        self.env.cr.execute(""" select sum(cantidadpedido) from sale_order_line where order_id='%s'""" % (order))
        resultv = self.env.cr.fetchone()
        paletsv = resultv[0]
        self.paletsv = paletsv
        try:
            self.faltanpalets = paletsv - palets or 0
        except:
            self.faltanpalets = paletsv
        if palets != paletsv:
            self.estadopalets == True
            self.env.cr.execute(""" update sale_order set estadopalets='t' where id='%s'""" % (order))
        else:
            self.env.cr.execute(""" update sale_order set estadopalets='f' where id='%s'""" % (order))
        for lines in self.order_line:
            numpalets = 0.0
            try:
                lines.paletsc = 0.0
                for line in lines.multicomp:
                    numpalets += line.numpalets or 0.0
                    lines.paletsc = numpalets
            except:
                lines.paletsc = 0
        return {}

    def sale_createline_detalle(self, context=None):
        parent = self.id
        partner = self.partner_id.id

        orderline_obj = self.env['sale.order.line']
        invoice = orderline_obj.create({
            'order_id': parent,
            'partner_id': partner,
            'product_id': 17,
            'currency_id': 1, })
        context = {'parent': self.id}
        context['view_buttons'] = True
        invoice = int(invoice[0])
        view = {
            'name': _('Detalles de la Venta'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': invoice,
            'context': context
        }
        return view

    @api.model
    def create(self, vals_list):
        vals = super(SaleOrder, self).create(vals_list)
        if not vals.analytic_account_id:
            vals.analytic_account_id = self.env['account.analytic.account'].create(
                {'name': 'j' + str(datetime.date.today().year)[2:] + '/' + vals.name[1:]})
        return vals
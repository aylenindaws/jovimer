# -*- coding: utf-8 -*-
import base64
import os.path

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, time, timedelta
from odoo.tools import float_compare, float_is_zero, float_repr, float_round, float_split, float_split_str
import subprocess
import logging
import datetime

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _compute_total_weightnet(self):
        for rec in self:
            totalkg = 0
            for line in rec.invoice_line_ids:
                if line.product_id:
                    totalkg += line.totalkglin or 0.0
            rec.totalkg = totalkg

    relpartnerfiscal = fields.Char(string='Nombre Fiscal', related='partner_id.nomfiscal')
    relpartnercta = fields.Char(string='Cta VTA', related='partner_id.cta')
    relpartnerctap = fields.Char(string='Cta COMP', related='partner_id.ctap')
    quierebr = fields.Boolean(string='Con KG Brutos', related='partner_id.quierebr')
    noimprimepal = fields.Boolean(string='NO Imprime Tipo Palet', related='partner_id.noimprimepal')
    nobio = fields.Boolean(string='Entidad NO BIO', related='partner_id.nobio')
    edinumber = fields.Char(string='Número EDI', related='partner_id.edinumber')
    emailctaventa = fields.Char(string='Email Cuenta de Venta', related='partner_id.emailctaventa')
    ##################################################################################################
    fechasalida = fields.Date(string='Fecha de Salida')
    fechallegada = fields.Date(string='Fecha de Llegada')
    horallegada = fields.Char(string='Hora de Llegada', help='Permite caracteres Alfanuméricos')
    campanya = fields.Char(string='Serie / Campaña', help='Número Expediente')
    expediente = fields.Many2one('account.analytic.account', string='Expediente')
    mododecobro = fields.Many2one('payment.acquirer', string='Modo de Cobros')
    conformalote = fields.Many2one('jovimer.conflote', string='Conforma LOTE', store=True)
    reslote = fields.Char(string='Lote')
    obspedido = fields.Text(string='Observaciones Pedido')
    totalkg = fields.Float(string='Kg. Neto', compute='_compute_total_weightnet')
    description = fields.Char(string='Desc.')
    palets = fields.Float(string='C. Compra', compute='_compute_paletsc')
    paletsv = fields.Float(string='C. Venta')
    refcliente = fields.Char(string='Referencia Pedido Cliente', help='Referencia Cliente')
    plataforma = fields.Many2one('jovimer.plataforma', string='Plataforma')
    estadopalets = fields.Boolean(string='Estado Palets')
    faltanpalets = fields.Float(string='Faltan')
    pedcompra = fields.Many2many('purchase.order', string='Pedidos de Compra')
    regcalidad = fields.Text(string='Registro de Calidad')
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
                        if not self.partner_id:
                            raise ValidationError(
                                'Ingrese un valor valido para cliente, para poder continuar con la importación')
                        template = self.env['jovimer.partner.code'].search(
                            [('name', '=', linea[34:41]), ('partner_id', '=', self.partner_id.id)], limit=1)
                        if not template:
                            raise ValidationError(
                                ("Cree el codigo de cliente %s en la tabla de referencia") % linea[34:41])
                        product_id = template.product_id
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

    @api.onchange('conformalote', 'commitment_date', 'fechasalida')
    def onchange_conformalote(self):
        self.ensure_one()
        confname = str(self.conformalote.name)
        fechallegada = str(self.commitment_date.date()) if self.commitment_date else False
        fechasalida = str(self.fechasalida)

        if confname == "LO PONE EL CLIENTE":
            self.reslote = ' '

        if confname == "SEMANA/DIA LLEGADA":
            try:
                weekday = self.commitment_date.date().strftime("%w")
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
                if str(weekday) == "0":
                    weekday = "7"
                else:
                    weekday = str(weekday)
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
                if str(weekday) == "0":
                    weekday = "7"
                else:
                    weekday = str(weekday)
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

    def action_post(self):
        for item in self:
            for line in item.invoice_line_ids:
                if line.purchase_line_id:
                    if line.price_unit > line.purchase_line_id.price_unit + 0.01 or line.price_unit < line.purchase_line_id.price_unit - 0.01:
                        raise ValidationError('El precio Facturado para la linea de producto ' + str(
                            line.product_id.name) + ' con id ' + str(line.id) + '\ntiene una diferencia de ' + str(
                            abs(float_round((line.price_unit - line.purchase_line_id.price_unit),
                                            2))) + ' saliendose del margen de 0,01')
        super(AccountMove, self).action_post()

    @api.depends('price_unit', 'discount', 'quantity', 'price_subtotal, pvpcoste')
    def _compute_resultadoresto(self):
        coste = self.pvpcoste or 0
        ingreso = self.price_subtotal
        resultadoresto = float(ingreso) - float(coste)
        self.resultadoresto = float(resultadoresto)

    def _compute_totalbultosprev(self):
        self.totalbultosprev = 0
        for rec in self:
            bultos = 0
            if rec.product_id:
                bultos = rec.bultos or 0.0
                palets = rec.cantidadpedido or 0.0
                totalbultosprev = palets * bultos
                rec.totalbultosprev = totalbultosprev

    def _compute_previstoserror(self):
        previstoserror = False
        for lines in self:
            totalbultos = lines.totalbultos
            totalbultosprev = lines.totalbultosprev
            print("RESTO: " + str(totalbultos) + "--" + str(totalbultosprev))
            if str(totalbultos) != str(totalbultosprev):
                lines.previstoserror = True

    def _compute_subtotalasignado(self):
        subtotalasignado = 0
        for rec in self:
            ## subtotalasignado = sum(rec.price_subtotalas)
            original = rec.asignaroriginal
            invoice_id = rec.move_id.id
            asignarmadre = rec.id
            if original == False:
                subtotalasignado = rec.price_subtotal
                try:
                    self.env.cr.execute(
                        """ select sum(price_subtotalas) from account_invoice_line where invoice_id='%s' and asignarmadre='%s' """ % (
                        invoice_id, asignarmadre))
                    result = self.env.cr.fetchone()
                    subtotalasignado = result[0] or 0.0
                except:
                    subtotalasignado = 0
                    # subtotalasignado = sum(rec.price_subtotalas)
                    ## print("\n\n -------------------------- " + str(subtotalasignado) + "\n\n")
                rec.subtotalasignado = subtotalasignado

    def _compute_valorcvvta(self):
        valorcvvta = 0
        for rec in self:
            rec.valorcvvta = rec.subtotalasignado

    def _compute_pvpcvvta(self):
        pvpcvvta = 0
        for rec in self:
            preciooriginal = rec.price_unit
            cantidadoriginal = rec.quantity
            discount = rec.discount
            valorcvvta = rec.valorcvvta
            valororiginal = rec.price_subtotal
            if valorcvvta == valororiginal:
                pvpcvvta = preciooriginal
            else:
                try:
                    dtodec = discount / 100
                    dto2 = 1 + dtodec
                    pvpcvvta = (valorcvvta * dto2) / cantidadoriginal
                except:
                    pvpcvvta = 0
                rec.pvpcvvta = pvpcvvta


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    expediente = fields.Many2one('account.analytic.account', string='Expediente')
    # expediente = fields.Many2one('account.analytic.accoun', string='Expediente', domain=[('serie','in',(1,3,4,12))])
    # expediente_origen = fields.Integer(string='Número', help='Número Expediente', related='invoice_id.expediente.name')
    # expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya')
    # expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')
    # fechasalida = fields.Date('jovimer_expedientes', related='expediente.fechasalida')
    # fechallegada= fields.Date('jovimer_expedientes', related='expediente.fechallegada')
    # clientefinal= fields.Many2one('res.partner', related='expediente.cliente')
    cantidadpedido = fields.Float(string='Palets')
    unidadpedido = fields.Many2one('uom.uom', string='Tipo', domain=[('invisiblecp', '=', 'SI')])
    bultos = fields.Float(string='Bultos')
    unidabulto = fields.Many2one('uom.uom', string='Ud. NO FUN')
    variedad = fields.Many2one('jovimer.variedad', string='Variedad')
    variedadeng = fields.Char(string='Traduccion', related='variedad.abrev')
    calibre = fields.Many2one('jovimer.calibre', string='Calibre')
    categoria = fields.Many2one('jovimer.categoria', string='Categoria')
    confeccion = fields.Many2one('jovimer.confeccion', string='Confección')
    envase = fields.Many2one('jovimer.envase', string='Envase')
    envasecod = fields.Char(string='Envase Codigo', related='envase.code')
    marca = fields.Many2one('jovimer.marca', string='Marca')
    nocalcbultos = fields.Boolean(string='No Calcula Bultos')
    unidabulto = fields.Many2one('uom.uom', string='Unidad', domain=[('invisibleudvta', '=', 'SI')])
    kgnetbulto = fields.Float(string='Kg/Net Bulto', store=True)
    totalbultos = fields.Float(string='Total Bultos', store=True)
    quedanbultos = fields.Float(string='Quedan', store=True)
    totalbultosprev = fields.Float(string='Total Previstos', store=True)
    previstoserror = fields.Boolean(string='Error Previstos')
    cargado = fields.Boolean(string='Cargado')
    cargado_por = fields.Many2one('res.users', string='Quien')
    cargado_cuando = fields.Date(string='Cuando')
    cargado_cuandot = fields.Datetime(string='Cuando')
    obsbultos = fields.Char(string='Obs')
    unidadesporbulto = fields.Float(string='Unidad por Bulto')
    partner = fields.Many2one('res.partner', string='Cliente')
    ## plantillaeti
    pvpcoste = fields.Float(string='Coste')
    pvptipo = fields.Many2one('uom.uom', string='PVP/Tipo')
    pvptrans = fields.Float(string='Transporte')
    pvpvta = fields.Float(string='Venta')
    tipouom = fields.Many2one('uom.uom', string='Tipo Medida')
    preparaalbvta = fields.Boolean(string='Prepara Albaran de Venta')
    asignado = fields.Boolean(string='Asignada Compra')
    relalbvta = fields.Char(string='Relacion Albarán de Venta')
    # multicomp = fields.One2many('jovimer_lineascompra', 'orderline', string='Lineas de Compra')
    reclamacion = fields.One2many('jovimer.reclamaciones', 'detalledocumentos', string='Reclamaciones')
    reclamaciones = fields.Many2one('jovimer.reclamaciones', string='Reclamaciones')
    # ordendecarganac = fields.Many2many('jovimer_ctn', string='Orden de Carga Nacional')
    # ordendecargaint = fields.Many2many('jovimer_cti', string='Orden de Carga Internacional')
    # lineacompra = fields.Many2one('purchase.order.line', string='Linea de Compra')
    fechallegadanac = fields.Date(string='Fecha LLegada Nacional')
    # lineacompracalidadpartner = fields.Many2one('res.partner', string='Proveedor', related='lineacompra.partner_id')
    nobioline = fields.Boolean(string='NO BIO L')
    nobioexp = fields.Boolean(string='NO BIO EXP')
    ### lineacompracalidadpartnerbio = fields.Boolean(string='Entidad NO BIO', related='lineacompracalidadpartner.nobio')
    lineaventa = fields.Many2one('sale.order.line', string='Linea de Venta')
    precioscompra = fields.Text(string='Datos de la Compra', related='lineaventa.precioscompra')
    pvpcoste = fields.Float(string='Coste', related='lineaventa.pvpcoste')
    resultadoresto = fields.Float(string='Resultado')
    ## resultadorestocalc = fields.Float(string='Resultado'store=True, readonly=True, compute='_compute_resultadoresto')
    lineaventaud = fields.Many2one('uom.uom', string='Unidad Pedido Cliente', related='lineaventa.unidabulto')
    descctavta = fields.Char(string='Motivo')
    fechafact = fields.Date(string='Fecha Documento', related='move_id.invoice_date')
    fechafact2 = fields.Date(string='Fecha Documento INTRA / Guardado')
    ## camount_untaxed = fields.Float(string='Tot', related='move_id.amount_untaxed')
    ctavtarepasado = fields.Boolean(string='Repasado')
    ctavtarepasadoas = fields.Boolean(string='Repasado Asignado')
    priceas = fields.Float(string='Precio')
    discountas = fields.Float(string='Dto%')
    price_subtotalas = fields.Float(string='Total')
    ctavtaenviado = fields.Boolean(string='Para Enviar')
    ctavtafin = fields.Boolean(string='Enviado')
    valorcvvta = fields.Float(string='TOTAL C/V')
    pvpcvvta = fields.Float(string='Precio C/V', compute="_compute_pvpcvvta")
    fechactavtarepasado = fields.Date(string='Fecha Repasado Cuenta de Venta')
    fechactavtarepasadoas = fields.Date(string='Fecha Repasado Cuenta de Venta')
    fechactavtaenviado = fields.Date(string='Fecha Enviado Cuenta de Venta')
    ocultaimpresion = fields.Boolean(string='NO Imprime')
    devolucion = fields.Boolean(string='Devuelto')
    basura = fields.Boolean(string='Basura')
    basuralineamadre = fields.Many2one('account.move.line', string='Origen Basura')
    basuralineadestino = fields.Many2one('account.move.line', string='Destino Basura')
    albvtadestinolin = fields.Many2one('account.move.line', string='Linea Albarán Destino')
    unidabultoj = fields.Many2one('uom.uom', string='Tipo Cálculo Jovimer', related='purchase_line_id.product_uom',
                                  domain=[('invisible', '=', 'NO')])
    cantidadj = fields.Float(string='Cantidad Jovimer')
    subtotalj = fields.Float(string='Subtotal Jovimer')
    pricej = fields.Float(string='Precio Jovimer', related='purchase_line_id.price_unit')
    unidabultoalb = fields.Many2one('uom.uom', string='Tipo Cálculo Albarán', domain=[('invisible', '=', 'NO')])
    cantidadalb = fields.Float(string='Cantidad Albarán')
    subtotalalb = fields.Float(string='Subtotal Albarán')
    subtotalasignado = fields.Float(string='Subtotal Asignado', compute='_compute_subtotalasignado')
    pricealb = fields.Float(string='Precio Jovimer')
    paislins = fields.Many2one('res.country', string='Pais')
    totalkglin = fields.Float(string='Kg Net')
    totalkglinbr = fields.Float(string='Kg Brut')
    # viaje = fields.Many2one('jovimer_viajes', string='Viaje Relacionado')
    paislin = fields.Many2one(string='Link Country', related='move_id.partner_id.country_id')
    albvtadestino = fields.Many2one('account.move', string='Albarán Destino')
    albvtadestinolin = fields.Many2one('account.move.line', string='Linea Albarán Destino')
    devoluvta = fields.Boolean(string='Devolución')
    # devoluvtar = fields.Many2one('jovimer_devalbaranv', string='Devolución')
    factcompradestino = fields.Many2one('account.move', string='Factura Destino')
    docqueorigina = fields.Many2one('account.move', string='Documento Origen')
    buscaasignacion = fields.Many2one('purchase.order.line', string='Busca Asignacion',
                                      domain=[('asignado', '=', True)])
    diariofactura = fields.Many2one(string='Diario', related='move_id.journal_id')
    descripcioncajas = fields.Float(string='CxP')
    asignarcantidad = fields.Integer(string='Cantidad Asignada')
    asignarunidad = fields.Many2one('uom.uom', string='Unidad Asignada', domain=[('invisiblecp', '=', 'SI')])
    asignarquedaran = fields.Integer(string='Cantidad que Quedará')
    asignarnosale = fields.Boolean(string='No EL AlbCli')
    asignaroriginal = fields.Boolean(string='No Original')
    asignarprimera = fields.Boolean(string='Primera')
    asignarmadre = fields.Many2one('account.move.line', string='Linea Madre')
    asignarquedaranbultos = fields.Integer(string='Bultos que Quedarán')
    asignarcantidadviaje = fields.Integer(string="Asigna")
    asignarrestodviaje = fields.Float(string="Stock")
    lineaalbarancompra = fields.Many2one('account.move.line', string='Linea Albaran Compra')
    lineacabalbarancompra = fields.Many2one('account.move', string='Albaran Compra')
    cabeceraalbarancompra = fields.Char(string='Albaran Compra', related='lineaalbarancompra.move_id.name')
    cabeceraalbarancompraid = fields.Many2one('account.move', string='Albaran Compra',
                                              related='lineaalbarancompra.move_id')
    algovamal = fields.Boolean(string='No cuadra')
    ## errorvamal = fields.Boolean(string='No cuadra')
    bultostotalesalbarancompra = fields.Float(string='Bultos Totales Albarán Compra')
    bultostotalespedidocompra = fields.Float(string='Bultos Totales Pedido Compra')
    remontado = fields.Boolean(string='Remontado')
    nocargar = fields.Boolean(string='NO CARGAR')
    nocargarasig = fields.Boolean(string='NO CARGAR LINEA ASIGNADA VIAJE')
    plataformaorigen = fields.Many2one('res.partner', string='Almacén Origen')
    plataformadestino = fields.Many2one('res.partner', string='Destino')
    preciomediaintra = fields.Float(string='Precio Intrastat KG', group_operator="avg")
    precioenkg = fields.Float(string='Precio en KG')
    tipomovalmacen = fields.Selection([('ENTRADA', 'ENTRADA'), ('SALIDA', 'SALIDA'), ('BASURA', 'BASURA')],
                                      string='Tipo Movimiento')
    cantidadalmacencajas = fields.Float(string='Cantidad Almacén Cajas')
    cantidadalmacenkg = fields.Float(string='Cantidad Almacén KG')
    fechaalmacen = fields.Date(string='Fecha de Almacén')
    precioalmacenkg = fields.Float(string='Precio Medio Almacén KG')
    fechapedidocompra = fields.Date(string='Fecha Pedido Compra')
    fechapedidoventa = fields.Date(string='Fecha Pedido Venta')
    fechapedidosalida = fields.Date(string='Fecha Pedido/Salida')
    trasladaalbaran = fields.Many2one('account.move', string='Albarán Destino',
                                      domain=[('journal_id', '=', 9), ('state', '=', 'draft')])
    numdelinea = fields.Integer(string='NLin')
    dividiralbarane = fields.Many2one('account.move', string='Albarán Existente')
    typefact = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Vendor Bill'),
        ('out_refund', 'Customer Credit Note'),
        ('in_refund', 'Vendor Credit Note'),
    ], readonly=True, related='move_id.move_type', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='Status', index=True, readonly=True, default='draft', related='move_id.state', store=True)
    correctoctavta = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO'),
        ('FALTA', 'FALTA'),
    ], string='Estado', default='FALTA')

    correctoliqui = fields.Selection([
        ('SI', 'SI'),
        ('NO', 'NO'),
        ('FALTA', 'FALTA'),
    ], string='Estado', default='FALTA')
    descliqui = fields.Char(string='Motivo')
    statusrecla = fields.Selection([
        ('OK', 'OK'),
        ('RECLAMADA', 'RECLAMADA'),
        ('DEVUELTA', 'DEVUELTA'),
    ], string='Estado', default='OK')
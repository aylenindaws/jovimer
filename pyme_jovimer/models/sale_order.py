# -*- coding: utf-8 -*-
import base64

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import subprocess
from time import sleep
from datetime import datetime, date, time, timedelta

class ModelSaleOrder(models.Model):
     
     # Herencia de la tabla de ventas
     _inherit = 'sale.order'

     def _compute_palets(self):
        try:
          palets = 0
          paletsv = 0
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
           self.faltanpalets = abs(paletsv - palets) or 0
          except:
           self.faltanpalets = paletsv
          if palets != paletsv:
           self.estadopalets == True
           self.env.cr.execute(""" update sale_order set estadopalets='t' where id='%s'""" % (order))
          else:
           self.env.cr.execute(""" update sale_order set estadopalets='f' where id='%s'""" % (order))
           ## raise UserError("Estoy Aki MAL")
          for lines in self.order_line:
           numpalets = 0.0
           try:
            lines.paletsc = 0.0
            for line in lines.multicomp:        
             numpalets += line.numpalets or 0.0
             lines.paletsc =  numpalets
           except:
            lines.paletsc =  0
        except:
          palets = 0
          paletsv = 0

        return {} 

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
 
     # Campos Pesonalizados en pedidos de Venta
     fechasalida  = fields.Date(string='Fecha de Salida')
     fechallegada = fields.Date(string='Fecha de Llegada')
     horallegada  = fields.Char(string='Hora de Llegada', help='Permite caracteres Alfanuméricos')
     campanya = fields.Char(string='Serie / Campaña', help='Número Expediente')
     expediente = fields.Many2one('jovimer_expedientes', string='Expediente')
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya', store=True)
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')
     expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name', store=True)
     mododecobro = fields.Many2one('payment.acquirer', string='Modo de Cobros')
     conformalote = fields.Many2one('jovimer_conflote', string='Conforma LOTE')
     reslote = fields.Char(string='Lote')
     obspedido = fields.Text(string='Observaciones PEdido')
     description  = fields.Char(string='Desc.')
     palets  = fields.Float(string='C. Compra', compute='_compute_palets')
     paletsv  = fields.Float(string='C. Venta')
     refcliente = fields.Char(string='Referencia Pedido Cliente', help='Referencia Cliente')
     plataforma = fields.Char(string='Plataforma', help='Plataforma Destino')	 
     etiquetas = fields.One2many('jovimer_etiquetas','saleorder', string='Etiquetas del Pedido')
     estadopalets = fields.Boolean(string='Estado Palets')	
     faltanpalets  = fields.Float(string='Faltan')
     pedcompra = fields.Many2many('purchase.order', string='Pedidos de Compra')
     regcalidad = fields.Text(string='Registro de Calidad')
     moneda = fields.Many2one('res.currency', string='Moneda')
     costetrans = fields.Float(string='Transporte')
     coste = fields.Float(string='Compra', compute='_compute_total_coste')
     resultado = fields.Float(string='Resultado')
     pedidocerrado = fields.Boolean(string='Pedido Cerrado')
     edifile = fields.Binary(string="Fichero EDI")
     editxt= fields.Many2one(comodel_name="ir.attachment", string="Fichero EDI", domain="[('mimetype','=','text/plain')]" )
     serieexpnuevo = fields.Many2one('jovimer_expedientes.series', string="Serie Expediente", default=12)
     numexpnuevo = fields.Integer(string="Número Expediente")

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
             'context': {'default_expediente':expediente,'default_order_id': order_id}
             }
            return view

     def action_calcpedido(self, default=None):
        ## raise UserError("Recalculo No completado")
        for lines in self.order_line:
            calculo = lines.calcula_cantidad()
        return {}

     def creaexpediente(self, default=None):
         id = str(self.id)
         numexpnuevo = self.numexpnuevo
         serieexpnuevoid = self.serieexpnuevo.id
         serieexpnuevoname = self.serieexpnuevo.name
         buscaexp = self.env['jovimer_expedientes'].search_count([('name', '=', numexpnuevo ),('serie', '=', serieexpnuevoid )])
         if buscaexp != 0:
            raise UserError("El Número de Expediente ya existe o no se puede Usar:" + str(serieexpnuevoname) + "-" + str(numexpnuevo) + ".")
            return {}
         else:
            expediente_obj = self.env['jovimer_expedientes']
            expedientenuevo = expediente_obj.create({
                        'serie': serieexpnuevoid,
                        'name': numexpnuevo})
            self.write({'expediente': expedientenuevo.id })
            return {}

     def cargaredi(self, default=None):
         id = str(self.id)
         args = ["/opt/jovimer12/bin/importaedi_pedido.sh", id, "&"]
         subprocess.call(args)
         return {}

     def import_file(self, context=None):
         TemporaryFile = '/tmp/edi1.txt'
         fileobj = TemporaryFile('w+')
         fileobj.write(base64.decodestring(self.edi_file))
         # your treatment
         return

     def action_creapedidocompra(self, default=None):
        id = str(self.id)
        #### fechasalida = str(self.fechasalida)
        #### fechallegada = str(self.fechallegada)
        #### if fechasalida == 'False':
        ####     raise AccessError("NO puede procesarse el pedido si no hay una Fecha de Salida: " + fechasalida + " o Llegada Registrada: " + fechallegada + ".")
        #### if fechallegada == 'False':
        ####     raise AccessError("NO puede procesarse el pedido si no hay una Fecha de Salida: " + fechasalida + " o Llegada Registrada: " + fechallegada + ".")
        args = ["/opt/jovimer12/bin/creapedidocompra.bash", id, "&"]
        subprocess.call(args)
        palets = 0
        paletsv = 0
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
         ## raise UserError("Estoy Aki MAL")
        for lines in self.order_line:
         numpalets = 0.0
         try:
          lines.paletsc = 0.0
          for line in lines.multicomp:        
           numpalets += line.numpalets or 0.0
           lines.paletsc =  numpalets
         except:
          lines.paletsc =  0
        return {}

     def jovimer_view_lineasventa(self, context=None):
        self.ensure_one()
        ### self.env.cr.execute(""" select id from ir_ui_view where name LIKE '%JOVIMER - Control Transporte Nacional%' and type='tree' ORDER BY id DESC LIMIT 1""")
        ### result = self.env.cr.fetchone()
        ### record_id = int(result[0])
        ### partner = self._ids[0]
        orderid = self.id
        return {
        'name': ("Lineas de Venta"),
        'type': 'ir.actions.act_window',
        'res_model': 'sale.order.line',
        'view_mode': 'tree',
        'view_type': 'form',
        ## 'view_id': record_id,
        'target': 'current',
        'domain': [('order_id','=',orderid)],
        }
        return {}

     ### def action_creapedidocompra(self, default=None):
     ###     id = str(self.id)
     ###     args = ["/opt/jovimer12/bin/creapedidocompra.bash", id, "&"]
     ###     subprocess.call(args)
     ###     return {}

     @api.onchange('conformalote','fechallegada','fechasalida')
     def on_change_conformalote(self):
         import datetime
         from datetime import datetime, date, time, timedelta
         confid = str(self.conformalote.id)
         fechallegada = str(self.fechallegada)
         fechasalida = str(self.fechasalida)
         
         ## Lo pone el Cliente
         if confid == "3":
          self.reslote = ' '

         ## SEMANA/DIA LLEGADA
         if confid == "1":
          try:
           weekday=self.fechallegada.strftime("%w")
           if str(weekday) == "0":
            weekday="7"
           else:
            weekday=str(weekday)

           year = fechallegada.split('-')[0]
           month = fechallegada.split('-')[1]
           day  = fechallegada.split('-')[2]
           dt = date(int(year), int(month), int(day))
           wk = dt.isocalendar()[1]
           self.reslote = str(wk) + '/' + str(weekday.zfill(2))
          except:
           self.reslote = 'Faltan datos'     

         ## SEMANA/DIA SALIDA
         if confid == "2":
          try:
           weekday=self.fechasalida.strftime("%w")
           if str(weekday) == "0":
            weekday="7"
           else:
            weekday=str(weekday)

           year = fechasalida.split('-')[0]
           month = fechasalida.split('-')[1]
           day  = fechasalida.split('-')[2]
           dt = date(int(year), int(month), int(day))
           wk = dt.isocalendar()[1]
           self.reslote = str(wk) + '/' + str(weekday.zfill(2))
          except:
           self.reslote = 'Faltan datos'     

         ## SEMANA / AÑO LLEGADA
         if confid == "4":
          try:
           year = fechallegada.split('-')[0]
           month = fechallegada.split('-')[1]
           day  = fechallegada.split('-')[2]
           dt = date(int(year), int(month), int(day))
           wk = dt.isocalendar()[1]
           self.reslote = str(wk) + '/' + str(year)
          except:
           self.reslote = 'Faltan datos'     

         ## SEMANA / AÑO SALIDA - 3
         if confid == "5":
          try:
           diaresto=3
           ahora = datetime.strptime(fechallegada, '%Y-%m-%d')
           hace3diastime = str(ahora - timedelta(days=diaresto))
           hace3diastime2 = ahora - timedelta(days=diaresto)
           hace3dias = hace3diastime.split(' ')[0]
           weekday = hace3diastime2.strftime("%w")
           year = hace3dias.split('-')[0]
           month = hace3dias.split('-')[1]
           day  = hace3dias.split('-')[2]
           dt = date(int(year), int(month), int(day))
           wk = dt.isocalendar()[1]
           resultado = str(weekday.zfill(2))
           if resultado == '00':
              resultado = '07'
           self.reslote = str(wk) + '/' + str(resultado)
          except:
           self.reslote = 'Faltan datos' 

         ## SEMANA / AÑO SALIDA - 1
         if confid == "6":
          try:
           diaresto=1
           ahora = datetime.strptime(fechallegada, '%Y-%m-%d')
           hace3diastime = str(ahora - timedelta(days=diaresto))
           hace3diastime2 = ahora - timedelta(days=diaresto)
           hace3dias = hace3diastime.split(' ')[0]
           weekday = hace3diastime2.strftime("%w")
           year = hace3dias.split('-')[0]
           month = hace3dias.split('-')[1]
           day  = hace3dias.split('-')[2]
           dt = date(int(year), int(month), int(day))
           wk = dt.isocalendar()[1]
           self.reslote = str(wk) + '/' + str(weekday.zfill(2))
          except:
           self.reslote = 'Faltan datos'

         ## DIA/MES/AÑO
         if confid == "7":
          try:
           year = fechallegada.split('-')[0]
           month = fechallegada.split('-')[1]
           day  = fechallegada.split('-')[2]
           dt = date(int(year), int(month), int(day))
           wk = dt.isocalendar()[1]
           self.reslote = str(day) + '/' + str(month) + '/' + str(year)
          except:
           self.reslote = 'Faltan datos'



         ## DIA LLEGADA MENOS - 4
         if confid == "8":
          try:
           ahora = datetime.strptime(fechallegada, '%Y-%m-%d')
           hace4 = ahora - timedelta(days=4)
           dt_string = hace4.strftime("%d/%m/%Y")
           self.reslote = str(dt_string)
          except:
           self.reslote = 'Faltan datos' 


         ## DIA/MES/AÑO DE SALIDA
         if confid == "9":
          try:
           ahora = datetime.strptime(fechasalida, '%Y-%m-%d')
           dt_string = ahora.strftime("%d/%m/%Y")
           self.reslote = str(dt_string)
          except:
           self.reslote = 'Faltan datos' 


         ## SEMANA/DIA LLEGADA + 1
         if confid == "12":
          try:
           ahora = datetime.strptime(fechallegada, '%Y-%m-%d')
           hace4 = ahora + timedelta(days=1)
           weekday=hace4.strftime("%w")
           if str(weekday) == "0":
            weekday="7"
           else:
            weekday=str(weekday)
           year = fechallegada.split('-')[0]
           month = fechallegada.split('-')[1]
           day  = fechallegada.split('-')[2]
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
        self.palets =  numpalets
       except:
        self.palets =  0
       numpaletsv = 0.0
       try:
        for linev in self.order_line:        
            numpaletsv += linev.cantidadpedido or 0.0
        self.paletsv =  numpaletsv
       except:
        self.palets =  0

     def calcpalets(self):
        palets = 0
        paletsv = 0
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
         ## raise UserError("Estoy Aki MAL")
        for lines in self.order_line:
         numpalets = 0.0
         try:
          lines.paletsc = 0.0
          for line in lines.multicomp:        
           numpalets += line.numpalets or 0.0
           lines.paletsc =  numpalets
         except:
          lines.paletsc =  0

        return {}     

     ### @api.onchange('order_line')
     ### def on_change_order_line(self):
     ###  try:
     ###    palets = 10
     ###    paletsv = 10
     ###  except:
     ###    palets = 0
     ###    paletsv = 0	  
     ###  return {}     

     def sale_createline_detalle(self, context=None):
        cr = self._cr
        uid = self._uid
        ids = self._ids
        parent = self.id
        partner = self.partner_id.id
        
        orderline_obj = self.env['sale.order.line']
        invoice = orderline_obj.create({
                   'order_id': parent,
                   'partner_id': partner,
                   'product_id': 17,
                   'currency_id': 1, })
        ## args = ["/opt/jovimer12/bin/webservice/create_sale_order_line.py", str(parent), str(partner)]
		## subprocess.call(args)      
        ## return {}
        context = {'parent': self.id}
        context['view_buttons'] = True
        invoice = int(invoice[0])
        ## raise UserError("Generada la linea " + str(invoice) + ", para el pedido: " + str(self.id) + ".")
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


     
class ModelSaleOrderLine(models.Model):
     
     # Herencia de la tabla de ventas
     _inherit = 'sale.order.line'

     def _calc_palets(self):
       numpalets = 0.0
       try:
        for line in self.multicomp:        
         numpalets += float(line.numpalets)
         self.paletsc =  numpalets
       except:
        self.paletsc =  0
     
     def _calc_compra(self):
       try:
         preciocompra = 2		  
         order = self.id		 
         self.env.cr.execute(""" select avg(pvpcompra) from jovimer_lineascompra where orderline='%s'""" % (order))
         result = self.env.cr.fetchone()
         preciocompra = result[0]
         ## raise UserError("Order: " + str(order) + ". Precio: " + str(preciocompra) + "")
         preciocompra = 'NO' 
         return preciocompra
       except:
         preciocompra = 1
         return preciocompra	

     @api.depends('bultos','cantidadpedido')
     
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

     expediente = fields.Many2one('jovimer_expedientes', string='Expediente', related='order_id.expediente', store=True)
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya', store=True)
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')
     expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name', store=True)
     bultos = fields.Float(string='Bultos x Palet')  
     totalbultos = fields.Float(string='Total Bultos', compute='_compute_totalbultos', store=True)
     partner_id = fields.Many2one(string='Partner', related='order_id.partner_id', store=True)
     kgnetbulto = fields.Float(string='Kg/Net Bulto')
     unidadesporbulto = fields.Float(string='Unidades por Bulto')
     unidabulto = fields.Many2one('uom.uom', string='Ud Vta', domain=[('invisibleudvta','=','SI')])
     plantilla = fields.Many2one('jovimer_plantillaproductos', string='Plantilla de Producto')
     variedad = fields.Many2one('jovimer_variedad', string='Variedad')
     calibre = fields.Many2one('jovimer_calibre', string='Calibre')
     categoria = fields.Many2one('jovimer_categoria', string='Categoria')
     confeccion = fields.Many2one('jovimer_confeccion', string='Confección')
     kgnetbultor = fields.Float(string='Kg/Net Bulto', related='confeccion.kgnetobulto')
     unidadesporbultor = fields.Float(string='Unidades por Bulto', related='confeccion.unidadesporbulto')
     udfacturacion = fields.Many2one('uom.uom', string='Ud Albaran/Factura', related='plantilla.udfacturacion')
     envase = fields.Many2one('jovimer_envase', string='Envase')
     marca = fields.Many2one('jovimer_marca', string='Marca')
     name  = fields.Char(string='Nombre')
     nocalcbultos = fields.Boolean(string='No Calcula Bultos')  
     partner = fields.Many2one('res.partner', string='Cliente')
     cantidadpedidoi = fields.Integer(string='Palets')
     cantidadpedido = fields.Float(string='Palets Venta', digits=None, default=0)
     cantidadpedidoorig = fields.Float(string='Palets Venta')
     unidadpedido = fields.Many2one('uom.uom', string='Tipo Palet', domain=[('invisiblecp','=','SI')])
     product = fields.Many2one('product.product', string='Producto')
     pvpcoste = fields.Float(string='Coste') 
     pvptipo = fields.Many2one('uom.uom', string='PVP/Tipo', domain=[('invisible','=','NO')])
     pvptrans = fields.Float(string='Transporte') 
     pvpvta = fields.Float(string='Venta') 
     pvpres = fields.Float(string='Resultado') 
     pvpres2 = fields.Float(string='Resultado', compute='_get_total')
     tipouom = fields.Many2one('uom.uom', string='Tipo Medida', domain=[('invisible','=','NO')])
     multicomp = fields.One2many('jovimer_lineascompra', 'orderline', string='Lineas de Compra')
     reclamacion = fields.One2many('jovimer_reclamaciones', 'detalledocumentos', string='Reclamaciones')
     reclamaciones = fields.Many2one('jovimer_reclamaciones', string='Reclamaciones')
     paletsc  = fields.Float(string='Compra', compute='_calc_palets',store=True)
     ### paletsc  = fields.Float(string='Compra')
     provisionales = fields.Many2many('purchase.order.line', string='Provisionales', domain=[('expediente_serie','=','PR21'),('state', 'in', ['done', 'purchase'])], limit=2)
     provisionaleso2m = fields.One2many('purchase.order.line', 'asignacionj', string="Provisionales")
     viajedirecto = fields.Boolean(string="Viaje Directo")
     plantillaetiqueta = fields.Many2one('jovimer_etiquetas_plantilla', string='Plantilla Etiqueta')
     etiqueta = fields.Many2one('jovimer_etiquetas', string='Etiqueta')
     etiquetatxt = fields.Text(string='Etiqueta Resultante Bulto')
     etiquetatxtu = fields.Text(string='Etiqueta Resultante Unidad')
     proveedores = fields.Char(string='Proveedores')
     pvpmediocompra = fields.Char(string='P.Compra')
     precioscompra = fields.Text(string='Datos de la Compra')
     asignacionlineac = fields.Many2one('purchase.order.line', string='Linea Para Asignar', limit=1)
     edideslin = fields.Text(string='Detalles Linea EDI')
     statusrecla = fields.Selection([
		('OK','OK'),
		('RECLAMADA','RECLAMADA'),
		('DEVUELTA','DEVUELTA'),
		],string='Estado',default='OK')     
  

     def recalculalinea(self): 
             productid = self.plantilla.product.id
             variedad = self.plantilla.variedad
             calibre = self.plantilla.calibre
             categoria = self.plantilla.categoria
             confeccion = self.plantilla.confeccion
             envase = self.plantilla.envase
             marca = self.plantilla.marca
             bultos = self.plantilla.bultos
             self.product_id = productid
             self.variedad = variedad
             self.calibre = calibre
             self.categoria = categoria
             self.confeccion = confeccion
             self.envase = envase
             self.marca = marca
             self.bultos = bultos
             self.unidadpedido = self.plantilla.tipouom
             self.unidabulto = self.plantilla.confeccion.unidabulto
             self.kgnetbulto = self.plantilla.confeccion.kgnetobulto
             self.unidadesporbulto = self.plantilla.confeccion.unidadesporbulto
             self.product_uom = self.plantilla.tipouom
             self.plantillaetiqueta = self.plantilla.plantillaetiquetas
             ## self.totalbultos = bultos * self.cantidadpedido
             return {}

     @api.onchange('plantilla')
     def on_change_plantilla(self):
             productid = self.plantilla.product.id
             variedad = self.plantilla.variedad
             calibre = self.plantilla.calibre
             categoria = self.plantilla.categoria
             confeccion = self.plantilla.confeccion
             envase = self.plantilla.envase
             marca = self.plantilla.marca
             bultos = self.plantilla.bultos
             self.product_id = productid
             self.variedad = variedad
             self.calibre = calibre
             self.categoria = categoria
             self.confeccion = confeccion
             self.envase = envase
             self.marca = marca
             self.bultos = bultos
             self.unidadpedido = self.plantilla.tipouom
             self.unidabulto = self.plantilla.confeccion.unidabulto
             self.kgnetbulto = self.plantilla.confeccion.kgnetobulto
             self.unidadesporbulto = self.plantilla.confeccion.unidadesporbulto
             self.product_uom = self.plantilla.tipouom
             self.plantillaetiqueta = self.plantilla.plantillaetiquetas
             ## self.totalbultos = bultos * self.cantidadpedido
             return {}

     ## @api.onchange('confeccion')
     ## def on_change_confeccion(self):
     ##         unidades = self.confeccion.unidadesporbulto
     ##         bultose = self.confeccion.bultoseuropalet	 
     ##         bultosg = self.confeccion.bultosgrandpalet
     ##         kgnetbulto = self.confeccion.kgnetobulto
     ##         self.bultos = bultos
     ##         self.kgnetbulto = kgnetbulto
     ##         self.unidadesporbulto = unidades
     ##         return {}
			 

     def buscaprovisionales(self):
             idorder = self.order_id			
             idline = self.id
             self.provisionaleso2m = False
             provisionaleso2m = self.provisionaleso2m.search([('expediente_serie', '=', 'PR21'),('state', 'in', ['done', 'purchase'])])
             ## print (" >>>>>>>>>>>>>>>>>>>>             Line: " + str(idline) + " ==== " + str(provisionaleso2m) + " <<<<<<<<<<<<<<<<<<<<<")
             if provisionaleso2m:
               for line in provisionaleso2m:
                  line.asignacionj = idline
             else:
               raise UserError("NADA")			 
             return {}

     @api.onchange('price_unit') 
     def on_change_pvpres(self):
             self.pvpres = self.price_subtotal - self.pvpcoste

     @api.onchange('cantidadpedido','bultos','kgnetbulto','unidabulto','kgnetbultor','unidadesporbultor') 
     def on_change_cantidadpedido(self):
             self.totalbultos = self.cantidadpedido * float(self.bultos)
             ## raise AccessError("Tipo: " + str(self.unidabulto))
             ## Bultos
             if self.unidabulto.id == 24:
                self.product_uom_qty = float(self.cantidadpedido) * float(self.bultos)
             ## KG
             if self.unidabulto.id == 27:
                self.product_uom_qty = float(self.cantidadpedido) * float(self.bultos) * float(self.kgnetbultor)
             ## Unidades
             if self.unidabulto.id == 1:
                self.product_uom_qty = float(self.cantidadpedido) * float(self.bultos) * float(self.unidadesporbultor)
             return {}

     @api.onchange('cantidadpedido','bultos','kgnetbulto','unidabulto','kgnetbultor','unidadesporbultor') 
     def on_change_unidabulto(self):
             self.totalbultos = self.cantidadpedido * float(self.bultos)
             ## raise AccessError("Tipo: " + str(self.unidabulto))
             ## Bultos
             unidabulto = self.unidabulto
             if self.unidabulto.id == 24:
                self.product_uom_qty = float(self.cantidadpedido) * float(self.bultos)
             ## KG
             if self.unidabulto.id == 27:
                self.product_uom_qty = float(self.cantidadpedido) * float(self.bultos) * float(self.kgnetbultor)
             ## Unidades
             if self.unidabulto.id == 1:
                self.product_uom_qty = float(self.cantidadpedido) * float(self.bultos) * float(self.unidadesporbultor)
             self.pvpres = self.price_subtotal - self.pvpcoste
             self.unidabulto = unidabulto
             return {}



     @api.onchange('confeccion') 
     def on_change_confeccion(self):
             self.bultos = self.plantilla.bultos
             self.kgnetbulto = self.plantilla.confeccion.kgnetobulto
             return {}



     @api.onchange('product_uom_qty') 
     def on_change_name(self):
             cantidadpedido = self.cantidadpedido or 0
             bultos = self.bultos or 0
             cantidad = self.product_uom_qty or 0
             unidabulto = self.unidabulto
             print("\n\n\n LINEA: " + str(cantidadpedido) + "::" + str(bultos) + "::" + str(cantidad) + ">" + str(unidabulto.id) + "< ::\n\n\n ")
             if str(unidabulto.id) == "24":
                   cantidadtotal = float(cantidadpedido) * float(bultos)
                   print("\n\n\n LINEA: " + str(cantidadtotal) + " < " + str(cantidad) + "\n\n\n")
                   if float(cantidadtotal) < float(cantidad):
                       raise AccessError("Has sobrepasado la cantidad de Bultos por palet en cantidad. Debes corregirlo en Numero de Palets o Numero de Bultos por palet")
                       self.product_uom_qty = 0
                       

     def calcula_cantidad(self):
             ## raise AccessError("Tipo: " + str(self.unidabulto))
             ## Bultos
             orderid = self.order_id.id
             price_subtotal = 0
             price_subtotal = self.price_subtotal
             totalbultos = 0
             totalbultos = self.totalbultos or 0
             if totalbultos == 0:
                    totalbultos = float(self.cantidadpedido) * float(self.bultos)
                    self.totalbultos = totalbultos
             if self.unidabulto.id == 24:
                self.product_uom_qty = totalbultos
             ## KG
             if self.unidabulto.id == 27:
                self.product_uom_qty = float(totalbultos) * float(self.kgnetbulto)
             ## Unidades
             if self.unidabulto.id == 1:
                self.product_uom_qty = float(totalbultos) * float(self.unidadesporbulto)
             self.pvpres = self.price_subtotal - self.pvpcoste

             ## Sumamos Lineas
             pricesubtot = 0
             pricecoste = 0
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


     def regeneraetiqueta(self, default=None):
           ## self.write({'statusrecla': 'RECLAMADA'})
           id = str(self.id)
           args = ["/opt/jovimer12/bin/crearetiqueta.sh", id, "&"]
           subprocess.call(args)
           return {}

     def action_crearreclamacion(self, default=None):
           ## self.write({'statusrecla': 'RECLAMADA'})
           id = str(self.id)
           args = ["/opt/jovimer12/bin/creareclamacion.bash", id, "&"]
           subprocess.call(args)
           return {}


     def action_cerrarreclamacion(self, default=None):
           self.write({'statusrecla': 'OK'})
           return {}

     def sale_abredetalle_form2(self):
        ## context = self.env.context.copy()
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
        cr = self._cr
        uid = self._uid
        ids = self._ids
        idlin = self.id
        parent = self.order_id.id
        partnerid = self.order_id.partner_id.id
        context = {'parent': self.order_id, 'partner_id': partnerid, 'order_id': parent}
        ## raise AccessError("Contexto: " + str(context))
        return {
           'name': ('Pyme - Lineas de Venta'),
           'view_type': 'form',
           'view_mode': 'form',
           'res_model': 'sale.order.line',
           'view_id': False,
           'res_id': idlin,
           'type': 'ir.actions.act_window',
           'target':'new',
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
            nameasig = "" + str(expediente_serieo) + "/" + str(expediente_numo) + " para " + str(expediente_serie) + "/" + str(expediente_num) + ". LineaVenta: " + str(saleorderline) + "."
            ### raise UserError(str(nameasig))
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
            ### view = {}
            return view	   
	   
class ModelLinesCompra(models.Model):
     
     # Herencia de la tabla de ventas
     _name = 'jovimer_lineascompra'
     
     orderline = fields.Many2one('sale.order.line', string='Linea Compra')
     order_id = fields.Many2one('sale.order', string='Orden Venta', related='orderline.order_id', auto_join=True, store=True)
     fechacompra = fields.Date(string='Fecha Compra')  
     proveedor = fields.Many2one('res.partner', string='Proveedor')
     name = fields.Many2one('res.partner', string='Proveedor')
     comision = fields.Float(string='Comisión') 
     numpalets = fields.Float(string='Palets') 
     bultos = fields.Float(string='BxP') 
     pvpcompra = fields.Float(string='Precio Compra') 
     unidad = fields.Many2one('uom.uom', string='Unidad Comp', domain=[('invisibleudvta','=','SI')])
     asignado = fields.Boolean(string='Asignado')
     asignacion = fields.Many2one('jovimer_expedientes', string='Exp')
     idasignacion = fields.Many2one('jovimer_asignaciones', string='Asignacion')
     asignacionlinea = fields.Many2one('purchase.order.line', string='Compra Origen')
     expediente_serie = fields.Selection('jovimer_expedientes', related='asignacion.campanya', store=True)
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='asignacion.serie', store=True)	 
     proveedores = fields.Char(string='Proveedores')
     paletsc = fields.Float(string='Palets Compra', related='orderline.paletsc', auto_join=True) 
     purchaseline = fields.Many2one('purchase.order.line', string='Linea Compra')
 

     @api.onchange('fechacompra')
     def on_change_fechacompra(self):
            ## proveedorid = self.name.name
            self.comision = self.name.comisionvta or 6
            self.bultos = self.orderline.bultos or 0
            self.unidad = self.orderline.unidabulto or None
            self.numpalets = self.orderline.cantidadpedido or 0			 
            return {}

     def creaasignacioncomp(self):
            lineaid = self.id
            proveedorid = self.name.id
            saleorderline = self.orderline.id
            expediente = self.orderline.order_id.expediente.id
            expediente_serie = self.orderline.order_id.expediente.campanya
            expediente_num = self.orderline.order_id.expediente.name
            nameasig = "- " + str(expediente_serie) + "/" + str(expediente_num) + ". LineaVenta: " + str(saleorderline) + "."
            fechaoperacion = datetime.today()
            orderline_obj = self.env['jovimer_asignaciones']
            invoice = orderline_obj.create({
                   'saleorderlinedestino': saleorderline,
                   'fechaoperacion': fechaoperacion,
                   'lineavtacompra': nameasig,
                   'name': lineaid,
                   })
            invoice = int(invoice[0])
            self.asignado = True
            self.idasignacion = invoice
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



            ## raise UserError("Vas a Generar una Asignación de la linea:" + str(saleorderline) + " y Expdiente: " + str(expediente) + ".")			
            return {}


class WizardCambiarExpediente(models.Model):
     
     # Herencia de la tabla de ventas
     _name = 'jovimer_wizardsaleexp'
	 
     order_id = fields.Many2one('sale.order', string='Pedido Venta')	 
     partner_id = fields.Many2one('res.partner', string='Cliente', related='order_id.partner_id')	
     expediente = fields.Many2one('jovimer_expedientes', string='Expediente Actual')
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya', store=True)
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')
     expedientenuevo = fields.Many2one('jovimer_expedientes', string='Expediente Nuevo')
     expedientenuevo_serie = fields.Selection('jovimer_expedientes', related='expedientenuevo.campanya', store=True)
     expedientenuevo_serien = fields.Many2one('jovimer_expedientes.series', related='expedientenuevo.serie')


     def cambiar_expediente(self, default=None):
        expediente_nuevo = self.expedientenuevo.id
        order_id = self.order_id.id
        ## raise AccessError("Vas a Cambiar al Expediente " + str(expediente_nuevo) + ", el Pedido: " + str(order_id) + ".")
        pedidoventa_obj = self.env['sale.order']
        marcaprocesado = pedidoventa_obj.search([('id', '=', order_id)]).write({'expediente': expediente_nuevo})               
        return {}

	 
	 
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import date
import subprocess

class ModelViajes(models.Model):
     
     _name = 'jovimer_viajes'
     _description = 'Gestion de Viajes'

     def _compute_serie(self):
        serie = "JXX"
        for rec in self:
            try: 
               serie = ""
               for exps in rec.expedientes:
                   num = exps.name
                   seriee = exps.serie.name
                   serie += str(seriee) + "-" + str(num) + " "
            except: 
               serie = "JX1"
            rec.expedientesseriechar = serie
   
     # Campos Pesonalizados en pedidos de Venta
     expediente = fields.Many2one('jovimer_expedientes', string='Expediente')
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya')
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')
     expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name')
     expedientesseriechar = fields.Char(string="Serie", compute='_compute_serie')
     expedientes = fields.Many2many('jovimer_expedientes', string="Expedientes")
     expedientestxt = fields.Char(string='Expedientes')
     tipoviaje = fields.Selection([
		('NACIONAL','NACIONAL'),('INTERNACIONAL','INTERNACIONAL'),('INTERNACIONALD','INTERNACIONAL DIRECTO')
		],string='Tipo de Viaje')
     fechaformalizado  = fields.Date(string='Fecha Formalizado')
     referencia = fields.Integer(string='Ref Interna')
     name  = fields.Char(string='Número de Orden')
     matricula  = fields.Char(string='Matricula')
     referenciatxt  = fields.Char(string='Referencia')
     contactochofer  = fields.Char(string='Contacto Chófer') 
     temperatura  = fields.Char(string='Temperatura')     
     tempfijoauto  = fields.Char(string='Fijo / Auto')
     tempdoblesimple  = fields.Char(string='Doble/Simpel')
     importe = fields.Float('Importe')
     transportista = fields.Many2one('res.partner', string='Transportista', domain="[('trasnportista','=', True)]")
     paleteur = fields.Float(string='Eur') 
     paletgr = fields.Float(string='Gr') 
     apilables = fields.Char(string='Apilables')     
     combina = fields.Boolean(string='Combina')        
     ctn = fields.Many2many('jovimer_ctn', string='Control Transporte Nacional')
     cti = fields.Many2many('jovimer_cti', string='Control Transporte Internacional')
     ctno2m = fields.One2many('jovimer_ctn', 'orcarga', string='Control Transporte Nacional')
     ctio2m = fields.One2many('jovimer_cti', 'viaje', string='Control Transporte Internacional')
     ordenrecoalma = fields.One2many('jovimer_ordenrecalm', 'viaje', string='Orden Recogida Almacén')
     cmr = fields.Many2many('jovimer_cmr', string='CMR')
     ordencarga = fields.One2many('jovimer_ordencarga', 'viaje', string='Ordenes de Carga')
     observaciones = fields.Text(string='Observaciones')   
     destinointerior = fields.Selection([
		('Plataforma XERESA','Plataforma XERESA'),('Perpignan','Perpignan'),('Barcelona','Barcelona')
		],string='Destino Interior')
     almacenorigen = fields.Many2one('res.partner', string='Almacén Origen', domain="[('name','=ilike', 'JOVIMER')]")
     destinoor = fields.Many2one('res.partner', string='Destino Cliente', domain="[('customer','=', True)]")
     fechallegadanacional = fields.Date(string='Fecha LLegada Nacional')
     fechallegadainternacional  = fields.Date(string='Fecha Llegada Internacional')
     orcargacab  = fields.One2many('jovimer_ordencargacab', 'viajerel', string='Orden Carga Cabecera')
     orcargacabprint  = fields.One2many('jovimer_ordencargacabprint', 'viajerel', string='Impresion Orden de Carga')
     productos = fields.Text(string='Productos')
     preparafactura = fields.Boolean(string='Prep Factura')
     facturado = fields.Boolean(string='Facturado')
     facturarel = fields.Many2one(string='account.invoice')
     resumencabe = fields.One2many('jovimer_viajeresumen', 'viaje', string='Resumen Cliente')
     resumenlin = fields.One2many('jovimer_viajeresumenlin', 'viaje', string='Resumen Lineas')
     grupajes = fields.One2many('jovimer_grupajes', 'name', string='Grupajes')
     proveedores = fields.Text(string='Proveedores')
     linealbcompra = fields.Many2many('account.invoice.line', string='Lineas de Albarán', domain="[('diariofactura','=', 9)]")
     almacenxeresa = fields.Many2many('account.invoice.line', string='Almacen Xeresa')
     nunlinlinealbcompra = fields.Char(string='Num. Lineas')
     nunlinalmacenxeresa = fields.Char(string='Num. Lineas')
     state = fields.Selection([
		('draft','BORRADOR'),
		('online','EN CURSO'),
        ('cancel','ENCANCELADOCURSO'),
        ('done','CERRADO')
		],string='Estado',default='draft')

     @api.onchange('linealbcompra')
     def on_change_nunlinlinealbcompra(self):
        iddoc = self._origin.id
        record_id = 0
        for lines in self.linealbcompra:
             record_id = record_id + 1
        self.nunlinlinealbcompra = str(record_id)

     @api.onchange('almacenxeresa')
     def on_change_nunlinalmacenxeresa(self):
        iddoc = self._origin.id
        record_id = 0
        for lines in self.almacenxeresa:
             record_id = record_id + 1
        self.nunlinalmacenxeresa = str(record_id)

     def jovimer_view_ctn(self, context=None):
        self.ensure_one()
        self.env.cr.execute(""" select id from ir_ui_view where name LIKE '%JOVIMER - Control Transporte Nacional%' and type='tree' ORDER BY id DESC LIMIT 1""")
        result = self.env.cr.fetchone()
        record_id = int(result[0])
        partner = self._ids[0]
        return {
        'name': ("Control Transporte Nacional"),
        'type': 'ir.actions.act_window',
        'res_model': 'jovimer_ctn',
        'view_mode': 'tree',
        'view_type': 'form',
        'view_id': record_id,
        'target': 'current',
        'domain': [('orcarga','=',partner)],
        }
        return {}

     def jovimer_view_cti(self, context=None):
        self.ensure_one()
        ### self.env.cr.execute(""" select id from ir_ui_view where name LIKE '%JOVIMER - Control Transporte Internacional%' and type='tree' ORDER BY id DESC LIMIT 1""")
        ### result = self.env.cr.fetchone()
        ### record_id = int(result[0])
        partner = self._ids[0]
        return {
        'name': ("Control Transporte Internacional"),
        'type': 'ir.actions.act_window',
        'res_model': 'jovimer_cti',
        'view_mode': 'tree,form',
        'view_type': 'form',
        ## 'view_id': record_id,
        'target': 'current',
        'domain': [('viaje','=',partner)],
        }
        return {}

     def action_creacmr(self, default=None):
         id = str(self.id)
         args = ["/opt/jovimer12/bin/actionserver_creacmr.sh", id, "&"]
         subprocess.call(args)
         return {}

     def genera_cmr_alb(self, default=None):
         id = str(self.id)
         args = ["/opt/jovimer12/bin/actionserver_creacmr_desdealb.sh", id, "&"]
         subprocess.call(args)
         return {}


     def action_creaorna(self, default=None):
         id = str(self.id)
         args = ["/opt/jovimer12/bin/actionserver_creaorna.sh", id, "&"]
         subprocess.call(args)
         return {}


     def action_creaorni2(self, default=None):
         id = str(self.id)
         fechallegadanacional = str(self.fechallegadanacional)
         if fechallegadanacional == "False":
             raise AccessError(" Debes colocar Una Fecha de Llegada en el Viaje")
             return {}
         args = ["/opt/jovimer12/bin/actionserver_creaorna2.sh", id]
         subprocess.call(args)
         if self.paleteur > 33:
             raise AccessError(" Atencion EL TOTAL de Palets supera el Limite: " + str(self.paleteur))
         return {} 





     def action_creaorni(self, default=None):
         id = str(self.id)
         args = ["/opt/jovimer12/bin/actionserver_creaorni.sh", id, "&"]
         subprocess.call(args)
         return {}


     def action_creaorni2(self, default=None):
         id = str(self.id)
         fechallegadainternacional = str(self.fechallegadainternacional)
         ## raise AccessError(" Llegada: " + fechallegadainternacional)
         if fechallegadainternacional == "False":
             raise AccessError(" Debes colocar Una Fecha de Llegada en el Viaje")
             return {}
         args = ["/opt/jovimer12/bin/actionserver_creaorni2.sh", id]
         subprocess.call(args)
         if self.paleteur > 33:
             raise AccessError(" Atencion EL TOTAL de Palets supera el Limite: " + str(self.paleteur))
         return {}         
       

     def jovimer_creaviajedesdealb(self, default=None):
         id = str(self.id)
         fechallegadainternacional = str(self.fechallegadainternacional)
         ## raise AccessError(" Llegada: " + fechallegadainternacional)
         if fechallegadainternacional == "False":
             raise AccessError(" Debes colocar Una Fecha de Llegada en el Viaje")
             return {}
         args = ["/opt/jovimer12/bin/actionserver_creaorni_alb.sh", id]
         subprocess.call(args)
         if self.paleteur > 33:
             raise AccessError(" Atencion EL TOTAL de Palets supera el Limite: " + str(self.paleteur))
         return {}   
         

     def jovimer_creaviajedesdealbdef(self, default=None):
         id = str(self.id)
         usuario = self.env.user.id
         if str(usuario) != "31":
             raise AccessError("La generación de Carga Definitiva Se realiza desde el Usuario de Javier Ruiz")
         ## raise AccessError("Eres: " + str(usuario) + ".")
         fechallegadainternacional = str(self.fechallegadainternacional)
         ## raise AccessError(" Llegada: " + fechallegadainternacional)
         if fechallegadainternacional == "False":
             raise AccessError(" Debes colocar Una Fecha de Llegada en el Viaje")
             return {}
         args = ["/opt/jovimer12/bin/actionserver_creaorni_alb_def.sh", id]
         subprocess.call(args)
         if self.paleteur > 33:
             raise AccessError(" Atencion EL TOTAL de Palets supera el Limite: " + str(self.paleteur))
         return {}  



     def action_confirm(self, default=None):
         id = str(self.id)
         args = ["/opt/jovimer12/bin/confirmaviaje.bash", id, "&"]
         subprocess.call(args)
         return {}


     def action_cierra(self, default=None):
         self.write({'state': 'done'})
         return {}

     def action_cancel(self, default=None):
         self.write({'state': 'cancel'})
         return {}

     def action_draft(self, default=None):
         self.write({'state': 'draft'})
         return {}


     @api.onchange('expedientes')
     def on_change_expedientes(self):
      viaje = self.id
      expname=""
      refcliente = ""
      expdescarga = False
      for line in self.expedientes:
        expname += str(line.campanya) + '/' + str(line.name) + " "
        expdescarga = line.dccdescarga.id
        self.env.cr.execute("select refcliente from sale_order where expediente='" + str(line.id) + "' ORDER by id DESC LIMIT 1")
        resultv = self.env.cr.fetchone()
        refcliente = str(resultv[0])
      self.destinoor = expdescarga
      self.referenciatxt = refcliente
      ## self.env.cr.execute(""" update jovimer_viajes set expedientestxt='%s' where id='%s'""" % (expname, viaje))
      ## raise UserError(str(expname))
      return {}



     def cambiadestinos(self):  
         viajeid = self.id
         destinoor = self.destinoor
         lineas = ""
         for lineasalbaranes in self.linealbcompra:
             lineas += str(lineasalbaranes.id) + ","
             lineasalbaranes.plataformadestino = destinoor
         ## raise AccessError("Cambiando los Destinos " + str(lineas) + " del Viaje " + str(viajeid) + "")
         return {}


     def GeneraAlbaranSalida(self):  
       usuario = self.env.user.id
       idviaje = self.id
       albaranes = ""
       expedientes = self.expedientes
       for expediente_id in expedientes:
           expedienteid = expediente_id.id
           serieexp = expediente_id.serie.name
           numeroexp = expediente_id.name
           clienteexp = expediente_id.cliente.id
           clientenameexp = expediente_id.cliente.name
           descarga = self.env['sale.order'].search([('expediente', '=', expedienteid )], order='id desc', limit=1).partner_shipping_id.id
           hoy = date.today()
           lineascarga = self.env['jovimer_ordencarga'].search([('expediente', '=', expedienteid ),('viaje', '=', idviaje ),('tipomov', '=', 'CARGA' )])
           albaranes += str(serieexp) + "-" + str(numeroexp) + " :: " + str(clientenameexp) + " :: " + str(lineascarga) + "\n"
           invoice_obj = self.env['account.invoice']
           invoice = invoice_obj.create({
                      'refcliente': 'PRUEBA PEPE DESDE VIAJES',
                      'date_invoice': hoy,
                      'journal_id': 10,
                      'expediente': expedienteid,
                      'partner_shipping_id': descarga,
                      'partner_id': clienteexp})
           for lineas in lineascarga:
               cuenta = 443
               producto = lineas.producto
               producto_id = lineas.albclin.product_id.id
               plantilla = lineas.albclin.plantilla.id
               variedad = lineas.albclin.variedad.id
               calibre = lineas.albclin.calibre.id
               categoria = lineas.albclin.categoria.id
               confeccion = lineas.albclin.confeccion.id
               envase = lineas.albclin.envase.id
               marca = lineas.albclin.marca.id
               bultos = lineas.albclin.bultos
               cantidadpedido = lineas.albclin.cantidadpedido
               unidadpedido = lineas.albclin.unidadpedido.id
               unidadesporbulto = lineas.albclin.confeccion.unidadesporbulto or 1
               unidabulto = lineas.albclin.unidabulto.id
               unidabulto = 27
               kgnetbulto = lineas.albclin.kgnetbulto
               totalbultos = lineas.totalbultos
               totalkglin = int(totalbultos) * int(kgnetbulto)      
               lineacompracalidadpartner = lineas.albclin.partner_id.id
               cabeceraalbarancompra = lineas.albclin.invoice_id.id
               albaranes += " - LIN: " + str(producto) + "\n"
               lineaventa = lineas.polin.saleorderline.id
               lineaventaud = lineas.polin.saleorderline.unidabulto.id
               if lineaventaud == False or lineaventaud == None:
                   lineaventaud = unidabulto
               if lineaventaud == 1:
                   
                   try: 
                      cantidad = float(totalbultos) * float(unidadesporbulto)
                   except: 
                      raise UserError(str(totalbultos) + " : " + str(unidadesporbulto))
               if lineaventaud == 24:
                   cantidad = totalbultos
               if lineaventaud == 27:
                   cantidad = totalkglin
               invoiceline_obj = self.env['account.invoice.line']
               invoice_line = invoiceline_obj.create({
                              'expediente': expedienteid,
                              'partner_id': clienteexp,
                              'invoice_id': invoice.id,
                              'product_id': producto_id,
                              'name': producto,
                              'plantilla': plantilla,
                              'variedad': variedad,
                              'calibre': calibre,
                              'categoria': categoria,
                              'confeccion': confeccion,
                              'envase': envase,
                              'marca': marca,
                              'bultos': bultos,
                              'cantidadpedido': cantidadpedido,
                              'unidadpedido': unidadpedido,
                              'totalbultos': totalbultos,
                              'unidadesporbulto': unidadesporbulto,
                              'lineaalbarancompra': lineas.albclin.id,
                              'lineacompra': lineas.polin.id,
                              'lineaventa': lineaventa,
                              'lineacompracalidadpartner': lineacompracalidadpartner,
                              'cabeceraalbarancompra': cabeceraalbarancompra,
                              'unidabulto': lineaventaud,
                              'kgnetbulto': kgnetbulto,
                              'totalkglin': totalkglin,
                              'quantity':  cantidad,
                              'price_unit': 0,
                              'account_id': cuenta})
               lineas.albclin.write({'albvtadestino': invoice.id,'albvtadestinolin': invoice_line.id})
       ## raise UserError(str(albaranes))
       return {}

       ### self.env.cr.execute(""" select id from ir_ui_view where name LIKE '%Preparar Albaranes salida%' and type='form' ORDER BY id DESC LIMIT 1""")
       ### result = self.env.cr.fetchone()
       ### record_id = int(result[0])
       ### view = {
       ###    'name': _('Prepara Albaranes de Salida'),
       ###    'view_type': 'form',
       ###    'view_mode': 'tree',
       ###    'res_model': 'jovimer_preparaalbaranessalida',
       ###    'view_id': record_id,
       ###    'type': 'ir.actions.act_window',
       ###    'target': 'current',
       ###    'res_id': False }
       ### return view   





class ModelTranscti(models.Model):
     # Herencia de la tabla de ventas
     _name = 'jovimer_cti'
     _description = 'Control Viajes Internacional'

     sequence = fields.Integer(string='Sequence', default=10)
     expediente = fields.Many2one('jovimer_expedientes', string='Expediente')
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya', store=True)
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')
     expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name')     
     name = fields.Char(string='Ref Cliente') 
     date = fields.Date(string='Fecha') 
     origen = fields.Many2one('res.partner', string='Origen', domain="[('supplier','=', True),('trasnportista','!=', True),('acreedor','!=', True)]")
     partner = fields.Many2one('res.partner', string='Destino', domain="[('customer','=', True)]")
     refcliente = fields.Char(string='Ref Cliente') 
     descripcion = fields.Char(string='Prod.') 
     saleorderline = fields.Many2one('sale.order.line', string='Linea de Venta')
     saleorder = fields.Many2one('sale.order', string='Pedido de Venta', related='saleorderline.order_id', store=True)
     purchaseorderline = fields.Many2one('purchase.order.line', string='Linea de Compra')
     purchaseorder = fields.Many2one('purchase.order', string='Pedido de Compra', related='purchaseorderline.order_id', store=True)
     productomaestro = fields.Many2one('jovimer_productos_maestros', string='Producto Maestro', related='purchaseorderline.product_id.product_tmpl_id.productomaestro', store=True)
     envase = fields.Char(string='Envase') 
     marca = fields.Char(string='Marca') 
     paleteur = fields.Float(string='Eur') 
     paletgr = fields.Float(string='Gr') 
     bultos = fields.Float(string='BxP') 
     totalbultos = fields.Float(string='Bultos') 
     kgnetbulto = fields.Float(string='KgNet', related='purchaseorderline.confeccion.kgnetobulto', store=True, readonly=False)
     confeccion = fields.Many2one(string='Confeccion', related='purchaseorderline.confeccion')
     variedad = fields.Many2one(string='Variedad', related='purchaseorderline.variedad')
     calibre = fields.Many2one(string='Calibre', related='purchaseorderline.calibre')
     categoria = fields.Many2one(string='Calibre', related='purchaseorderline.categoria')
     ordencarga = fields.Many2one('jovimer_ordencarga', string='Orden Carga')
     transportista = fields.Many2one('res.partner', string='Transportista', domain="[('trasnportista','=', True)]", related='viaje.transportista', store=True)
     matricula = fields.Char(string='Matrícula', related='viaje.matricula', store=True) 
     observaciones = fields.Char(string='Obs.') 
     previaje = fields.Boolean('Pte Viaje')
     viaje = fields.Many2one('jovimer_viajes', string='Viaje')
     ## viajeorcab = fields.Many2one('jovimer_viajes', string='Viaje')
     coste = fields.Float(string='Coste') 
     ### destino = fields.Many2one('res.partner', string='Destino', domain="[('customer','=', True)]")
     invoicelinea = fields.Many2one('account.invoice.line', string='Albaran VTA')
     proveedor = fields.Many2one('res.partner', string='Proveedor', domain="[('supplier','=', True)]", related="purchaseorderline.partner_id")
     destino = fields.Many2one('res.partner', string='Cliente', related="expediente.cliente")
     invoicelinef = fields.Many2one('account.invoice.line', string='Factura VTA')
     estado = fields.Selection([
		('BORRADOR','BORRADOR'),('EN CURSO','EN CURSO'),('CERRADA','CERRADA')
		],string='Estado',default='EN CURSO')
     pendiente = fields.Boolean('Pendiente')
     simpledoble = fields.Selection([
		('SIMPLE','SIMPLE'),
		('DOBLE','DOBLE')
		],string='Simple / Doble',default='SIMPLE')
     remontado = fields.Boolean('Remontado')
     llegada = fields.Date(string='Fecha Llegada', related='viaje.fechallegadainternacional', store=True)
     metodo = fields.Char(string='Método') 

class ModelTransctn(models.Model):
     # Herencia de la tabla de ventas
     _name = 'jovimer_ctn'
     _description = 'Control Viajes Nacional'

     def _calc_estado(self, default=None):
         id = str(self.id)
         if self.orcarga:
            self.estado='EN CURSO'
         else:
            self.estado='BORRADOR'
         return {}
     
     sequence = fields.Integer(string='Sequence', default=10)
     expediente = fields.Many2one('jovimer_expedientes', string='Expediente')
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya')
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')
     expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name')
     dia = fields.Char(string='Dia') 
     date = fields.Date(string='Fecha') 
     datecompra = fields.Date(string='Fecha',related='purchaseorderline.fechasalida') 
     name = fields.Char(string='Origen') 
     destino = fields.Many2one('res.partner', string='Destino')
     transportista = fields.Many2one('res.partner', string='Transportista', domain="[('trasnportista','=', True)]", related='orcarga.transportista', store=True)
     proveedor = fields.Many2one('res.partner', string='Proveedor', domain="[('supplier','=', True),('trasnportista','!=', True),('acreedor','!=', True)]")
     paleteur = fields.Float(string='Eur') 
     paletgr = fields.Float(string='Gr')
     paleteurr = fields.Boolean(string='Remontado') 
     paletgrr = fields.Boolean(string='Remontado')
     bultos = fields.Float(string='BxP') 
     totalbultos = fields.Float(string='Bultos')  
     purchaseorderline = fields.Many2one('purchase.order.line', string='Linea de Compra') 
     kgnetbulto = fields.Float(string='KgNet', related='purchaseorderline.confeccion.kgnetobulto', store=True, readonly=False)
     confeccion = fields.Many2one(string='Confeccion', related='purchaseorderline.confeccion')
     variedad = fields.Many2one(string='Variedad', related='purchaseorderline.variedad')
     calibre = fields.Many2one(string='Calibre', related='purchaseorderline.calibre')
     categoria = fields.Many2one(string='Categoria', related='purchaseorderline.categoria')	 
     partner_ref = fields.Char(string='Referecia Proveedor', related='purchaseorderline.order_id.partner_ref')
     estado_compra = fields.Selection([('draft', 'RFQ'),('sent', 'RFQ Sent'),('to approve', 'To Approve'),('purchase', 'Purchase Order'),('done', 'Locked'),('cancel', 'Cancelled')], string='Estado Compra', related='purchaseorderline.order_id.state')
     order_line = fields.One2many('purchase.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
     notes = fields.Text('Terms and Conditions')
     envase = fields.Char(string='Envase') 
     marca = fields.Char(string='Marca') 
     producto = fields.Char(string='Origen') 
     desproducto = fields.Char(string='Producto') 
     ordencarga = fields.Many2one('jovimer_ordencarga', string='Orden Carga')
     almacencarga = fields.Char(string='Almacén de Carga') 
     destinointerior = fields.Selection([
		('Plataforma XERESA','Plataforma XERESA'),('Perpignan','Perpignan'),('Barcelona','Barcelona')
		],string='Destino Interior',default='Plataforma XERESA', related='orcarga.destinointerior', store=True)
     coste = fields.Float(string='Coste') 
     orcarga = fields.Many2one('jovimer_viajes', string='Viaje')
     estado = fields.Selection([
		('BORRADOR','BORRADOR'),('EN CURSO','EN CURSO'),('CERRADA','CERRADA')
		],string='Estado', compute='_calc_estado', store=True)
     simpledoble = fields.Selection([
		('SIMPLE','SIMPLE'),
		('DOBLE','DOBLE')
		],string='Simple / Doble',default='SIMPLE')     
     descripcion = fields.Char(string='Desc') 
     matricula = fields.Char(string='Matrícula') 
     observaciones = fields.Text(string='Obs') 
     partner = fields.Many2one('res.partner', string='Cliente', domain="[('customer','=', True)]")
     pendiente = fields.Boolean('Pendiente')
     previaje = fields.Boolean('Pte Viaje')
     refcliente = fields.Char(string='Ref Cliente') 
     directo = fields.Boolean(string='Directo')     
     remontado = fields.Boolean('R')
     fechallegada = fields.Date(string='Fecha Llegada', related='orcarga.fechallegadanacional', store=True)
     fechacarga = fields.Date(string='Fecha Carga')
     modocarga = fields.Char(string='Modo Carga', help='C - Cargado, A - Automático Sin Plataforma, M - Manual Forzado)')
     cargado = fields.Boolean('C')
     cantidadpedido = fields.Float(string='CP', related='purchaseorderline.cantidadpedido')
     unidadpedido = fields.Many2one(string='UP', related='purchaseorderline.unidadpedido')
     bultospedido = fields.Float(string='BxP', related='purchaseorderline.bultos')

     def action_pasadirecto(self, default=None):
         id = str(self.id)
         args = ["/opt/jovimer12/bin/viajedirecto.bash", id, "&"]
         subprocess.call(args)
         return {}


     def action_cargarlinea(self, default=None):
         from datetime import datetime
         now = datetime.now()
         dt_string = now.strftime("%Y/%m/%d")
         id = str(self.id)
         modocarga="C"
         self.write({'modocarga': str(modocarga)})
         self.write({'fechacarga': dt_string})
         self.write({'cargado': True})
         return {}


     def action_descargalinea(self, default=None):
         self.write({'modocarga': False})
         self.write({'fechacarga': False})
         self.write({'cargado': False})
         return {}


     def action_editar(self, default=None):
           polineid = self.purchaseorderline.id
           return {
           'name': ("Lineas de Compra"),
           'type': 'ir.actions.act_window',
           'res_model': 'purchase.order.line',
           'view_mode': 'form',
           'view_type': 'form',
           'target': 'new',
           'res_id': polineid,
           'context': {'form_view_initial_mode': 'edit','force_detailed_view': 'true'},
           }



class ModelCmr(models.Model):
     # Herencia de la tabla de ventas
     _name = 'jovimer_cmr'
     _description = 'CMR'
     
     name = fields.Char(string='Num CMR') 
     viaje = fields.Many2many('jovimer_viajes', string='Viajes')
     cliente = fields.Many2one('res.partner', string='Cliente')
     codigo = fields.Char(string='Código') 
     destino = fields.Char(string='Destino') 
     origen = fields.Char(string='Origen') 
     serie = fields.Char(string='Serie') 
     transportista = fields.Many2one('res.partner', string='Transportista', domain="[('trasnportista','=', True)]")   
     expediente = fields.Many2one('jovimer_expedientes', string='Expediente', store=True)
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya', store=True)
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')
     expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name', store=True)     
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
     estado = fields.Selection([
		('BORRADOR','BORRADOR'),('EN CURSO','EN CURSO'),('CERRADA','CERRADA')
		],string='Estado',default='EN CURSO')


     @api.onchange('cliente') 
     def on_change_cliente(self):
             resultado = ""
             clienteid = self.cliente.id
             direccion = self.cliente.street
             direccion2 = self.cliente.street2
             city = self.cliente.city
             zip = self.cliente.city
             pais = self.cliente.country_id.name
             resultado = str(direccion) + " " + str(direccion2) + " " + str(city) + "\n" + str(zip) + " - " + str(pais)
             self.txt02 = direccion
             self.txt03 = direccion2

     def creaalbsalida(self):
             raise AccessError("NO Tienes los Permisos para Crear el Albarán de Salida.")
             return{}



class ModelOrdenCargacabprint(models.Model):
     # Herencia de la tabla de ventas
     _name = 'jovimer_ordencargacabprint'
     _description = 'OrdenCarga Cabecera'
     
     _order = "sequence, fechacarga"
     
     def _compute_paletse(self):
         numpalets = 0.0
         for line in self.lineasorden:        
             try:
                numpalets += float(line.totaleuro) or 0.0
             except:
                numpalets += 0			 
         self.totaleuro =  int(numpalets)
     
     def _compute_paletsg(self):
         numpalets = 0.0
         for line in self.lineasorden:        
             numpalets += float(line.totalgrande) or 0.0
         self.totalgran =  int(numpalets)
     
     
     def _compute_bultos(self):
         numbultos = 0.0
         try:
            for line in self.lineasorden:        
                numbultos += float(line.totalbultos) or 0.0
         except:
                numbultos = 0
         self.totalbultos =  int(numbultos)
     
     sequence = fields.Integer(string='Sequence', default=10)
     name = fields.Selection([('CARGA','CARGA'),('DESCARGA','DESCARGA')],string='Tipo de Movimiento')
     origen = fields.Many2one('res.partner', string='Sale desde')
     transportista = fields.Many2one('res.partner', string='Transportista')
     destino = fields.Many2one('res.partner', string='Destino')
     partner = fields.Many2one('res.partner', string='Origen/Destino')
     direccion = fields.Char(string='Direccion') 
     fechacarga = fields.Char(string='Fecha Carga') 
     fechadescarga = fields.Char(string='Fecha Descarga') 
     fecha = fields.Char(string='Fecha')
     totalbultos = fields.Char(string='Total Bultos', compute='_compute_bultos')
     totaleuro = fields.Char(string='Total EuroP', compute='_compute_paletse')
     totalgran = fields.Char(string='Total PaletGR', compute='_compute_paletsg')
     obs = fields.Text(string='Observaciones')
     viajerel = fields.Many2one('jovimer_viajes', string='Viaje')
     lineasorden = fields.Many2many('jovimer_ordencarga', 'ordencargacabe', string='Lineas')




class ModelOrdenCargacab(models.Model):
     # Herencia de la tabla de ventas
     _name = 'jovimer_ordencargacab'
     _description = 'OrdenCarga Cabecera'
     
     _order = "id desc"
     
     name = fields.Many2one('res.partner', string='Transportista')
     direccion = fields.Char(string='Direccion') 
     fechacarga = fields.Char(string='Fecha Carga') 
     fechadescarga = fields.Char(string='Fecha Descarga') 
     fecha = fields.Char(string='Fecha')
     totalbultos = fields.Char(string='Total Bultos')
     totaleuro = fields.Char(string='Total EuroP')
     totalgran = fields.Char(string='Total PaletGR')
     obs = fields.Text(string='Observaciones')
     viajerel = fields.Many2one('jovimer_viajes', string='Viaje')
     lineasorden = fields.One2many('jovimer_ordencarga', 'ordencargacabe', string='Lineas')

class ModelOrdenCarga(models.Model):
     # Herencia de la tabla de ventas
     _name = 'jovimer_ordencarga'
     _description = 'OrdenCarga'
     
     _order = "sequence, fechacarga"
     
     sequence = fields.Integer(string='Sequence', default=10)
     name = fields.Selection([('CARGA','CARGA'),('DESCARGA','DESCARGA')],string='Tipo de Movimiento')
     plataforma = fields.Many2one('res.partner', string='Plataforma') 
     partner = fields.Many2one('res.partner', string='Entidad') 
     direccion = fields.Char(string='Direccion') 
     fechacarga = fields.Char(string='Fecha Carga') 
     fechadescarga = fields.Char(string='Fecha Descarga') 
     fechahasta = fields.Char(string='Fecha Hasta') 
     expediente = fields.Many2one('jovimer_expedientes', string='Expediente', store=True)
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya', store=True)
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')
     expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name', store=True)   
     matricula = fields.Char(string='Matrícula')
     importe = fields.Char(string='Importe')
     temp = fields.Char(string='Temperatura') 
     phone = fields.Char(string='Teléfono') 
     viaje = fields.Many2one('jovimer_viajes', string='Viaje')
     ctn = fields.One2many('jovimer_ctn', 'ordencarga', string='Control Transporte Nacional')
     cti = fields.One2many('jovimer_ctn', 'ordencarga', string='Control Transporte Internacional')
     ctilin = fields.Many2one('jovimer_cti', string='CTI')
     ctnlin = fields.Many2one('jovimer_ctn', string='CTN')
     albclin = fields.Many2one('account.invoice.line', string='Linea Alb Compra')
     expediente_origen = fields.Integer(string='Número', help='Número Expediente', related='albclin.invoice_id.expediente.name')
     polin = fields.Many2one('purchase.order.line', string='Linea Compra')
     ## confeccion = fields.Many2one(string='Confeccion', related='cti.confeccion')
     ## variedad = fields.Many2one(string='Variedad', related='cti.purchaseorderline.variedad')
     ## calibre = fields.Many2one(string='Calibre', related='cti.purchaseorderline.calibre')
     ## categoria = fields.Many2one(string='Calibre', related='cti.purchaseorderline.categoria')	
     tipoviaje = fields.Selection([
		('NACIONAL','NACIONAL'),('INTERNACIONAL','INTERNACIONAL')
		],string='Tipo de Viaje', related='viaje.tipoviaje')
     producto = fields.Char(string='Producto')
     tipomov = fields.Char(string='Tipo Movimiento')
     totaleuro = fields.Char(string='EuroPalets') 
     totalgrande = fields.Char(string='Palet Grande')
     destinointerior = fields.Char(string='Destino Interior')     
     bultos = fields.Char(string='Bultos')
     totalbultos = fields.Char(string='Total Bultos')
     ordencargacabe = fields.Many2one('jovimer_ordencargacab', string='Orden de Carga')
     remontado = fields.Char(string=' ')
     paletsenref = fields.Char(string='Palet x J')
     estado = fields.Selection([
		('BORRADOR','BORRADOR'),('EN CURSO','EN CURSO'),('CERRADA','CERRADA')
		],string='Estado',default='EN CURSO')	 
	 
class ModelOrdenrecogidaalmacen(models.Model):
     # Herencia de la tabla de ventas
     _name = 'jovimer_ordenrecalm'
     _description = 'Orden Recogida Almacén'
     
     sequence = fields.Integer(string='Sequence', default=10)
     name = fields.Many2one('res.partner', string='Plataforma') 
     transportista = fields.Many2one('res.partner', string='Transportista')
     matricula = fields.Char(string='Direccion') 
     fechasalida = fields.Char(string='Fecha Salida') 
     viaje = fields.Many2one('jovimer_viajes', string='Viaje')
     ordencarga = fields.One2many('jovimer_ordenrecalmlin', 'ordencarga', string='Lineas de Carga')

class ModelOrdenrecogidaalmacenlin(models.Model):
     # Herencia de la tabla de ventas
     _name = 'jovimer_ordenrecalmlin'
     _description = 'Orden Recogida Almacén Líneas'
     
     sequence = fields.Integer(string='Sequence', default=10)
     name = fields.Char(string='Productos')
     palets = fields.Char(string='Palets') 
     tipo = fields.Char(string='Tipo Palets')
     bultos	 = fields.Char(string='BxP') 
     totalbultos = fields.Char(string='Total Bultos')
     expediente = fields.Many2one('jovimer_expedientes', string='Expediente', store=True)
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya', store=True)
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')
     expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name', store=True)   
     proveedor = fields.Many2one('res.partner', string='Proveedor')   
     platdes = fields.Many2one('res.partner', string='Plataforma Destino')
     ordencarga = fields.Many2one('jovimer_ordenrecalm', string='Orden')


class ModelResumenViajeLinea(models.Model):
     # Herencia de la tabla de ventas
     _name = 'jovimer_viajeresumen'
     _description = 'Resumen Viaje'
     
     sequence = fields.Integer(string='Sequence', default=10)
     name = fields.Many2one('res.partner', string='Cliente') 
     viaje = fields.Many2one('jovimer_viajes', string='Viaje')
     euro = fields.Char(string='Eur') 
     gran = fields.Char(string='Gran')
     bultos	 = fields.Char(string='Bultos') 
     expediente = fields.Many2one('jovimer_expedientes', string='Expediente', store=True)
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya', store=True)
     expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name', store=True)   
     resumenlineas = fields.One2many('jovimer_viajeresumenlin', 'resumenid', string='Lineas')   
     obs = fields.Char(string='Observaciones')
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')


class ModelResumenViajeLinea(models.Model):
     # Herencia de la tabla de ventas
     _name = 'jovimer_viajeresumenlin'
     _description = 'Resumen Viaje Lineas'
     
     sequence = fields.Integer(string='Sequence', default=10)
     name = fields.Char(string='Productos')
     euro = fields.Char(string='Eur') 
     gran = fields.Char(string='Gran')
     bultos	 = fields.Char(string='Total Bultos') 	 
     bultosxp = fields.Char(string='Bultos / Palet') 
     expediente = fields.Many2one('jovimer_expedientes', string='Expediente', store=True)
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya')
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')
     expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name')   
     proveedor = fields.Many2one('res.partner', string='Proveedor')   
     lineacompra = fields.Many2one('purchase.order.line', string='Linea Compra')
     confeccion = fields.Char(string='Confección') 
     envase = fields.Char(string='Envase') 
     viaje = fields.Many2one('jovimer_viajes', string='Viaje')
     resumenid = fields.Many2one('jovimer_viajeresumen', string='Viaje')
     obs = fields.Char(string='Observaciones')	 




class ModelWizardGrupaje(models.Model):
     # Herencia de la tabla de ventas
     _name = 'jovimer_preparagrupaje'
     _description = 'Prepara Grupaje de Viajes'

     name = fields.Char(string='Grupaje')
     fecha = fields.Date(string='Fecha')



class ModelGrupajesViaje(models.Model):
     _name = 'jovimer_grupajeviajes'
     _description = 'Grupajes en Viajes'	 


     name = fields.Char(string='Grupaje')
     fecha = fields.Date(string='Fecha')
     viajes = fields.Many2many('jovimer_viajes', string='Expedientes y Palets') 
     obs = fields.Text(string='Observaciones')






class ModelGrupajesViaje(models.Model):
     # Herencia de la tabla de ventas
     _name = 'jovimer_grupajes'
     _description = 'Grupajes'
     
     sequence = fields.Integer(string='Sequence', default=10)
     name = fields.Many2one('jovimer_viajes', string='Viaje')
     expypalets = fields.Text(string='Expedientes y Palets') 
     productosypalets = fields.Text(string='Productos y Palets')	 
     preciouni = fields.Char(string='Precio / Palet')
     precioporexp = fields.Text(string='Precio Por Exp') 
	 
	 
	 
class ModelAlbaranesViaje(models.Model):
     # Herencia de la tabla de ventas
     _name = 'jovimer_preparaalbaranessalida'
     _description = 'Prepara Albaranes Salida'
     
     name = fields.Many2one('res.partner', string='Cliente')
     viaje = fields.Many2one('jovimer_viajes', string='Viaje')
     expediente = fields.Many2one('jovimer_expedientes', string='Expediente', store=True)
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya', store=True)
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie', store=True)
     expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name', store=True)    	 
	 


class ModelWizardCarga(models.Model):
     # Herencia de la tabla de ventas
     _name = 'jovimer_preparaentrada'
     _description = 'Prepara Entrada'
     
     name = fields.Many2one('account.invoice.line', string='Linea de Albarán')
     albaran = fields.Many2one('account.invoice', string='Albarán de Compra', related='name.invoice_id')
     variedad = fields.Many2one('jovimer_variedad', string='Variedad', related='name.variedad')
     calibre = fields.Many2one('jovimer_calibre', string='Calibre', related='name.calibre')
     categoria = fields.Many2one('jovimer_categoria', string='Categoria', related='name.categoria')
     confeccion = fields.Many2one('jovimer_confeccion', string='Confección', related='name.confeccion')
     envase = fields.Many2one('jovimer_envase', string='Envase' , related='name.envase')
     totalbultos = fields.Float(string='Total Bultos', related='name.totalbultos')
     totalbultosentrada = fields.Float(string='Total Entrada')
     lineas = fields.Many2many('account.invoice.line', string='Linea de Asignación')
     
	 
     ## expediente = fields.Many2one('jovimer_expedientes', string='Expediente', store=True)
     ## expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya', store=True)
     ## expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie', store=True)
     ## expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name', store=True)    	 
	 

	 
    
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import datetime
import subprocess

class ModelExpedientes(models.Model):
     # Herencia de la tabla de ventas
     _name = 'jovimer_expedientes'
     _description = 'Expedientes'
     _order = "name asc"
     ### _rec_name = 'serieynum'
     # Añadir el estado Pedido a ventas
     
     
     cliente  = fields.Many2one('res.partner', string='Cliente', related='pedvta.partner_id')
     dccdescarga  = fields.Many2one('res.partner', string='Direccion Descarga', related='pedvta.partner_shipping_id')
     fechasalida  = fields.Date(string='Fecha de Salida', related='pedvta.fechasalida')
     fechallegada = fields.Date(string='Fecha de Llegada', related='pedvta.fechallegada')
     horallegada  = fields.Char(string='Hora de Llegada', help='Permite caracteres Alfanuméricos')
     matricula  = fields.Char(string='Matrícula', help='Permite varias')
     transporteinternacional = fields.Many2one('res.partner', string='Transporte Internacional')
     transporteinterior = fields.Many2one('res.partner', string='Transporte Nacional')
     preciotransporteinternacional = fields.Float(string='Precio Transporte Internacional')
     preciotransporteinterior = fields.Float(string='Precio Transporte Nacional')
     abono = fields.Text(string='Abono')
     cpedidos = fields.Boolean(string='Pedidos')
     clogistica = fields.Boolean(string='Logística')
     cfacturacion = fields.Boolean(string='Facturación')
     cliquidaciones = fields.Boolean(string='Liquidaciones')
     ccuentadeventas = fields.Boolean(string='Cuenta de Ventas')
     csalidas = fields.Boolean(string='Salidas')
     nobio = fields.Boolean(string='NO BIO')
     observaciones = fields.Text(string='Observaciones')
     ## state
     ## partecoste
     ## coste
     ## resultado
     ## resultadoestimado
     name = fields.Integer(string='Número', help='Número Expediente')
     numint = fields.Integer(string='Número Anterior', help='Número Expediente')
     serie = fields.Many2one('jovimer_expedientes.series', string='Serie')
     campanyachar = fields.Char('Serie Char')
     serieynum = fields.Char('Expediente', compute='_compute_fields_combination')
     campanya = fields.Selection([
		('J22','J22'),
		('J20','J20'),
		('PR20','PR20'),
		('CO20','CO20'),
		('J21','J21'),
		('PR21','PR21'),
		('CO21','CO21'),
		],string='Campaña',default='J22')
     ## proveedores = fields.Many2many(string='res.partner', help='Proveedore Asociados')
     importado = fields.Boolean(string='Importado')
     
     pedvta = fields.One2many('sale.order', 'expediente', string='Pedidos venta')
     pedcompra = fields.One2many('purchase.order', 'expediente', string='Pedidos venta')
     facturacionv = fields.One2many('account.invoice', 'expediente', string='Facturas Venta')
     lineascomrpa = fields.One2many('account.invoice.line', 'expediente', string='Facturas Compra', domain=[('typefact','=','in_invoice')])
     viajes = fields.One2many('jovimer_viajes', 'expediente', string='Viajes')
     ctn = fields.One2many('jovimer_ctn', 'expediente', string='Control Trans Nacional')
     cti = fields.One2many('jovimer_cti', 'expediente', string='Control Trans Internacional')
     reclamaciones = fields.One2many('jovimer_reclamaciones', 'expediente', string='Etiquetas')     
     etiquetas = fields.One2many('jovimer_etiquetas', 'expediente', string='Etiquetas')     
     pedidocerrado = fields.Boolean(string='Pedido Cerrado', related='pedvta.pedidocerrado')
     


     
     ### _sql_constraints = [('name', 'unique(name)', 'Ya existe un Expediente con ese Número. No puedes Ducplicarlo')]
     
     @api.depends('serie', 'name')
     def _compute_fields_combination(self):
        for test in self:
            test.serieynum = test.serie.name + '-' + str(test.name)

     
     @api.model
     def create(self, vals):
        serie = self.campanya
        numero = self.name
        vals['cliente'] = 3495
        result = super(ModelExpedientes, self).create(vals)
        ### raise UserError("CReando...." + str(serie) + "/" + str(numero) + "")
        return result
	 

class ModelExpedientesSeries(models.Model):
     # Herencia de la tabla de ventas
     _name = 'jovimer_expedientes.series'
     _description = 'Expedientes Series'
     _order = "name asc"

     name = fields.Char(string='Nombre', help='Nombre Serie')
     partner_id  = fields.Many2one('res.partner', string='Cliente', help='Cliente Por defecto')


     
class ModelSaleOrder(models.Model):
     
     # Herencia de la tabla de ventas
     _inherit = 'sale.order'
     
     

     # Campos Pesonalizados en pedidos de Venta
     fechasalida  = fields.Date(string='Fecha de Salida')
     fechallegada = fields.Date(string='Fecha de Llegada')
     horallegada  = fields.Char(string='Hora de Llegada', help='Permite caracteres Alfanuméricos')
     campanya = fields.Char(string='Serie / Campaña', help='Número Expediente')
     expediente = fields.Many2one('jovimer_expedientes', string='Expediente')
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya')
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')
     expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name')




class pedidoCompraasigna(models.Model):
    # Herencia de la tabla de ventas

    _name = 'jovimer_asignaciones'

    name = fields.Char(string='Nombre Asignacion')
    purchaseorderline = fields.Many2one('purchase.order.line', string="Linea Compra Origen", limit=1)
    saleorderlinedestino = fields.Many2one('sale.order.line', string="Linea Venta Destino", limit=1)
    purchaseorder = fields.Many2one('purchase.order', string="Compra Origen", related='purchaseorderline.order_id')
    saleorderdestino = fields.Many2one('sale.order', string="Venta Destino", related='saleorderlinedestino.order_id')
    cantidadasignada = fields.Float(string="Cantidad Asignada", related='purchaseorderline.cantidadasignada')
    libreasignada = fields.Float(string="Cantidad Asignada", related='purchaseorderline.libreasignada')
    expedienteorigen = fields.Many2one('jovimer_expedientes', string="Expediente Origen", related='purchaseorderline.expediente')
    expedientedestino = fields.Many2one('jovimer_expedientes', string="Expediente Destino", related='saleorderlinedestino.expediente')
    ## viaje = fields.Many2one('jovimer_viajes', string="Expediente Destino", related='purchaseorderline.expediente')
    fechaoperacion = fields.Date(string="Fecha Operacion")
    lineavtacompra = fields.Many2one('jovimer_lineascompra', string="Linea Asignada Venta")
    cantidad = fields.Float(string="Cantidad Asignada") 
    unidad = fields.Many2one('uom.uom', string='Ud', domain=[('invisibleasig','=','SI')]) 
    realizado = fields.Boolean(string="Realizado")

    def generaasignacion(self, default=None):
          ## self.write({'statusrecla': 'RECLAMADA'})
          id = str(self.id)
          args = ["/opt/jovimer12/bin/crearasignaciones.bash", id, "&"]
          subprocess.call(args)
          return {}  

class ModelReclamaciones(models.Model):
     
     # Tabla Reclamaciones
     _name = 'jovimer_reclamaciones'
     _description = 'Asignaciones Jovimer'
 
     # Campos Pesonalizados en pedidos de Venta
     name = fields.Char(string='Codigo Reclamacion')
     asunto = fields.Char(string='Tema Reclamacion')
     fechasaalta  = fields.Date(string='Fecha de Alta')
     fechabaja = fields.Date(string='Fecha de Baja')
     campanya = fields.Char(string='Serie / Campaña', help='Número Expediente')
     expediente = fields.Many2one('jovimer_expedientes', string='Expediente')
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya')
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')
     expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name')
     cliente  = fields.Many2one('res.partner', string='Quien Reclama')
     lineaspedido  = fields.Many2many('sale.order', string='Documentos de Venta Afectados')
     detalledocumentos  = fields.Many2many('sale.order.line', string='Lineas de Documentos Afectadas')
     detalledocumentoscompra  = fields.Many2many('purchase.order.line', string='Lineas de Documentos de Compra Afectados')
     detalledocumentoscontables  = fields.Many2many('account.invoice.line', string='Lineas de Documentos Contables Afectados')	 
     observacionescliente  = fields.Text(string='Observaciones Cliente')
     observacionescliente  = fields.Text(string='Observaciones Cliente')
     imagenes  = fields.One2many('jovimer_imagenes_reclamaciones','reclamacion', string='Imágenes Reclacionadas')
     accionescorrectivas  = fields.Text(string='Acciones Correctivas')
     status = fields.Selection([
		('ABIERTA','ABIERTA'),
		('EN CURSO','EN CURSO'),
		('CERRADA','CERRADA'),
		('CANCELADA','CANCELADA'),
		('DESESTIMADA','DESESTIMADA'),		
		],string='Estado',default='ABIERTA')


class ModelReclamacionesImagenes(models.Model):
     
     # Tabla Reclamaciones
     _name = 'jovimer_imagenes_reclamaciones'
     
     # Campos Pesonalizados en pedidos de Venta
     name = fields.Char(string='Codigo Reclamacion')
     imagen = fields.Binary(string='Imagen Reclamacion')	 
     reclamacion = fields.Many2one('jovimer_reclamaciones', string='Reclamación') 
	 
	 

class ModelUom(models.Model):
     
     _inherit = 'uom.uom'

     # Campos 
     invisible  = fields.Selection([
		('SI','SI'),
		('NO','NO')],string='Invisible',default='NO')
     invisiblecp  = fields.Selection([
		('SI','SI'),
		('NO','NO')],string='Cantidad Palets',default='NO')
     invisibleudvta  = fields.Selection([
		('SI','SI'),
		('NO','NO')],string='Unidad de Venta',default='NO')
     invisibleasig  = fields.Selection([
		('SI','SI'),
		('NO','NO')],string='Unidad Asignacion',default='NO')
     nameeng = fields.Char(string='Eng Name')
     pesobruto = fields.Float(string='Peso Bruto')


class ModelConfLOte(models.Model):
     
     _name = 'jovimer_conflote'
     _description = 'Conforma Lote'

     # Campos 
     name  = fields.Char(string='Nombre')
     codigo = fields.Char(string='Código')
     formula = fields.Char(string='Formula')


class ModelCalibre(models.Model):
     
     _name = 'jovimer_calibre'
     _description = 'Calibres'

     # Campos 
     name  = fields.Char(string='Nombre')
     codigo = fields.Char(string='Código')
     abrev = fields.Char(string='abrev')
     importa = fields.Char(string='Impresion')
     importado = fields.Boolean(string='Importado Velneo')

class ModelCategoria(models.Model):
     
     _name = 'jovimer_categoria'
     _description = 'Categorias'

     # Campos 
     name  = fields.Char(string='Nombre')
     codigo = fields.Char(string='Código')
     abrev = fields.Char(string='abrev')
     importa = fields.Char(string='Impresion')
     importado = fields.Boolean(string='Importado Velneo')     

class ModelEnvase(models.Model):
     
     _name = 'jovimer_envase'
     _description = 'Envases'

     # Campos 
     name  = fields.Char(string='Nombre')
     codigo = fields.Char(string='Código')
     abrev = fields.Char(string='abrev')
     importa = fields.Char(string='Impresión')
     importado = fields.Boolean(string='Importado Velneo')    
     pesobruto = fields.Float(string='Peso Bruto')


class ModelMarca(models.Model):
     
     _name = 'jovimer_marca'
     _description = 'Marcas'

     # Campos 
     name  = fields.Char(string='Nombre')
     codigo = fields.Char(string='Código')
     abrev = fields.Char(string='abrev')
     importa = fields.Char(string='Impresión')
     importado = fields.Boolean(string='Importado Velneo')      
     
class ModelVariedad(models.Model):
     
     _name = 'jovimer_variedad'
     _description = 'Variedades'

     # Campos 
     name  = fields.Char(string='Nombre')
     producto  = fields.Many2one('product.product', string='Producto')
     codigo = fields.Char(string='Código')
     abrev = fields.Char(string='Trad Ingles')
     importa = fields.Char(string='Impresión')
     importado = fields.Boolean(string='Importado Velneo')  

class ModelConfeccion(models.Model):
     
     _name = 'jovimer_confeccion'
     _description = 'Confecciones'

     # Campos 
     name  = fields.Char(string='Nombre')
     codigo = fields.Char(string='Código')
     abrev = fields.Char(string='abrev')
     importa = fields.Char(string='Nombre Importado')
     importado = fields.Boolean(string='Importado Velneo')  
     bultoseuropalet = fields.Float(string='Bultos Euro Palet')  
     bultosgrandpalet = fields.Float(string='Bultos Palet Grande') 
     kgnetobulto = fields.Float(string='KG/NET Bulto') 
     unidadesporbulto = fields.Float(string='Unidad por Bulto')
     nombreimpresion = fields.Char(string='Impresion') 
     tara = fields.Float(string='Tara') 
     unidabulto = fields.Many2one('uom.uom', string='Tipo Cálculo / Ud Venta', domain=[('invisible','=','NO')])
     plantilla = fields.One2many('jovimer_plantillaproductos', 'confeccion', string='Plantillas Afectadas')

     ### 
     ### @api.onchange('bultoseuropalet','bultosgranpalet')
     ### def _compute_bultos(self):
     ###         self.plantilla.bultos = self.bultoseuropalet
     ###         return {}


class ModelPlantillaProductos(models.Model):
     
     _name = 'jovimer_plantillaproductos'
     _description = 'Plantillas de Producto'

     # Campos 
     variedad = fields.Many2one('jovimer_variedad', string='Variedad')
     codproducto = fields.Char(string='Codigo Cliente')
     calibre = fields.Many2one('jovimer_calibre', string='Calibre')
     categoria = fields.Many2one('jovimer_categoria', string='Categoria')
     confeccion = fields.Many2one('jovimer_confeccion', string='Confección')
     envase = fields.Many2one('jovimer_envase', string='Envase')
     marca = fields.Many2one('jovimer_marca', string='Marca')
     name  = fields.Char(string='Nombre')
     nocalcbultos = fields.Boolean(string='No Calcula Bultos')
     bultos = fields.Float(string='Bultos') 
     kgnetobulto = fields.Float(string='KG/NET Confección') 
     partner = fields.Many2one('res.partner', string='Cliente')
     ## plantillaeti
     product = fields.Many2one('product.product', string='Producto')
     pvpcoste = fields.Float(string='Coste') 
     pvptipo = fields.Many2one('uom.uom', string='PVP/Tipo', domain=[('invisible','=','NO')])
     pvptrans = fields.Float(string='Transporte') 
     pvpvta = fields.Float(string='Venta') 
     tipouom = fields.Many2one('uom.uom', string='Tipo Medida', domain=[('invisible','=','NO')])
     udfacturacion = fields.Many2one('uom.uom', string='Ud Albaran/Factura', domain=[('invisibleudvta','=','SI')])
     plantillaetiquetas = fields.Many2one('jovimer_etiquetas_plantilla', string='P. Etiquetas')     
     precio_semana = fields.Integer( string='Semana', help='Semana a la que se aplica el precio atendiendo a la fecha de llegada del Pedido')
     invoiceline = fields.Many2one('account.invoice.line', string='Lin ALB/FACT')     
     saleline = fields.Many2one('sale.order.line', string='Lin Pedido')     
     invoiceid = fields.Many2one('account.invoice', string='ALB/FACT')     
     saleid = fields.Many2one('sale.order', string='Pedido')  
     semana = fields.Char(string='Semana')
     noactivo = fields.Boolean(string='NO Activo')
	 
     @api.onchange('confeccion.bultoseuropalet')
     def _compute_bultoseuropalet(self):
             self.bultos = self.confeccion.bultoseuropalet
             return {}

     @api.onchange('confeccion.bultosgrandpalet')
     def _compute_bultosbultosgrandpalet(self):
             self.bultos = self.confeccion.bultosgrandpalet
             return {}

     @api.onchange('confeccion.kgnetobulto')
     def _compute_kgnetobulto(self):
             self.kgnetobulto = self.confeccion.kgnetobulto
             return {}

             

     def calcula_bultos(self):
            
             nocalculabultos = self.nocalcbultos
             if nocalculabultos == True:
              return{}
             else:
              self.bultos = self.confeccion.bultoseuropalet
              return {}


class Modeltraspasocontacobrosypagos(models.Model):
      
     _name = 'jovimer_traspasocyp'
     _description = 'Traspaso Contabilidad Cobros y Pagos'


     # Campos 
     name  = fields.Char(string='Nombre')
     fecha = fields.Date(string='Fecha Traspaso')
     pagos = fields.Many2many("account.payment", string="Pagos Asociados")
     generadiario = fields.Boolean(string='Libro Diario')
     tipotraspaso = fields.Char(string='Tipo Traspaso')

     def creatrasoasocontable(self,context=None):
        hoy = datetime.today()
        traspasoid = self.id
        namecont = "Traspaso Contable: " + str(hoy) + "."
        self.write({'fecha': hoy,'name': str(namecont),'tipotraspaso': 'PAGOS','generadiario': True})        
        id = str(self.id)
        args = ["/opt/jovimer12/bin/creatraspasologocontapagos.sh", id, "&"]
        subprocess.call(args)
        return True


class Modeltraspasoconta(models.Model):
      
     _name = 'jovimer_traspasoconta'
     _description = 'Traspaso Contabilidad'


     # Campos 
     name  = fields.Char(string='Nombre')
     fecha = fields.Date(string='Fecha Traspaso')
     facturas = fields.Many2many("account.invoice", string="Facturas Afectadas")
     generaiva = fields.Boolean(string='Libro de Iva')
     generadiario = fields.Boolean(string='Libro Diario')
     tipotraspaso = fields.Char(string='Tipo Traspaso')
 



     def abrirfacturas(self, context=None):
        self.ensure_one()
        self.env.cr.execute(""" select id from ir_ui_view where name LIKE '%Jovimer - Facturas Proveedor%' and type='tree' ORDER BY id DESC LIMIT 1""")
        result = self.env.cr.fetchone()
        record_id = int(result[0])
        partner = self._ids[0]
        return {
        'name': ("Facturas Relacionadas"),
        'type': 'ir.actions.act_window',
        'res_model': 'account.invoice',
        'view_mode': 'tree,form',
        'view_type': 'form',
        ## 'view_id': record_id,
        'target': 'current',
        'domain': [('traspasoid','=',self.id)],
        }
        return {}



     def creatrasoasocontable(self,context=None):
        hoy = datetime.today()
        traspasoid = self.id
        self.env.cr.execute(""" select count(*) from account_invoice where journal_id in (1,10) and id in (select account_invoice_id from account_invoice_jovimer_traspasoconta_rel where jovimer_traspasoconta_id='%s') """ % (traspasoid))
        result = self.env.cr.fetchone()
        contador = int(result[0])
        if int(contador) > 0:
            raise UserError("Existe Algun diario NO permitido en el Traspaso")
        for x in self.facturas:
            linea = x.relpartnerfiscal
            nameparter = x.partner_id.name
            ### raise UserError("Eres: " + str(linea) + ".")
            if str(linea) == "False":
                raise UserError("No Existe Nombre Fiscal en alguna linea: " + str(nameparter) + ".")
                return
        for s in self.facturas:
            lineap = s.relpartnercta
            nameparter = s.partner_id.name
            ## raise UserError("Eres: " + str(lineap) + ".")
            if str(lineap) == "False":
                raise UserError("No Existe Cuentas Contables de Venta en allguna linea: " + str(nameparter) + ".")
                return		
        namecont = "Traspaso Contable: " + str(hoy) + "."
        self.write({'fecha': hoy})        
        self.write({'name': str(namecont)})
        self.write({'tipotraspaso': 'EMITIDAS'}) 
        self.write({'generaiva': True})        
        self.write({'generadiario': True})                
        id = str(self.id)
        args = ["/opt/jovimer12/bin/creatraspasologoconta.sh", id, "&"]
        subprocess.call(args)
        return True 

     def creatrasoasocontablec(self,context=None):
        hoy = datetime.today()
        traspasoid = self.id
        traspasoidstr = str(traspasoid)
        self.env.cr.execute(""" select count(*) from account_invoice where journal_id in (2,9) and id in (select account_invoice_id from account_invoice_jovimer_traspasoconta_rel where jovimer_traspasoconta_id='%s') """ % (traspasoid))
        result = self.env.cr.fetchone()
        contador = int(result[0])
        if int(contador) > 0:
            raise UserError("Existe Algun diario NO permitido en el Traspaso")

        for x in self.facturas:
            numfact = x.reference
            namepartner = x.partner_id.name
            amotax = x.amount_tax
            if str(x.modologocontamercasp) == "True" and str(amotax) != "0.0":
                        raise UserError ("En Mercancia con Sujeto Pasivo hay Facturas de " + str(namepartner) + " con importe de iva diferente a 0. Debes revisarlas")
                        return
            if str(x.modologocontamercain) == "True" and str(amotax) != "0.0":
                        raise UserError ("En Mercancia Intracomunitaria hay Facturas de " + str(namepartner) + " con importe de iva diferente a 0. Debes revisarlas")
                        return



        for x in self.facturas:
            linea = x.relpartnerfiscal
            nameparter = x.partner_id.name
            ### raise UserError("Eres: " + str(linea) + ".")
            if str(linea) == "False":
                raise UserError("No Existe Nombre Fiscal en alguna linea: " + str(nameparter) + ".")
                return
        for s in self.facturas:
            lineap = s.relpartnerctap
            nameparter = s.partner_id.name
            ## raise UserError("Eres: " + str(lineap) + ".")
            if str(lineap) == "False":
                raise UserError("No Existe Cuentas Contables de Compra en allguna linea: " + str(nameparter) + ".")
                return
        for t in self.facturas:
            lineat = t.traspasocontfecha
            traspasoidfact = t.traspasoid
            numberfact = t.number
            ### raise UserError("Eres: " + str(lineat) + ".")
            ### if str(lineat) != "False" and str(traspasoidfact) != traspasoidstr:
            ###     raise UserError("La Factura Figura como Traspasada: " + str(numberfact) + ". Debes desmarcarla primero.")
            ###     return


        namecont = "Traspaso Contable: " + str(hoy) + "."
        ## self.write({'fecha': hoy})        
        self.write({'name': str(namecont),'tipotraspaso': 'RECIBIDAS','generaiva': True,'generadiario': True})                
        id = str(self.id)
        args = ["/opt/jovimer12/bin/creatraspasologoconta_compra.sh", id, "&"]
        subprocess.call(args)
        return True 


 
class Modelinstrastat(models.Model):
      
     _name = 'jovimer_intrastat'
     _description = 'Instratstat'


     # Campos 
     name  = fields.Char(string='Descripcion')
     tipomov = fields.Char(string='Tipo Mov')
     producto = fields.Many2many("account.invoice", string="Facturas Afectadas")
     kilos = fields.Float(string='Kilos')
     preciomedio = fields.Float(string='Precio Medio')
     total = fields.Float(string='Total')
     fechaini = fields.Date(string='Fecha Inicial')
     fechafin = fields.Date(string='Fecha Final')
     estado = fields.Char(string='Estado')	 



     def creaintrastat(self,context=None):
         fechaini=self.fechaini
         fechafin=self.fechafin
         if str(fechaini) == "None" or  str(fechafin) == "None":
            self.write({'estado': 'ERROR: Alguna Fecha no esta establecida'}) 
            return {}
         if fechaini >= fechafin:
            self.write({'estado': 'ERROR: La Fecha de fin  no puede ser mayor que la Fecha de Inicio'}) 
            return {}
         self.write({'estado': 'Iniciando'}) 
         objects = str(fechaini) + "," + str(fechafin)
         args = ["/opt/jovimer12/bin/calculaintrastat.sh", str(objects)]
         ## raise UserError("Voy a Ejecutar: " + str(args) + "")
         subprocess.call(args) 
         self.write({'estado': 'Iniciando'}) 
         return {}


class ModelProductos(models.Model):
      
     _inherit = 'product.template'


     # Campos 
     productomaestro  = fields.Many2one('jovimer_productos_maestros', string='Producto Maestro')


class ModelProductMaestro(models.Model):
      
     _name = 'jovimer_productos_maestros_pyp'
     _description = 'Productos Maestros'

     def _calcula_desvio(self):
        for rec in self:
            desviob = False
            prediomedioventa = rec.prediomedioventa or 0
            prediomedioventag = rec.prediomedioventag or 0
            if prediomedioventag != 0:
               desvio = ( prediomedioventa * 100 ) / prediomedioventag
               if desvio < 10:
                  desviob = True
            rec.desvio = desviob


     # Campos 
     name  = fields.Many2one('res.country', string='Pais')
     periodo = fields.Char(string='Periodo')
     prediomediocompra = fields.Float(string='PVP Medio Compra')
     prediomedioventa = fields.Float(string='PVP Medio Venta')
     productomaestro = fields.Many2one('jovimer_productos_maestros', string='Producto Maestro')
     prediomedioventag = fields.Float(string='PVP Medio Venta Global')
     desvio = fields.Boolean(string='Desvio', compute='_calcula_desvio')



class ModelProductMaestro(models.Model):
      
     _name = 'jovimer_productos_maestros'
     _description = 'Productos Maestros'


     # Campos 
     name  = fields.Char(string='Nombre')
     prediomediocompra = fields.Float(string='PVP Medio Compra')
     prediomedioventa = fields.Float(string='PVP Medio Venta')
     productobio = fields.Boolean(string='Producto BIO')
     productos = fields.One2many('product.template', 'productomaestro', string='Productos Incluidos')
     paisyprecio = fields.One2many('jovimer_productos_maestros_pyp', 'productomaestro', string='Productos Incluidos')



class ModelAlmacenLin(models.Model):
      
     _name = 'jovimer_almacen_lin'
     _description = 'Gestion Almacén'


     # Campos 
     name = fields.Many2one('jovimer_expedientes', string='Expediente')
     expediente_serie = fields.Selection('jovimer_expedientes', related='name.campanya')  
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='name.serie')
     cliente = fields.Many2one('res.partner', related='name.cliente') 
     lineaafectada = fields.Many2one('account.invoice.line', string='Linea Afectada')
     fecha = fields.Date(string='Fecha', default=fields.Date.today)
     cantidad = fields.Float(string='Bultos')
     referencia = fields.Char(string='Referencia')
     precio = fields.Float(string='Precio Compra')
     precioservprov = fields.Float(string='Precio Service Providing')
     observaciones = fields.Text(string='Observaciones')
     almacen = fields.Selection([
		('CHEQUIA','CHEQUIA'),
		('ESLOVENIA','ESLOVENIA'),
		('XERESA','XERESA'),
		],string='Almacen',default='CHEQUIA')


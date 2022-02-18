# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import subprocess

class ModelSaleOrder(models.Model):
     
     # Herencia de la tabla de ventas
     _inherit = 'purchase.order'
     

     # Campos Pesonalizados en pedidos de Venta
     fechasalida  = fields.Date(string='Fecha de Pedido / Salida')
     fechallegada = fields.Date(string='Fecha de Llegada')
     horallegada  = fields.Char(string='Hora de Llegada', help='Permite caracteres Alfanuméricos')
     campanya = fields.Char(string='Serie / Campaña', help='Número Expediente')
     expediente = fields.Many2one('jovimer_expedientes', string='Expediente')
     pedidocerrado = fields.Boolean(string='Pedido Cerrado', related='expediente.pedidocerrado')
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya')
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')
     expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name')
     mododecobro = fields.Many2one('payment.acquirer', string='Modo de Cobros')
     conformalote = fields.Many2one('jovimer_conflote', string='Conforma LOTE')
     obspedido = fields.Text(string='Observaciones PEdido')
     description  = fields.Char(string='Desc.')
     estadodesc  = fields.Char(string='Estado Desc.')
     att  = fields.Char(string='Attención de:')
     consignatario  = fields.Char(string='Consignatario/Plataforma')
     destino  = fields.Boolean(string='Para Almacén')
     destinodonde  = fields.Char(string='Donde Está')
     saleorder  = fields.Many2one('sale.order', string='Venta Relacionada')
     partnersale  = fields.Many2one('res.partner', related='saleorder.partner_id', store=True)
     obspartnersale  = fields.Text(string='Observaciones Cliente')
     viajegenerado  = fields.Boolean(string='Viaje')
     totaleuro  = fields.Float(string='Palet')
     totalgr  = fields.Float(string='GR Palet') 
     estadocrear = fields.Boolean(string='Finalizada Creacion')
     paisdestino = fields.Many2one('res.country', string='Pais Destino')

     def button_cancel(self):
        for order in self:
            notas = order.notes
            pedidocerrado = order.pedidocerrado
            estadopedido = order.state
            if pedidocerrado == True:
               raise UserError("NO Puedes Cancelar este documento.\n El Pedido de Venta está cerrado y por tanto NO se pueden Modificar los Pedidos de Compra")

            print("\n\n Notas SON: " + str(notas) + ".")
            for lines in order.order_line:
                print("\n\n Lienas de Albarán: " + str(lines.lineaalbarancompra.id) + "\n\n")
                if lines.viajerel.id != False:
                    print("NO SE PUEDE CANCELAR: " + str(lines.viajerel.id) + ".")
                    raise UserError("NO se Puede Cancelar este Documento porque Ya esta registrada en algún VIAJE")
                if lines.lineaalbarancompra.id != False:
                    print("NO SE PUEDE CANCELAR: " + str(lines.lineaalbarancompra.id) + ".")
                    raise UserError("NO se Puede Cancelar este Documento porque Ya esta registrada alguna linea en Albaranes")

            if str(notas) == "False":
               raise UserError("Debes escribir un motivo en el apartado de Terminos y Condiciones por el motivo de la cancelación")
            for inv in order.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(_("Unable to cancel this purchase order. You must first cancel the related vendor bills."))

            for lines in order.order_line:
               saleorderline = lines.saleorderline.id
               poline = lines.id
               lineascompra = self.env['jovimer_lineascompra'].sudo().search([('orderline','=',saleorderline),('purchaseline','=', poline)]).id
               print("\n -------------- PEDCOMPRA ES: " + str(lineascompra) + " La linea de Pedido: " + str(poline) + " y la linea de venta a la que pertenece es: " + str(saleorderline) + "\n")
               if lineascompra != False:
                  borralinea = self.env['jovimer_lineascompra'].sudo().search([('id','=',lineascompra)]).unlink()


        self.write({'state': 'cancel'})


     def action_creaviajes(self, default=None):
         id = str(self.id)
         args = ["/opt/jovimer12/bin/creaviajes.bash", id, "&"]
         subprocess.call(args)
         self.write({'status': 'purchase'})
         return {}

     def action_validaeimprime(self, default=None):
         for order in self:
             try:          
                 idposa = str(order.id)
                 args = ["/opt/jovimer12/bin/creaviajes.bash", idposa, "&"]
                 subprocess.call(args)
             except:
                 print('NO SALE')
         self.write({'state': 'purchase'})
         self.write({'estadodesc': 'Impreso'}) 
         return self.env.ref('pyme_jovimer.purchase_order_jovimer_report').report_action(self)

     def action_validayenvia(self, default=None):
        for order in self:
            try:          
                idposa = str(order.id)
                args = ["/opt/jovimer12/bin/creaviajes.bash", idposa, "&"]
                subprocess.call(args)
            except:
                print('NO SALE')
        self.write({'state': 'purchase'})
        self.write({'estadodesc': 'Email Enviado'})         

        ### Enviamos EMAIL
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.env.context.get('send_rfq', False):
                template_id = ir_model_data.get_object_reference('purchase', 'email_template_edi_purchase')[1]
            else:
                template_id = ir_model_data.get_object_reference('purchase', 'email_template_edi_purchase_done')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'purchase.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'mark_rfq_as_sent': True,
        })

        # In the case of a RFQ or a PO, we want the "View..." button in line with the state of the
        # object. Therefore, we pass the model description in the context, in the language in which
        # the template is rendered.
        lang = self.env.context.get('lang')
        if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
            template = self.env['mail.template'].browse(ctx['default_template_id'])
            if template and template.lang:
                lang = template._render_template(template.lang, ctx['default_model'], ctx['default_res_id'])

        self = self.with_context(lang=lang)
        if self.state in ['draft', 'sent']:
            ctx['model_description'] = _('Request for Quotation')
        else:
            ctx['model_description'] = _('Purchase Order')
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
 
		 
		 
		## return self.env.ref('action_rfq_send').report_action(self)


     
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
     asignacionj = fields.Many2one('sale.order.line', string='Asignación', related='idasignacion.saleorderlinedestino', store=True)
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
     name  = fields.Char(string='Nombre')
     nocalcbultos = fields.Boolean(string='No Calcula Bultos')
     kgnetbulto = fields.Float(string='Kg/Net Bulto') 
     partner = fields.Many2one('res.partner', string='Cliente')
     cantidadpedido = fields.Float(string='Cantidad Pedido') 
     cantidadasignada = fields.Float(string='Cantidad Original')
     unidadasignada = fields.Many2one('uom.uom', string='Ud. Asig.')
     estaasignada = fields.Boolean(string='Asignado')
     expedienteorigen = fields.Many2one('jovimer_expedientes', string='Expediente Origen')
     unidadpedido = fields.Many2one('uom.uom', string='Unidad Pedido', domain=[('invisible','=','NO')])
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
     destino  = fields.Boolean(string='Para Almacén', related='order_id.destino', store=True)
     destinodonde  = fields.Char(string='Donde Está', related='order_id.destinodonde', store=True)	 
     fechasalida = fields.Date(string='Fecha Salida', related='order_id.fechasalida')
     etiquetau  = fields.Text(string='Etiqueta Unidad')	 
     lineafacturacompra  = fields.Many2one('account.invoice', string='Albarán')	 
     lineaalbarancompra  = fields.Many2one('account.invoice.line', string='Linea Albarán')	
     albarancomprarel  = fields.Many2one('account.invoice', string='Albarán Compra', related='lineaalbarancompra.invoice_id')
     etiquetab  = fields.Text(string='Etiqueta BUlto')	 
     facturado  = fields.Boolean(string='Prepara Albaran Factura')
     plantillaetiquetasc = fields.Many2one('jovimer_etiquetas_plantilla', string='Plantilla Etiquetas')      
     idgeneraalbaranes = fields.Many2one('jovimer_generaalbaranes', string='ID Genera Albaranes')	 
     jovimer_lineascompra = fields.Many2one('jovimer_lineascompra', string='Linea Origen Compra')	 
     statusrecla = fields.Selection([
		('OK','OK'),
		('RECLAMADA','RECLAMADA'),
		('DEVUELTA','DEVUELTA'),
		],string='Estado',default='OK')     
  
    
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
         self.env.cr.execute("select id from ir_ui_view where name LIKE '%view_recepcionptabletcarga_form%' and type='form' ORDER BY id DESC LIMIT 1")
         result = self.env.cr.fetchone()
         record_id = int(result[0])
         view = {
            'name': _(viewname),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order.line',
            'view_id': record_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'flags': {'initial_mode': 'view'},
            'res_id': idmensaje }
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
           self.env['sale.order.line'].create(vals)	
           ## return {'type': 'ir.actions.client', 'tag': 'reload',}

     def action_creact(self, default=None):
           return {}

		   
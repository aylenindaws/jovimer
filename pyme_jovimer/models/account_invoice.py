# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import subprocess
from time import sleep
from datetime import datetime, date, time, timedelta
import math

class ModelAccountInvoice(models.Model):
     
     # Herencia de la tabla de ventas
     _inherit = 'account.invoice'
     
     def _get_total_kg(self):
        try:
          order = self.id
          self.env.cr.execute(""" select sum(totalkglin) from account_invoice_line where invoice_id='%s'""" % (order))
          resultv = self.env.cr.fetchone()
          self.totalkg = resultv[0]
        except:
          print("self.totalkg = 0")
        return {}
 
     def _get_total_bultoskg(self):
        for rec in self:
           try:
              order = rec.id
              rec.env.cr.execute(""" select sum(totalbultos) from account_invoice_line where invoice_id='%s'""" % (order))
              resultv = rec.env.cr.fetchone()
              rec.totalbltkg = resultv[0]
           except:
              print("rec.totalbltkg = 0")
        return {}

     def _get_total_palets(self):
        for rec in self:
           try:
              order = rec.id
              rec.env.cr.execute(""" select sum(cantidadpedido) from account_invoice_line where invoice_id='%s'""" % (order))
              resultv = rec.env.cr.fetchone()
              rec.totalpalets = resultv[0]
           except:
              print("rec.totalpalets = 0")
        return {}


     def _compute_total_weightnet(self):
        for rec in self:
            totalkg = 0
            for line in rec.invoice_line_ids:
                if line.product_id:
                    totalkg += line.totalkglin or 0.0
            rec.totalkg = totalkg

     def _compute_total_weight(self):
        for rec in self:
            totalkgbr = 0
            for line in rec.invoice_line_ids:
                if line.product_id:
                    totalkgbr += line.totalkglinbr or 0.0
            rec.totalkgbr = totalkgbr



     def _compute_numfactnorm(self):
        numfactnorm = ""
        for rec in self:
            journaltype=rec.journal_id.type
            numinterno=rec.number
            numexterno=rec.reference
            if journaltype == "sale":
               numfactnorm = str(numinterno)
            if journaltype == "purchase":
               numfactnorm = str(numexterno)
            rec.numfactnorm = numfactnorm


     def _compute_valorasignado(self):
        valorasignado = 0
        for rec in self:
            invoiceid = rec.id
            valorasignado = sum(line.price_subtotalas for line in rec.invoice_line_ids)
            ### rec.env.cr.execute("select sum(price_subtotalas) from account_invoice where invoice_id='" + str(invoiceid) + "'")
            ### result = self.env.cr.fetchone()
            ### palets = result[0]
            rec.valorasignado = valorasignado

     def _compute_compasignadoorigen(self):
        compasignadoorigen = True
        for rec in self:
            price1 = rec.amount_untaxed
            price2 = rec.valorasignado
            if str(price1) != str(price2):
               compasignadoorigen = False
            contadorasignados = self.env['account.invoice.line'].search_count([('invoice_id','=',rec.id),('asignaroriginal','=',True)])
            if contadorasignados == 0:
               compasignadoorigen = True
            print("\n Precios " + str(price1) + " <> " + str(price2)+ " :: Contador Asignados: " + str(contadorasignados) + "\n")
            rec.compasignadoorigen = compasignadoorigen

     # Campos Pesonalizados en pedidos de Venta
     fechasalida  = fields.Date(string='Fecha de Salida')
     fechallegada = fields.Date(string='Fecha de Llegada')
     horallegada  = fields.Char(string='Hora de Llegada', help='Permite caracteres Alfanuméricos')
     campanya = fields.Char(string='Serie / Campaña', help='Número Expediente')
     expediente = fields.Many2one('jovimer_expedientes', string='Expediente')
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya')
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')
     expediente_serienb = fields.Boolean(string='Actualizado Expediente')
     expediente_num = fields.Integer('jovimer_expedientes', related='expediente.name')
     mododecobro = fields.Many2one('payment.acquirer', string='Modo de Cobros')
     conformalote = fields.Many2one('jovimer_conflote', string='Conforma LOTE')
     obspedido = fields.Text(string='Observaciones PEdido')
     ordendecarganac = fields.Many2many('jovimer_ctn', string='Orden de Carga Nacional')
     ordendecargaint = fields.Many2many('jovimer_cti', string='Orden de Carga Internacional')
     totalkg = fields.Float(string='Kg. Neto', compute='_compute_total_weightnet')
     totalkgbr = fields.Float(string='Kg. Bruto', compute='_compute_total_weight')
     totalbltkg = fields.Float(string='Total Bultos', compute='_get_total_bultoskg')
     expedientesdecompra = fields.Many2many('jovimer_expedientes', string='Exp. Origen')
     refcliente = fields.Char(string='Referencia CLiente')
     totalbultosccvta = fields.Float(string='Total Bultos Compra cta vta', store=True)
     totalbultosvcvta = fields.Float(string='Total Bultos Venta Cta Vta', store=True)	 
     ctavtarepasado = fields.Boolean(string='Repasado')   
     ctavtaenviado = fields.Boolean(string='Enviado')
     ctavtaimpreso = fields.Boolean(string='Impreso')
     fechactavtarepasado  = fields.Date(string='Fecha Repasado Cuenta de Venta')
     fechactavtaenviado  = fields.Date(string='Evío Cta.Vta.')      
     traspasocont = fields.Boolean(string='Traspasado Contabilidad')   
     traspasocontfecha = fields.Date(string='Fecha Traspaso')        
     traspasoid = fields.Many2one('jovimer_traspasoconta', string='Traspaso')        
     albaranfacturado = fields.Boolean(string='Albarán Facturado')
     fechaalbaranfacturado  = fields.Date(string='Fecha Albarán Facturado')
     docresultante  = fields.Many2one('account.invoice', string='Fact Resultante')
     totalpalets  = fields.Float(string='Total Palets', compute='_get_total_palets')
     partnerfiscal = fields.Many2one('res.partner', string='Partner Fiscal')
     taxorig = fields.Float(string='Tax Orig')
     taxrecal = fields.Float(string='Tax Recal')
     totalorig = fields.Float(string='Total Orig')
     fechaoperacionrect = fields.Date(string='Fecha Ope. Rect')
     ctavtacompleto = fields.Boolean(string='Repasado Completo')
     lineascompraalb = fields.One2many('purchase.order.line', 'lineafacturacompra', string='Lineas de Compra')
     modorecti = fields.Selection([('False','Escoge un Valor...'),('diferencia','Por Diferencias'),('total','Por el Total')],string='Modo',default='False') 
     rectificasubtotal = fields.Float(string='Rectifica Subtotal')
     rectificafactres = fields.Many2one('account.invoice', string='Fact Rect 1.')     
     rectificafactres2 = fields.Many2one('account.invoice', string='Fact Rect 2.')     
     viaje = fields.Many2one(string='Viaje Relacionado')
     totaleurodollar = fields.Float(string='Total Eur (€)')
     cambiodollar = fields.Float(string='Cambio Dollar/Euro', digits=(12,3))
     modologocontatrans = fields.Boolean(string='Trans')
     modologocontatranssiniva = fields.Boolean(string='Trans S')
     modologocontasujpa = fields.Boolean(string='Suj. P.')
     modologocontamerca = fields.Boolean(string='Mercancia Nac')
     modologocontamercasp = fields.Boolean(string='Mercancia Nac y SP')
     modologocontamercain = fields.Boolean(string='Mercancia Intra')
     modologocontaasignado = fields.Boolean(string='Asignado')
     cadenafactcomprar = fields.Many2one('account.invoice', string='Factura Dependiente')
     cadenafactcompra = fields.One2many('account.invoice','cadenafactcomprar',string='Cadena Facturas Compra')	
     fileedi = fields.Binary('Fichero EDI')
     fileedilink = fields.Char('Fichero EDI')
     buscaasignacion = fields.Many2one('purchase.order.line', string='Busca Asignacion', domain=[('asignado','=', True)])
     buscaasignacionp = fields.Many2one('purchase.order.line', string='Busca Asignacion', domain=[('lineafacturacompra','=', False)])
     descripcioncajas = fields.Text(string='Cajas por Produto')
     contenedordes = fields.Char(string='Contenedor')
     totalesmanuales = fields.Boolean(string='Redondeo Manual') 
     redondeoiva = fields.Float(string='Redondeo IVA') 
     redondeobase = fields.Float(string='Redondeo Base') 
     sumabultosalbasigo = fields.Float(string='Bultos Originales') 
     sumabultosalbasiga = fields.Float(string='Bultos Asignados') 
     restobultosasignado = fields.Float(string='Resto')
     restobultosmal = fields.Boolean(string='Bultos MAL')
     totallineas = fields.Integer(string='Total Lineas')
     totaltarap = fields.Integer(string='Total Tara Palets')
     totaltarab = fields.Integer(string='Total Taras Box')
     totalpaletsi = fields.Integer(string='Total Palets Informe')
     totalbultoslin = fields.Integer(string='Total Bultos Lineas')
     partnername = fields.Char(string='Partner Name', related='partner_id.name')
     partnerpart = fields.Many2one('res.partner', string='Partner parent', related='partner_id.parent_id')
     ## numfactagos = fields.Char(string='Num Factura COBROS/PAGOS',  compute='_compute_numfactagos', store=True)
     numfactnorm = fields.Char(string='Num Factura COBROS PAGOS',  compute='_compute_numfactnorm', index=True)
     valorasignado = fields.Float(string='Valor Asignación',  compute='_compute_valorasignado', index=True)
     compasignadoorigen = fields.Boolean(string='Diferencia',  compute='_compute_compasignadoorigen', index=True)
     fsproviding = fields.Boolean(string='Es Service Providing', index=True)

     pteimportarcompra = fields.Selection([
		('PTE','PTE'),
		('OK','OK'),
		('FINALIZADO','FINALIZADO'),
		('NO','NO'),
		],string='Incorporar Lineas de Albarán',default='NO')     



     def action_invoice_cancel_pyme(self):
         ### if self.filtered(lambda inv: inv.state not in ['draft', 'open']):
         ###     raise UserError(_("Las Facturas Pagadas No pueden cancelarse si no se eliminan los Pagos o Cobros Primero."))
         iddoc = self.id
         idjournal = self.journal_id.id
         ctavtacompleto = self.ctavtacompleto
         sent = self.sent
         if idjournal == 9:
            if ctavtacompleto == True:
               raise AccessError("EL Albarán de Compra YA tiene una cuenta de Venta Realizada NO puede Cancelarse")
            if sent == True:
               raise AccessError("EL Albarán de Compra YA tiene una cuenta de Venta Realizada y Enviada NO puede Cancelarse")

         if self.bloqueapago == True:
            raise AccessError("Las Facturas con PAGOS realizados NO pueden ser modificadas y/o canceladas")
         return self.action_cancel()


     def action_invoice_cancel_ctvta(self):
         ### if self.filtered(lambda inv: inv.state not in ['draft', 'open']):
         ###     raise UserError(_("Las Facturas Pagadas No pueden cancelarse si no se eliminan los Pagos o Cobros Primero."))
         iddoc = self.id
         idjournal = self.journal_id.id
         ctavtacompleto = self.ctavtacompleto
         sent = self.sent

         if self.bloqueapago == True:
            raise AccessError("Las Facturas con PAGOS realizados NO pueden ser modificadas y/o canceladas")
         return self.action_cancel()

     def action_invoice_cancel_pyme2(self):
         ### if self.filtered(lambda inv: inv.state not in ['draft', 'open']):
         ###     raise UserError(_("Las Facturas Pagadas No pueden cancelarse si no se eliminan los Pagos o Cobros Primero."))
         iddoc = self.id
         idjournal = self.journal_id.id
         if self.bloqueapago == True:
            raise AccessError("Las Facturas con PAGOS realizados NO pueden ser modificadas y/o canceladas")
         context = self._context
         current_uid = context.get('uid')
         if current_uid == 17 or current_uid == 20:
             self.write({'traspasocont': False})
             self.write({'traspasocontfecha': False})
             return self.action_cancel()
         else:            
             raise AccessError("No tienes Permiso para poder Cancelar una Factura COntabilizada. El Usario con permiso: Miguel Sanfelix y Anais Reig - administracion")



     def copy(self, context=None):
         iddoc = self.id
         idjournal = self.journal_id.id
         if idjournal == 9:
           raise AccessError("No se pueden Duplicar ALbaranes de Entrada. En su lugar utiliza el Modo de Dividir Albarán")
         ## if idjournal == 10:
         ##  raise AccessError("No se pueden Duplicar ALbaranes de Salida.")
         duplica = super(ModelAccountInvoice, self).copy()
         return duplica

     def copy2(self, context=None):
         iddoc = self.id
         idjournal = self.journal_id.id
         ## if idjournal == 10:
         ##   raise AccessError("No se pueden Duplicar ALbaranes de Salida.")
         duplica = super(ModelAccountInvoice, self).copy()
         return duplica


     def reload_fiscal_position(self, context=None):
         iddoc = self.id
         idfiscal = self.fiscal_position_id.id
         statedoc = self.state
         if statedoc != 'draft':
            raise AccessError("No se puede realizar esta acción si el documento no está en Borrador/Activo")
         if idfiscal == 2:
            for lines in self.invoice_line_ids:
                idline = lines.id
                namevar = lines.variedad.name
                print("\n\n-- Linea: " + str(idline) + " :: " + str(namevar) + "")
                for tax_lines in lines.invoice_line_tax_ids:
                    idtax = tax_lines.id
                    nametax = tax_lines.name
                    print("-- Linea: " + str(idline) + " TAX Linea: " + str(idtax) + " :: " + str(nametax) + "\n")               
                    ## borralinea = tax_lines.sudo().unlink()
                    self.env.cr.execute("DELETE FROM account_invoice_line_tax where invoice_line_id='" + str(idline) + "' and tax_id='" + str(idtax) + "'")
            borralineafact = self.env['account.invoice.tax'].search([('invoice_id','=', iddoc)]).sudo().unlink()
            print(" Se ha borrado la linea: " + str(borralineafact) + " de los impuestos \n\n")
            return {}
         else:
            raise AccessError("El Documento: " + str(iddoc) + " tiene una posicion Fiscal que no permite recalcular el impuesto")

     def action_calculatodoslasunidades(self, vals):
         idalb = self.id
         linename = ""
         for linalb in self.invoice_line_ids:
                  linename += "\n" + str(linalb.name)
                  linalb.calcula_cantidadcli()
         return {}



     def action_calculaasignadoctcv(self,):
         idalb = self.id
         args = ["/opt/jovimer12/bin/acutalizaalbarancv_asignado.sh", str(idalb), "&"]
         subprocess.call(args)
         return {}



     def dividiralbarancompra(self, context=None):
        self.ensure_one()
        self.env.cr.execute(""" select id from ir_ui_view where name='jovimer_dividiralbaranes_view_tree' and type='tree' ORDER BY id DESC LIMIT 1""")
        result = self.env.cr.fetchone()
        record_id = int(result[0])
        usuarioname = self.env.user.name
        usuarioid = self.env.user.id
        ## if usuarioid != 2:
        ##   raise AccessError(str(usuarioname) + " esto no lo puedes gastar todavía")
        invoiceid = self._ids[0]
        return {
        'name': ("Dividir Albaranes de Compra"),
        'type': 'ir.actions.act_window',
        'res_model': 'account.invoice.line',
        'view_mode': 'tree',
        'view_type': 'form',
        'view_id': record_id,
        'target': 'current',
        'domain': [('invoice_id','=',invoiceid),('asignaroriginal','=',False)],
        }
        return {}



     def action_numeralineas(self,):
         idalb = self.id
         self.env.cr.execute("select sum(*) from account_invoice_line where invoice_id='" + str(idalb) + "'")
         result = self.env.cr.fetchone()
         totallineas = int(result[0])
         return {}


     def action_printpackinglist(self):
         iddoc = self.id
         self.env.cr.execute("select count(*) from account_invoice_line where invoice_id='" + str(iddoc) + "'")
         result = self.env.cr.fetchone()
         totallineas = int(result[0])
         self.env.cr.execute("select sum(totalbultos) from account_invoice_line where invoice_id='" + str(iddoc) + "'")
         result = self.env.cr.fetchone()
         totalbultoslin = int(result[0])
         self.env.cr.execute("select sum(cantidadpedido) from account_invoice_line where invoice_id='" + str(iddoc) + "'")
         result = self.env.cr.fetchone()
         totalpaletsi = int(result[0])
         self.env.cr.execute("SELECT sum(jovimer_envase.pesobruto) FROM account_invoice_line INNER JOIN jovimer_envase	ON account_invoice_line.envase = jovimer_envase.id WHERE invoice_id='" + str(iddoc) + "'")
         result = self.env.cr.fetchone()
         totaltarab = int(result[0])
         self.env.cr.execute("SELECT sum(uom_uom.pesobruto) FROM account_invoice_line INNER JOIN uom_uom	ON account_invoice_line.unidadpedido = uom_uom.id WHERE invoice_id='" + str(iddoc) + "'")
         result = self.env.cr.fetchone()
         totaltarap = int(result[0])
         for lines in self.invoice_line_ids:
             name = lines.name
             cajas = lines.totalbultos
             palets = lines.cantidadpedido
             kgnet = lines.totalkglin
             tarabox = lines.envase.pesobruto
             tarapalet = lines.unidadpedido.pesobruto
             if tarabox == 0:
              raise AccessError("El Envase de " + str(name) + " no tiene peso asignado. Debes establecerlo para hacer el calculo de Peso Bruto")
             if tarapalet == 0:
              raise AccessError("El Envase de " + str(name) + " no tiene peso asignado. Debes establecerlo para hacer el calculo de Peso Bruto")
             pesopalets = palets * tarapalet
             pesocajas = cajas * tarabox
             pesobruto = float(kgnet) + float(pesocajas) + float(pesopalets)
             lines.totalkglinbr = pesobruto
             ## raise AccessError("Nombre: " + str(name) + " Peso Neto: " + str(kgnet) + " Peso Bruto " + str(pesobruto) + " = " + str(pesopalets) + " + " + str(pesocajas) + " cajas: " + str(cajas) + " palets: " + str(palets) + " kgnet: " + str(kgnet) + " tarabox: " + str(tarabox) + " tarapalet: " + str(tarapalet) + "")
         self.write({'totallineas': totallineas,'totalbultoslin':totalbultoslin,'totalpaletsi':totalpaletsi,'totaltarab':totaltarab,'totaltarap':totaltarap})
         return self.env.ref('pyme_jovimer.packing_list_jovimer_report').report_action(self)



     def action_calcularestobultos(self, vals):
         idaccount = self.id
         totaloriginal = 0
         totaloasig = 0
         ## self.env.cr.execute(""" update account_invoice_line set asignarnosale='f' where invoice_id='%s'""" % (idaccount))
         for lines in self.invoice_line_ids:
              lines.asignarnosale = False
              totalbultos = lines.totalbultos
              self.env.cr.execute("select sum(totalbultos) from account_invoice_line where invoice_id='" + str(idaccount) + "' and asignaroriginal='t'")
              result1 = self.env.cr.fetchone()
              totaloasig = result1[0]
              self.env.cr.execute("select sum(totalbultos) from account_invoice_line where invoice_id='" + str(idaccount) + "' and ( asignaroriginal='f' or asignaroriginal IS NULL)")
              result2 = self.env.cr.fetchone()
              totaloriginal = result2[0]
              if str(totaloasig) == "None": 
                 totaloasig = totaloriginal
              if str(totaloriginal) == "None": 
                 totaloriginal = 0
         restobultos = float(totaloriginal) - float(totaloasig)
         if restobultos != 0:
            alerta = True
         else:
            alerta = False
         args = ["/opt/jovimer12/bin/actionserver_quitaptealbcli.sh", str(idaccount), '&']
         subprocess.call(args)
         self.sumabultosalbasiga = float(totaloasig)
         self.sumabultosalbasigo = float(totaloriginal)
         self.restobultosasignado = float(restobultos)
         self.restobultosmal = alerta

         return {}



     def action_validate_and_write(self, vals):
         userid = self.env.user.id
         id = self.id
         ### if str(userid) != "2" or str(userid) != "18":
         ###    raise UserError("Este Botón NO está disponible para los Usuarios NO admin.")
         ###    return {}



         ### Validar
         # lots of duplicate calls to action_invoice_open, so we remove those already open
         to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
         if to_open_invoices.filtered(lambda inv: not inv.partner_id):
            raise UserError(_("Sin Cliente/Proveedor no puedes Guardar el Documento."))
         if to_open_invoices.filtered(lambda inv: inv.state != 'draft'):
            raise UserError(_("NO se puede Guardar y Validar si no esta en modo Activo"))
         if to_open_invoices.filtered(lambda inv: not inv.account_id):
            raise UserError(_('Se necesitan Productos con Cuenta Contable Definida para poder Guardar y Validar el Documento'))
         to_open_invoices.action_date_assign()
         to_open_invoices.action_move_create()
         to_open_invoices.invoice_validate()


         ### Guradar
         ### url = "/web#action=765&model=account.invoice&view_type=list&menu_id=656"
         ### return {
         ###    'res_model': 'ir.actions.act_url',
         ###    'type': 'ir.actions.act_url',
         ###    'url':  url,
         ###    'target' : 'self'
         ###    }
         search_view_id = 1947
         return {
                  'name': _('Listado de Albaranes'),
                  'view_type': 'form',
                  'view_mode': 'tree, form',
                  'view_id': False,
                  ## 'view_id': self.env.ref('pyme_jovimer.jovimer_facturas_prova_view_tree').id,
                  'views': [(self.env.ref('pyme_jovimer.jovimer_facturas_prova_view_tree').id, 'tree'), (self.env.ref('pyme_jovimer.jovimer_facturas_prov_view_form').id, 'form')],
                  'search_view_id': False,
                  'res_model': 'account.invoice',
                  'context': "{'default_type': 'in_invoice', 'type': 'in_invoice', 'journal_type': 'purchase', 'default_journal_id': 9,' default_search_view_id': 1947}",
                  'domain': "[('type','=','in_invoice'),('partner_id.supplier','=', True),('journal_id','=', 9),('albaranfacturado','=', False),('expedientesdecompra','!=', False)]",				  
                  'type': 'ir.actions.act_window',
                  'target': 'main',
                  }

     @api.onchange('partner_id')
     def _onchange_partner_journal(self):
         journal_id = False
         partner_id = self.partner_id.id
         journal_idv = self.partner_id.seriefacturasvta.id
         journal_idc = self.partner_id.seriefacturascomp.id
         typefact = self.type
         if str(typefact) == 'out_invoice':
            journal_id = journal_idv
         if str(typefact) == 'in_invoice':
            journal_id = journal_idc
         print("\n En una Factura: " + str(typefact) + " EL Partner: " + str(partner_id) + " tiene la Serie: " + str(journal_id) + "\n")
         if journal_id != False:
            self.journal_id = journal_id

     @api.onchange('expediente')
     def on_change_expediente(self):
         expedienteid = str(self.expediente.id)
         expedientenum = str(self.expediente.name)
         expedienteserie = str(self.expediente.campanya)
         journal = self.journal_id.id
         today = date.today()
         if str(journal) == '10':
           try:
             ## self.env.cr.execute(""" select partner_shipping_id from sale_order where expediente='%s' ORDER BY id DESC LIMIT 1""" % (expedienteid))
             ## result = self.env.cr.fetchone()
             self.partner_id = self.expediente.cliente
             self.date_invoice = today
             if str(expedienteid) != "False":
               self.env.cr.execute(""" select refcliente from sale_order where expediente='%s' ORDER BY id LIMIT 1""" % (expedienteid))
               result = self.env.cr.fetchone()
               refcliente = result[0]
               if str(refcliente) != "None":
                 self.refcliente = refcliente
               else:
                 self.refcliente = str(expedienteserie) + "-" + str(expedientenum)
             else:
               self.refcliente = "Debes Seleccionar primero el Expediente de Referencia"
             ## self.partner_shipping_id= result[0]
             ## self.fileedilink = str(refcliente)
             return {}
           except:
             return {}

     @api.onchange('totaleurodollar','cambiodollar','currency_id','amount_untaxed')
     def on_change_totaleurodollar(self):
         cambiodollar = 0
         amount_untaxed = 0
         amount_untaxed = self.amount_untaxed
         cambiodollar = self.cambiodollar
         try:
             self.totaleurodollar = float(amount_untaxed) * float(cambiodollar)
         except:
             self.totaleurodollar = 0

     def jovimer_view_lineasfact(self, context=None):
        self.ensure_one()
        ### self.env.cr.execute(""" select id from ir_ui_view where name LIKE '%JOVIMER - Control Transporte Nacional%' and type='tree' ORDER BY id DESC LIMIT 1""")
        ### result = self.env.cr.fetchone()
        ### record_id = int(result[0])
        orderid = self.id
        return {
        'name': ("Lineas de Documentos Albaran / Factura"),
        'type': 'ir.actions.act_window',
        'res_model': 'account.invoice.line',
        'view_mode': 'tree',
        'view_type': 'form',
        ## 'view_id': record_id,
        'target': 'current',
        'domain': [('invoice_id','=',orderid)],
        }
        return {}


     def action_creaediexport(self):
           iddoc = self.id
           idjournal = self.journal_id.id
           edinumber = self.edinumber
           if str(edinumber) == "False":
                   raise UserError("El Partner tiene el Número EDI Vacio. Este Campo se debe cumplimentar en la Ficha del Cliente")
                   return {}
           dateinvoice = self.date_invoice
           fechaformato = dateinvoice.strftime("%Y%m%d")
           for l in self.invoice_line_ids:
               totalkglin = l.totalkglin
               codprod = l.codproducto
               varprod = l.variedad.name
               varprode = l.variedad.abrev
               ## raise UserError("Esto: " + str(codprod) + "")
               if str(codprod) == "False" or str(varprode) == "False":
                   raise UserError("La linea de Producto: " + str() + ", no tiene codigo de producto en la Plantilla o sin traduccion al Inglés")
                   return {}
               if str(totalkglin) == "0" or str(totalkglin) == "False":
                   raise UserError("La linea de Producto: " + str() + ", no tiene Kilos establecidos. Debe existir un valor")
                   return {}
           if idjournal == 10:
               args = ["/opt/jovimer12/bin/creaedi_albaran.sh", str(iddoc), "&"]
               subprocess.call(args)
           else:
               args = ["/opt/jovimer12/bin/creaedi_invoice.sh", iddoc, "&"]
               ### subprocess.call(args)
               raise UserError("EL Fichero Edi no puede Generarse debido a la Falta de Datos de Intercambio EDI en la Factura de Cliente")
           ## return {}
           return {
             'type' : 'ir.actions.act_url',
             'url': '/web/static/EDI/DESADV' + str(fechaformato) + '' + str(iddoc) + '.dat',
             'target': 'new',}


     def quita_totalesmanuales(self):
           totalmanual = self.totalesmanuales
           self.redondeobase = 0
           self.redondeoiva = 0
           self.totalesmanuales = False
           return {}


     ### def suma1centbase(self):
     ###       amount_tax = self.amount_tax
     ###       amount_total = self.amount_total
     ###       amount_untaxed = self.amount_untaxed
     ###       redondeobase = self.redondeobase
     ###       if redondeobase > 0.09:
     ###           raise UserError("El Redondeo Excede el límite posible de +10 Ct en la BASE. No puedes añadir más")
     ###       try:
     ###           amount_untaxed = float(amount_untaxed) + 0.01
     ###           amount_total = float(amount_total) + 0.01
     ###           self.amount_untaxed = amount_untaxed
     ###           self.amount_total = amount_total
     ###           self.totalesmanuales = True
     ###           self.redondeobase += 0.01
     ###       except:
     ###           amount_untaxed = amount_untaxed
     ###           raise AccessError("Ha habido algun error al Realizar la operacion")
     ###       return {}


     def suma1centbase(self):
           inlinetax_ids = self.env['account.invoice.tax'].search([('invoice_id', '=', int(self.id))], limit=1)
           redondeobase = 0
           base = 0
           amount_tax = self.amount_tax
           amount_total = self.amount_total
           amount_untaxed = self.amount_untaxed
           for invoicetax in inlinetax_ids:
               base = invoicetax.base
               if redondeobase > 0.09:
                  raise UserError("El Redondeo Excede el límite posible de +10 Ct en la BASE. No puedes añadir más")
               base1 = base + 0.01
               print("Base: " + str(base1))
               invoicetax.update({'base':base1})
               ## raise AccessError("La Base es: " + str(base))
               amount_untaxed = float(amount_untaxed) + 0.01
               amount_total = float(amount_total) + 0.01
               self.amount_untaxed = amount_untaxed
               self.amount_total = amount_total
               self.totalesmanuales = True
               self.redondeobase += 0.01
           return {}


     def rest1cenbase(self):
           inlinetax_ids = self.env['account.invoice.tax'].search([('invoice_id', '=', int(self.id))], limit=1)
           redondeobase = 0
           base = 0
           amount_tax = self.amount_tax
           amount_total = self.amount_total
           amount_untaxed = self.amount_untaxed
           redondeobase = self.redondeobase
           if redondeobase < -0.09:
               raise UserError("El Redondeo Excede el límite posible de -10 Ct en la BASE. No puedes quitar más")
           try:
               ### lineaiva = self.env['account.invoice.tax'].search([('invoice_id','=',invoice_id)])
               amount_untaxed = float(amount_untaxed) - 0.01
               amount_total = float(amount_total) - 0.01
               self.amount_untaxed = amount_untaxed
               self.amount_total = amount_total
               self.totalesmanuales = True
               self.redondeobase += -0.01
           except:
               amount_untaxed = amount_untaxed
               raise AccessError("Ha habido algun error al Realizar la operacion")
           return {}




     def suma1centiva(self):
           amount_tax = self.amount_tax
           amount_total = self.amount_total
           amount_untaxed = self.amount_untaxed
           redondeoiva = self.redondeoiva
           if redondeoiva > 0.09:
               raise UserError("El Redondeo Excede el límite posible de +10 Ct en el IVA . No puedes añadir más")
           try:
               amount_tax = float(amount_tax) + 0.01
               self.amount_tax = float(amount_tax)
               self.amount_total = float(amount_untaxed) + float(amount_tax)
               self.totalesmanuales = True
               self.redondeoiva += 0.01
           except:
               amount_tax = amount_tax
               raise AccessError("Ha habido algun error al Realizar la operacion")
           return {}


     def rest1centiva(self):
           amount_tax = self.amount_tax
           amount_total = self.amount_total
           amount_untaxed = self.amount_untaxed
           redondeoiva = self.redondeoiva
           if redondeoiva < -0.09:
               raise UserError("El Redondeo Excede el límite posible de -10 Ct en el IVA . No puedes quitar más")
           try:
               amount_tax = float(amount_tax) - 0.01
               self.amount_tax = float(amount_tax)
               self.amount_total = float(amount_untaxed) + float(amount_tax)
               self.totalesmanuales = True
               self.redondeoiva += -0.01
           except:
               amount_tax = amount_tax
               raise AccessError("Ha habido algun error al Realizar la operacion")
           return {}



     def crearectificasubtotal(self):
           amount_total = self.amount_untaxed
           modorecti = self.modorecti
           if str(modorecti) == "False":
              raise AccessError("Debes Escoger un Modo de Rectificativa")
              return {}
           amount_rect = self.rectificasubtotal
           mifactid = self.id
           numberfact = self.number
           partner_id = self.partner_id.id
           expedienteid = self.expediente.id
           crearect_obj = self.env['account.invoice']
           hoy = date.today()
           importe2 = self.rectificasubtotal
           importe = amount_total - importe2
           importep = importe2 - amount_total
           importtesiniva = importe 
           importeiva = importep * 0.0400001
           if importe > 0:
              raise AccessError("EL Valor de la Rectificativa es Positivo: " + str(importe) + ". Solo se permite Valores Negativos a Proveedores")
              return {}
           if str(modorecti) == "total":
              ## raise AccessError("Este es el MODO SCOBY :: EL Sistema generará una Factura Provisional por: " + str(importe2) + ". Otra contrafactura de Abono por: -" + str(importe2) + " y dejará la actual como Definitiva por: " + str(amount_total) + "")
              lineinvoice1 = [(0,0, {'name': "Abono Provisional Compra Mercaderías",'plantilla': 869,'variedad': 320,'product_id': 229,'quantity': 1,'price_unit': importe2,'invoice_line_tax_ids': [(4, 21)],'account_id': 363,})]
              lineinvoice2 = [(0,0, {'name': "Provisional Compra Mercaderías",'plantilla': 869,'variedad': 320,'product_id': 229,'quantity': 1,'price_unit': -importe2,'invoice_line_tax_ids': [(4, 21)],'account_id': 363,})]
              invoice1 = crearect_obj.create({'origin': "Abono Provisional de: " + str(numberfact) + " ",'account_id': 443,'invoice_line_ids': lineinvoice2,'journal_id': 17,'expediente': expedienteid,'partner_id': partner_id})
              invoice1 = int(invoice1[0])
              invoice2 = crearect_obj.create({'origin': "Provisional de: " + str(numberfact) + " ",'account_id': 443,'invoice_line_ids': lineinvoice1,'journal_id': 17,'expediente': expedienteid,'partner_id': partner_id})
              invoice2 = int(invoice2[0])
              self.write({'rectificafactres': invoice1,'rectificafactres2': invoice2,'rectificasubtotal': 0})
              return {}
           ## raise AccessError("EL Importe de la Rectificativa es: " + str(importep) + "")
           if str(modorecti) == "diferencia":
             base1 = False
             amounttaxt = False
             for invoicetax in self.tax_line_ids:
               baseid = invoicetax.tax_id.id
               base = 0
               if baseid == 21:
                  base = invoicetax.base
                  amounttax = invoicetax.amount
                  base = invoicetax.base
                  base1 = base + importeiva
                  amounttaxt = amounttax + importeiva
                  ## print("Base: " + str(base1))
                  ## invoicetax.update({'base':base1})
             if base1 != False and amounttaxt != False:
                lineaiva = self.env['account.invoice.tax'].search([('invoice_id', '=', mifactid),('tax_id','=',21)], order='id', limit=1)
                lineaiva.update({'amount': amounttaxt, 'base': base1})
                ## raise AccessError("La ID de Linea: " + str(lineaiva) + ". La Base del Nuevo IVA es: " + str(base1) + ". La base anterior era: " + str(base) + " IMporte IVA: " + str(amounttax) + " Importe Despues: " + str(amounttaxt) + " EL incremento es de " + str(importeiva) + "")
             lineinvoice = [(0,0, {
                        'name': "Rectificación Compra Mercaderías",
                        'plantilla': 869,
                        'variedad': 320,
                        'product_id': 229,
                        'quantity': 1,
                        'price_unit': importtesiniva,
                        'invoice_line_tax_ids': [(4, 21)],
                        'account_id': 363,})]
             invoice = crearect_obj.create({
                      'origin': "Rectificativa de: " + str(numberfact) + " ",
                      ## 'dateinv_compra': hoy,
                      'account_id': 443,
                      'journal_id': 17,
                      'expediente': expedienteid,
                      'invoice_line_ids': lineinvoice,
                      'partner_id': partner_id})
             invoice = int(invoice[0])
             lineinvoicep = [(0,0, {
                        'name': "Rectificación Compra Mercaderías",
                        'plantilla': 869,
                        'variedad': 320,
                        'product_id': 229,
                        'quantity': 1,
                        'price_unit': importep,
                        'invoice_line_tax_ids': [(4, 21)],
                        'account_id': 363,})]
           self.write({'rectificafactres': invoice,'invoice_line_ids': lineinvoicep,'rectificasubtotal': 0})


     def capturarlineascompraca(self):
           partner = self.partner_id.id
           id = self.id
           self.write({'pteimportarcompra': 'PTE'})
           return {
           'name': ("Albaranes Compra"),
           'type': 'ir.actions.act_window',
           'res_model': 'account.invoice.line',
           'view_mode': 'tree,form',
           'view_type': 'form',
           ## 'view_id': record_id,
           'target': 'current',
           'domain': [('diariofactura','=', 9),('factcompradestino','=', False),('partner_id','=',partner)],
           }




     def importarlineascompra(self):
           id = self.id
           partner = self.partner_id.id
           if str(partner) == "False":
                      raise UserError("No has seleccionado el PROVEEDOR en el documento")
           fecha = datetime.today()
           orderline_obj = self.env['jovimer_preparaalbaranc']
           invoice = orderline_obj.create({
                   'name': id,
                   'partner': partner,				   
                   'fecha': fecha, })
           invoice = int(invoice[0])
           return {
           'name': ("Importar Lineas Compra"),
           'type': 'ir.actions.act_window',
           'res_model': 'jovimer_preparaalbaranc',
           'view_mode': 'form',
           'view_type': 'form',
           'res_id': invoice,
           'target': 'new',
           'domain': [('partner_id','=',partner)],
           }


     def importarlineasalbaranesc(self):
           id = self.id
           partner = self.partner_id.id
           raise UserError("Solo el Usuario ADMIN puede Utilizar este Servicio") 
           return {}





     def importarlineasalbaran(self):
           id = self.id
           partner = self.partner_id.id
           if str(partner) == "False":
                      raise UserError("No has seleccionado el CLIENTE en el documento")
           fecha = datetime.today()
           orderline_obj = self.env['jovimer_preparafacturav']
           invoice = orderline_obj.create({
                   'name': id,
                   'partner': partner,				   
                   'fecha': fecha, })
           invoice = int(invoice[0])
           return {
           'name': ("Importar Lineas Venta"),
           'type': 'ir.actions.act_window',
           'res_model': 'jovimer_preparafacturav',
           'view_mode': 'form',
           'view_type': 'form',
           'res_id': invoice,
           'target': 'new',
           }


     def importarlineasventa(self):
           id = self.id
           partner = self.partner_id.id
           if str(partner) == "False":
                      raise UserError("No has seleccionado el CLIENTE en el documento")
           fecha = datetime.today()
           orderline_obj = self.env['jovimer_preparaalbaranv']
           invoice = orderline_obj.create({
                   'name': id,
                   'partner': partner,				   
                   'fecha': fecha, })
           invoice = int(invoice[0])
           return {
           'name': ("Importar Lineas Venta"),
           'type': 'ir.actions.act_window',
           'res_model': 'jovimer_preparaalbaranv',
           'view_mode': 'form',
           'view_type': 'form',
           'res_id': invoice,
           'target': 'new',
           }

     def importarlineasalmacen(self):
           id = self.id
           partner = self.partner_id.id
           if str(partner) == "False":
                      raise UserError("No has seleccionado el CLIENTE en el documento")
           fecha = datetime.today()
           orderline_obj = self.env['jovimer_preparaalmalbaranv']
           invoice = orderline_obj.create({
                   'name': id,
                   'partner': partner,				   
                   'fecha': fecha, })
           invoice = int(invoice[0])
           return {
           'name': ("Importar Lineas Venta"),
           'type': 'ir.actions.act_window',
           'res_model': 'jovimer_preparaalmalbaranv',
           'view_mode': 'form',
           'view_type': 'form',
           'res_id': invoice,
           'target': 'new',
           }


     def jovimer_view_lineasalbaran(self, context=None):
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




     def capturarlineascompra(self):
           partner = self.partner_id.id
           id = self.id
           self.write({'pteimportarcompra': 'PTE'})
           ## raise AccessError("EL CLiente es: " + str(partner) + ". Con ID: " + str(id)+ ".")
		   
           return {
           'name': ("Lineas de Compra"),
           'type': 'ir.actions.act_window',
           'res_model': 'purchase.order.line',
           'view_mode': 'tree,form',
           'view_type': 'form',
           ## 'view_id': record_id,
           'target': 'current',
           'domain': [('lineafacturacompra','=', False),('partner_id','=',partner)],
           }


     def anyadirlinprov(self):
           partner = self.partner_id.id
           id = self.id
           ## raise AccessError("EL CLiente es: " + str(partner) + ". Con ID: " + str(id)+ ".")
		   
           return {
           'name': ("Lineas de Compra"),
           'type': 'ir.actions.act_window',
           'res_model': 'account.invoice.line',
           'view_mode': 'tree,form',
           'view_type': 'form',
           ## 'view_id': record_id,
           'target': 'current',
           'domain': [('invoice_id.journal_id','=', 9)],
           }


     def anyadirlinasig(self):
           ## id = str(self.id)
           ## args = ["/opt/jovimer12/bin/cuentaventarepasado.bash", id, "&"]
           ## subprocess.call(args)
           if str(self.buscaasignacion.id) == "False":
                      raise UserError("Debes escoger una linea editando el presente documento en el desplegable anterior a este boton")
           id = self.id
           partner = self.partner_id.id
           buscaasignacion = str(self.buscaasignacion.id)
           lineacompra = self.buscaasignacion.id
           ## PLANTILLA
           self.env.cr.execute(""" select plantilla from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           plantilla = result[0]
           ## PRODUCTO
           self.env.cr.execute(""" select product_id from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           producto = result[0]
           ## VARIEDAD
           self.env.cr.execute(""" select variedad from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           variedad = result[0]
           ## CALIBRE
           self.env.cr.execute(""" select calibre from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           calibre = result[0]
           ## CATEGORIA
           self.env.cr.execute(""" select categoria from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           categoria = result[0]
           ## CONFECCION
           self.env.cr.execute(""" select confeccion from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           confeccion = result[0]
           ## ENVASE
           self.env.cr.execute(""" select envase from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           envase = result[0]
           ## MARCA
           self.env.cr.execute(""" select marca from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           marca = result[0]
           ## BULTOS
           self.env.cr.execute(""" select bultos from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           bultos = result[0]
           ## KGNETBULTO
           self.env.cr.execute(""" select kgnetbulto from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           kgnetbulto = result[0]
           ## EXPEDIENTE
           self.env.cr.execute(""" select expediente from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           expediente = result[0]
           ## CANTIDADPEDIDO
           self.env.cr.execute(""" select cantidadpedido from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           cantidadpedido = result[0]		   
           ## TOTALBULTOS
           totalbultos = float(cantidadpedido) * float(bultos)
           ## UNIDADPEDIDO
           self.env.cr.execute(""" select unidadpedido from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           unidadpedido = result[0]	
           ## UNIDABULTO
           self.env.cr.execute(""" select product_uom from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           unidabulto = result[0]	
           ## UNIDADESPORBULTO
           self.env.cr.execute("""  select unidadesporbulto from jovimer_confeccion where id in (select confeccion from purchase_order_line where id='%s')""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           unidadesporbulto = result[0]	
           today = date.today()
           d1hoy = today.strftime("%Y-%m-%d")
           orderline_obj = self.env['account.invoice.line']
           quantity = 0
           if unidabulto == 24:
              quantity = float(cantidadpedido) * float(bultos)
           ## KG
           if unidabulto == 27:
              quantity = float(cantidadpedido) * float(bultos) * float(kgnetbulto)
           ## Unidades
           if unidabulto == 1:
              quantity = float(cantidadpedido) * float(bultos) * float(unidadesporbulto)
           invoice = orderline_obj.create({
                   'invoice_id': id,
                   'partner_id': partner,
                   'product_id': producto,
                   'account_id': 1,
                   'price_unit': 0,
                   'quantity': quantity,
                   'plantilla': plantilla,
                   'variedad': variedad,
                   'calibre': calibre,
                   'categoria': categoria,
                   'confeccion': confeccion,
                   'envase': envase,
                   'marca': marca,
                   'bultos': bultos,
                   'kgnetbulto': kgnetbulto,
                   'totalbultos': totalbultos,
                   'expediente': expediente,
                   'cantidadpedido': cantidadpedido,				   
                   'unidadpedido': unidadpedido,
                   'unidabulto': unidabulto,
                   'lineacompra': lineacompra,
				   'unidadesporbulto': unidadesporbulto,
                   'asignado': True,
                   'currency_id': 1, })
		   ## raise UserError("Voy a Asignar: " + str(buscaasignacion) + " a la linea " + str(idline) + " que pertenece a la Fcatura: " + str(idfact) + ".")
           self.write({'buscaasignacion': False}) 
           return {} 



     def anyadirlinasigp(self):
           ## id = str(self.id)
           ## args = ["/opt/jovimer12/bin/cuentaventarepasado.bash", id, "&"]
           ## subprocess.call(args)
           if str(self.buscaasignacionp.id) == "False":
                      raise UserError("Debes escoger una linea editando el presente documento en el desplegable anterior a este boton")
           id = self.id
           partner = self.partner_id.id
           buscaasignacion = str(self.buscaasignacionp.id)
           lineacompra = self.buscaasignacionp.id
           ## PLANTILLA
           self.env.cr.execute(""" select plantilla from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           plantilla = result[0]
           ## PRODUCTO
           self.env.cr.execute(""" select product_id from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           producto = result[0]
           ## VARIEDAD
           self.env.cr.execute(""" select variedad from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           variedad = result[0]
           ## CALIBRE
           self.env.cr.execute(""" select calibre from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           calibre = result[0]
           ## CATEGORIA
           self.env.cr.execute(""" select categoria from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           categoria = result[0]
           ## CONFECCION
           self.env.cr.execute(""" select confeccion from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           confeccion = result[0]
           ## ENVASE
           self.env.cr.execute(""" select envase from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           envase = result[0]
           ## MARCA
           self.env.cr.execute(""" select marca from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           marca = result[0]
           ## BULTOS
           self.env.cr.execute(""" select bultos from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           bultos = result[0]
           ## KGNETBULTO
           self.env.cr.execute(""" select kgnetbulto from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           kgnetbulto = result[0]
           ## EXPEDIENTE
           self.env.cr.execute(""" select expediente from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           expediente = result[0]
           ## CANTIDADPEDIDO
           self.env.cr.execute(""" select cantidadpedido from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           cantidadpedido = result[0]		   
           ## TOTALBULTOS
           totalbultos = float(cantidadpedido) * float(bultos)
           ## UNIDADPEDIDO
           self.env.cr.execute(""" select unidadpedido from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           unidadpedido = result[0]	
           ## UNIDABULTO
           self.env.cr.execute(""" select product_uom from purchase_order_line where id='%s'""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           unidabulto = result[0]	
           ## UNIDADESPORBULTO
           self.env.cr.execute("""  select unidadesporbulto from jovimer_confeccion where id in (select confeccion from purchase_order_line where id='%s')""" % (buscaasignacion))
           result = self.env.cr.fetchone()
           unidadesporbulto = result[0]	
           today = date.today()
           d1hoy = today.strftime("%Y-%m-%d")
           orderline_obj = self.env['account.invoice.line']
           quantity = 0
           if unidabulto == 24:
              quantity = float(cantidadpedido) * float(bultos)
           ## KG
           if unidabulto == 27:
              quantity = float(cantidadpedido) * float(bultos) * float(kgnetbulto)
           ## Unidades
           if unidabulto == 1:
              quantity = float(cantidadpedido) * float(bultos) * float(unidadesporbulto)
           invoice = orderline_obj.create({
                   'invoice_id': id,
                   'partner_id': partner,
                   'product_id': producto,
                   'account_id': 1,
                   'price_unit': 0,
                   'quantity': quantity,
                   'plantilla': plantilla,
                   'variedad': variedad,
                   'calibre': calibre,
                   'categoria': categoria,
                   'confeccion': confeccion,
                   'envase': envase,
                   'marca': marca,
                   'bultos': bultos,
                   'kgnetbulto': kgnetbulto,
                   'totalbultos': totalbultos,
                   'expediente': expediente,
                   'cantidadpedido': cantidadpedido,				   
                   'unidadpedido': unidadpedido,
                   'unidabulto': unidabulto,
                   'lineacompra': lineacompra,
                   'unidadesporbulto': unidadesporbulto,
                   'asignado': True,
                   'currency_id': 1, })
           invoice = int(invoice[0])
           ## raise UserError("Voy a Asignar: " + str(buscaasignacion) + " a la linea " + str(idline) + " que pertenece a la Fcatura: " + str(idfact) + ".")
           self.write({'buscaasignacionp': False}) 
           self.env.cr.execute("""  UPDATE  purchase_order_line SET lineafacturacompra='%s' where id='%s'""" % (str(id),str(buscaasignacion)))
           ## self.env.cr.execute("""  UPDATE  account_invoice_line SET qyantity='%s' where id='%s'""" % (str(quantity),str(invoice)))
           return {} 



     def action_afactura(self, default=None):
           ## self.write({'state': 'open'})
           factura = self.id
           for lineas in self.invoice_line_ids:
             priceunit = lineas.price_unit
             prodname = lineas.name
             if priceunit == 0:
               raise AccessError("La Linea de " + str(prodname) + " tiene el precio a 0. Se debe indicar un precio para poder continuar")
           refcliente = self.refcliente
           pais = self.partner_id.country_id.id
           if pais == 257 or pais == 68:
               ## journalid = 13
               journalid = 36
           else:		   
               ## journalid = 24
               journalid = 35
           journal_partner = self.partner_id.seriefacturasvta.id
           if journal_partner != False:
              journalid = journal_partner
           origen = self.number
           dateinv = self.date_invoice
           fechallegada = self.expediente.fechallegada
           fechasalida = self.expediente.fechasalida
           origencom = str(origen) + ' Dates:  Departure ' + str(fechasalida) + ', Arrival ' + str(fechallegada) 
           default.update({
           'journal_id': journalid,
           'refcliente': refcliente,
           'origin': str(origencom),
           'number': '',
           'move_name': '',
           'state': 'draft'})
           ## super(ModelAccountInvoice, self).copy(default)
           nuevafact = super(ModelAccountInvoice, self).copy(default)
           hoy = datetime.today()
           ### print(">>>>>>>> Nueva Fcat: " + str(nuevafact.id) + " para " + str(hoy) + ".")
           self.write({'docresultante': nuevafact.id,'albaranfacturado': True,'albaranfacturado': True,'fechaalbaranfacturado': hoy,'state': 'open'})
           ## self.write({'albaranfacturado': True})           
           ## self.write({'fechaalbaranfacturado': hoy})
           return {}

     ## @api.onchange('fiscal_position_id')
     def recalcimpuestos(self):

        ## invoice = self    
        invoiceid = self.id
        fiscalposition = self.fiscal_position_id.id
        ## raise UserError("La Factura es: " + str(invoiceid) + "")
        ## act = self.get_taxes_values()
        for line in self.tax_line_ids:
               line._compute_base_amount
        ### for line in self.line_ids:
        ###     line._onchange_product_id()
        ###     line._onchange_debit()
        ###     line._onchange_credit()
        """Function used in other module to compute the taxes on a fresh invoice created (onchanges did not applied)"""
        account_invoice_tax = self.env['account.invoice.tax']
        ctx = dict(self._context)
        for invoice in self:
            # Delete non-manual tax lines
            self._cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=" + str(invoiceid)  + " AND manual is False")
            if self._cr.rowcount:
                self.invalidate_cache()
        if str(fiscalposition) == "1":
            # Generate one tax line per tax, however many invoice lines it's applied to
            tax_grouped = invoice.get_taxes_values()

            # Create new tax lines
            for tax in tax_grouped.values():
                account_invoice_tax.create(tax)
        ### self._recompute_tax_lines()

        totalmanual = self.totalesmanuales
        self.redondeobase = 0
        self.redondeoiva = 0
        self.totalesmanuales = False

        return {}


     def action_afacturac(self, default=None):
           factura = self.id
           partneridc = self.partner_id.id
           payment_term_id = self.partner_id.property_supplier_payment_term_id.id
           fiscal_position_id = self.partner_id.property_account_position_id.id
           if str(fiscal_position_id) == "False":
              fiscal_position_id = 1
           if str(payment_term_id) == "False":
              payment_term_id = 5
           ## raise UserError("EL Modo de Pago es: " + str(payment_term_id) + ", y la Posicion Fiscal es: " + str(fiscal_position_id) + ".")
           ## self.env.cr.execute(""" select count(*) from account_invoice_line where invoice_id='%s' and ctavtafin is NULL """ % (factura))
           self.env.cr.execute(""" select count(*) from account_invoice_line where invoice_id='%s' and ctavtarepasado is NULL """ % (factura))
           result = self.env.cr.fetchone()
           contador = result[0]
           if str(contador) != "0":            
               raise AccessError("Existen " + str(contador) + " lineas de Cuentas de Venta No repasadas y/o enviadas. NO se puede Facturar ")
               return {}
           else: 
               self.write({'state': 'open'})
               ## self.write({'type_sale': 'aalbaran'})
               ## Buscamos la default
               ## self.env.cr.execute("""select id from sale_order_type where type_doc='Albaran' ORDER BY id DESC LIMIT 1""")
               ## resultp = self.env.cr.fetchone()
               ## tipoped = resultp[0]
               ## default = dict(default or {})
               hoy = datetime.today()               
               journalid = 16
               origen = self.number
               refcliente = self.refcliente
               dateinv = self.date_invoice
               origencom = 'Albaran: ' + str(self.reference) + '. Fecha: ' + str(dateinv)
               referencecom = 'Albaran: ' + str(self.reference) + ' '		   
               default.update({
               'journal_id': journalid,
               'refcliente': ' ' + str(refcliente) + ' ',
               'payment_term_id': payment_term_id,
               'fiscal_position_id': fiscal_position_id,
               'origin': str(origencom),
               ## 'reference': str(referencecom),		   
               'number': '',
               'account_id': 188,
               'move_name': '',
               'dateinv': hoy,
               'state': 'draft'})
               nuevafact = super(ModelAccountInvoice, self).copy(default)
               facturarc = nuevafact.id
               ### print(">>>>>>>> Nueva Fcat: " + str(nuevafact.id) + " para " + str(hoy) + ".")
               self.write({'docresultante': nuevafact.id})
               self.write({'albaranfacturado': True})           
               self.write({'fechaalbaranfacturado': hoy})
               url = "/web?debug#id=" + str(facturarc) + "&model=account.invoice&view_type=form&menu_id=656"
               ### return {
               ###    'name': 'Nueva Factura Creada desde Albarán',
               ###    'res_model': 'ir.actions.act_url',
               ###    'type': 'ir.actions.act_url',
               ###    'url':  url,
               ###    'target' : 'self'
               ###    }

               ## return {}
               ### sleep(1)
               return {
                      'name': ("Nueva Factura Proveedor"),
                      'type': 'ir.actions.act_window',
                      'res_model': 'account.invoice',
                      'view_mode': 'form,tree',
                      'res_id': facturarc,
                      'view_type': 'form',
                      ## 'view_id': record_id,
                      'target': 'current',
                      ## 'domain': [('id','=', facturarc)],
                      'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'},
                      }

           		 
     def action_crearectificativa(self, default=None):
           ## raise AccessError("Aqui estas")
           ## self.write({'state': 'open'})
           ## self.write({'type_sale': 'aalbaran'})
           ## Buscamos la default
           ## self.env.cr.execute("""select id from sale_order_type where type_doc='Albaran' ORDER BY id DESC LIMIT 1""")
           ## resultp = self.env.cr.fetchone()
           ## tipoped = resultp[0]
           ## default = dict(default or {})
           ## journalid = 15
           journalid = 41
           origen = self.number
           refcliente = self.refcliente
           dateinv = self.date_invoice
           origencom = str(origen) + '. Fecha: ' + str(dateinv)
           default.update({
           'journal_id': journalid,
           'refcliente': 'RECT: ' + str(refcliente),
           'origin': str(origencom),
           'number': '',
           'traspasocont': False,
           'traspasocontfecha': False,
           'move_name': '',
           'state': 'draft'})
           factrect = super(ModelAccountInvoice, self).copy(default)		   
           self.env.cr.execute(""" select id from ir_ui_view where name LIKE '%Pyme - Albaranes / Facturas Clientes%' and type='form' ORDER BY id DESC LIMIT 1""")
           result = self.env.cr.fetchone()
           record_id = int(result[0])
           view =  {
                     'name': ("Nueva Factura Rectificativa"),
                     'type': 'ir.actions.act_window',
                     'res_model': 'account.invoice',
                     'view_mode': 'form',
                     'res_id': factrect.id,
                     'view_type': 'form',
                     'view_id': record_id,
                     'target': 'current',}
           return view          

     def action_crearectificativaextra(self, default=None):
           ## raise AccessError("Aqui estas")
           ## self.write({'state': 'open'})
           ## self.write({'type_sale': 'aalbaran'})
           ## Buscamos la default
           ## self.env.cr.execute("""select id from sale_order_type where type_doc='Albaran' ORDER BY id DESC LIMIT 1""")
           ## resultp = self.env.cr.fetchone()
           ## tipoped = resultp[0]
           ## default = dict(default or {})
           ## journalid = 22
           journalid = 44
           origen = self.number
           dateinv = self.date_invoice
           origencom = str(origen) + '. Fecha: ' + str(dateinv)
           default.update({
           'journal_id': journalid,
           'refcliente': '',
           'origin': str(origencom),
           'number': '',
           'traspasocont': False,
           'traspasocontfecha': False,
           'move_name': '',
           'state': 'draft'})
           super(ModelAccountInvoice, self).copy(default)		   
           return {} 



     def action_crearectificativanacompra(self, default=None):
           ## raise AccessError("Aqui estas")
           ## self.write({'state': 'open'})
           ## self.write({'type_sale': 'aalbaran'})
           ## Buscamos la default
           ## self.env.cr.execute("""select id from sale_order_type where type_doc='Albaran' ORDER BY id DESC LIMIT 1""")
           ## resultp = self.env.cr.fetchone()
           ## tipoped = resultp[0]
           ## default = dict(default or {})
           journalid = 17
           origen = self.number
           dateinv = self.date_invoice
           origencom = str(origen) + '. Fecha: ' + str(dateinv)
           default.update({
           'journal_id': journalid,
           'refcliente': '',
           'origin': 'Abono:' + str(origencom),
           'number': '',
           'traspasocont': False,
           'traspasocontfecha': False,
           'move_name': '',
           'state': 'draft'})
           super(ModelAccountInvoice, self).copy(default)		   
           return {}


     def action_crearectificativanacomprayab(self, default=None):
           ## raise AccessError("Aqui estas")
           ## self.write({'state': 'open'})
           ## self.write({'type_sale': 'aalbaran'})
           ## Buscamos la default
           ## self.env.cr.execute("""select id from sale_order_type where type_doc='Albaran' ORDER BY id DESC LIMIT 1""")
           ## resultp = self.env.cr.fetchone()
           ## tipoped = resultp[0]
           ## default = dict(default or {})
           journalid = 17
           facturaactual = self.id,
           origen = self.number
           dateinv = self.date_invoice
           origencom = str(origen) + '. Fecha: ' + str(dateinv)
           default.update({
           'journal_id': journalid,
           'refcliente': '',
		   'cadenafactcomprar': facturaactual,
           'origin': "Abono: " + str(origencom),
           'number': '',
           'traspasocont': False,
           'traspasocontfecha': False,
           'move_name': '',
           'state': 'draft'})
           super(ModelAccountInvoice, self).copy(default)		   

           journalid = 17
           origen = self.number
           dateinv = self.date_invoice
           origencom = str(origen) + '. Fecha: ' + str(dateinv)
           default.update({
           'journal_id': journalid,
           'refcliente': '',
           'origin': "Definitiva: " + str(origencom),
           'number': '',
           'traspasocont': False,
           'traspasocontfecha': False,
           'move_name': '',
           'state': 'draft'})
           super(ModelAccountInvoice, self).copy(default)
           return {}




     def action_crearectificativanac(self, default=None):
           ## raise AccessError("Aqui estas")
           ## self.write({'state': 'open'})
           ## self.write({'type_sale': 'aalbaran'})
           ## Buscamos la default
           ## self.env.cr.execute("""select id from sale_order_type where type_doc='Albaran' ORDER BY id DESC LIMIT 1""")
           ## resultp = self.env.cr.fetchone()
           ## tipoped = resultp[0]
           ## default = dict(default or {})
           ## journalid = 20
           journalid = 40
           origen = self.number
           dateinv = self.date_invoice
           origencom = str(origen) + '. Fecha: ' + str(dateinv)
           default.update({
           'journal_id': journalid,
           'refcliente': '',
           'origin': str(origencom),
           'number': '',
           'traspasocont': False,
           'traspasocontfecha': False,
           'move_name': '',
           'state': 'draft'})
           super(ModelAccountInvoice, self).copy(default)		   
           return {}          


     def action_crearectificativasrv(self, default=None):
           ## raise AccessError("Aqui estas")
           ## self.write({'state': 'open'})
           ## self.write({'type_sale': 'aalbaran'})
           ## Buscamos la default
           ## self.env.cr.execute("""select id from sale_order_type where type_doc='Albaran' ORDER BY id DESC LIMIT 1""")
           ## resultp = self.env.cr.fetchone()
           ## tipoped = resultp[0]
           ## default = dict(default or {})
           ## journalid = 21
           journalid = 43
           origen = self.number
           dateinv = self.date_invoice
           origencom = str(origen) + '. Fecha: ' + str(dateinv)
           default.update({
           'journal_id': journalid,
           'refcliente': '',
           'origin': str(origencom),
           'number': '',
           'traspasocont': False,
           'traspasocontfecha': False,
           'move_name': '',
           'state': 'draft'})
           super(ModelAccountInvoice, self).copy(default)		   
           return {}   




     def action_crearectificativac(self, default=None):
           ## raise AccessError("Aqui estas")
           ## self.write({'state': 'open'})
           ## self.write({'type_sale': 'aalbaran'})
           ## Buscamos la default
           ## self.env.cr.execute("""select id from sale_order_type where type_doc='Albaran' ORDER BY id DESC LIMIT 1""")
           ## resultp = self.env.cr.fetchone()
           ## tipoped = resultp[0]
           ## default = dict(default or {})
           journalid = 17
           origen = self.number
           dateinv = self.date_invoice
           origencom = str(origen) + '. Fecha: ' + str(dateinv)
           default.update({
           'journal_id': journalid,
           'refcliente': '',
           'origin': str(origencom),
           'number': '',
           'traspasocont': False,
           'traspasocontfecha': False,		   
           'move_name': '',
           'state': 'draft'})
           super(ModelAccountInvoice, self).copy(default)		   
           return {} 



     def recalculatotal(self):
          round_curr = self.currency_id.round
          self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
          self.amount_tax = sum(round_curr(line.amount) for line in self.tax_line_ids)
          self.amount_total = self.amount_untaxed + self.amount_tax


     def quitapendiente(self):
           self.write({'ctavtacompleto': False})


     def creapendiente(self):
           self.write({'ctavtacompleto': True})
           self.write({'sent': False})
           self.write({'fechactavtaenviado': False})

     def quitarmarcactaimpresayenviada(self):
           today = date.today()
           d1hoy = today.strftime("%Y-%m-%d")
           self.write({'sent': False})
           self.write({'fechactavtaenviado': False})


     def enviarctvta(self):
           today = date.today()
           d1hoy = today.strftime("%Y-%m-%d")
           usuario = self.env.user.id
           invoice_id = self.id
           print("\n\n ")
           if usuario == 20 or usuario ==  29:
                 print("Continuamos con la cuenta de venta...")
           else:
                 raise AccessError("Solo el Usuario Anaïs Reig y Juani Nules pueden enviar Cuentas de Venta")
           ## if usuario != 20:

           ## for lines in self.invoice_line_ids:
           for lines in self.env['account.invoice.line'].search([('invoice_id','=',invoice_id),('asignaroriginal','=',False)]):
               asignaroriginal = lines.asignaroriginal
               asignarmadre = lines.asignarmadre
               nameprod = lines.variedad.name
               valorcvvta = lines.valorcvvta
               pvpcvvta = lines.pvpcvvta
               idline = lines.id
               ## if pvpcvvta == 0 or valorcvvta == 0:
               ##   raise AccessError("La Linea MADRE de " + str(nameprod) + " tiene valores 0 en Precio Cuenta Venta o Valor Total de Cuenta de Venta en la Linea")
               print("La linea " + str(idline) + " El Valor es: " + str(valorcvvta) + "")
           ## raise AccessError("Voy a enviar la cuenta de venta " + str(invoice_id) + "")
           args = ["/opt/jovimer12/bin/buscacuentasdeventa_individual.sh", str(invoice_id), "&"]
           subprocess.call(args)
           print("\n\n ")
           
     def enviarctvtano(self):
           today = date.today()
           d1hoy = today.strftime("%Y-%m-%d")
           raise AccessError("Falta alguna linea por repasar y/o no esta completo")

          
     def marcactaimpresayenviada(self):
           factura = self.id
           self.env.cr.execute(""" select count(*) from account_invoice_line where invoice_id='%s' and ctavtarepasado is NULL """ % (factura))
           result = self.env.cr.fetchone()
           contador = result[0]
           if str(contador) != "0":            
               raise AccessError("Existen " + str(contador) + " lineas de Cuentas de Venta No repasadas. NO se puede Marcar como Enviado.")
               return {}
           else: 
               today = date.today()
               d1hoy = today.strftime("%Y-%m-%d")
               self.write({'sent': True})
               self.write({'fechactavtaenviado': d1hoy})
           return {}




     def recalcular_amount_pyme(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id
            amount_total_company_signed = currency_id._convert(self.amount_total, self.company_id.currency_id, self.company_id, self.date_invoice or fields.Date.today())
            amount_untaxed_signed = currency_id._convert(self.amount_untaxed, self.company_id.currency_id, self.company_id, self.date_invoice or fields.Date.today())
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

     def recalcular_sign_taxes_pyme(self):
        for invoice in self:
            sign = invoice.type in ['in_refund', 'out_refund'] and -1 or 1
            invoice.amount_untaxed_invoice_signed = invoice.amount_untaxed * sign
            invoice.amount_tax_signed = invoice.amount_tax * sign

     def recalculaimpfactcompra(self):
        for invoice in self:
            if str(invoice.modologocontamercasp) == "True":
                        amotot = invoice.amount_untaxed
                        invoice.write({'amount_tax': 0})
                        invoice.write({'amount_total': amotot})
            if str(invoice.modologocontamercain) == "True":
                        amotot = invoice.amount_untaxed
                        invoice.write({'amount_tax': 0})
                        invoice.write({'amount_total': amotot})




     
class ModelAccountInvoiceLine(models.Model):
     
     # Herencia de la tabla de ventas
     _inherit = 'account.invoice.line'

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
                invoice_id = rec.invoice_id.id
                asignarmadre = rec.id
                if original == False:
                   subtotalasignado = rec.price_subtotal
                   try:
                      self.env.cr.execute(""" select sum(price_subtotalas) from account_invoice_line where invoice_id='%s' and asignarmadre='%s' """ % (invoice_id,asignarmadre))
                      result = self.env.cr.fetchone()
                      subtotalasignado = result[0] or 0.0
                   except:
                      subtotalasignado = 0
                   ## subtotalasignado = sum(rec.price_subtotalas)
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
                       pvpcvvta = ( valorcvvta * dto2 ) / cantidadoriginal
                    except:
                       pvpcvvta = 0
                rec.pvpcvvta = pvpcvvta
  
  
  
     expediente = fields.Many2one('jovimer_expedientes', string='Exp. Destino', domain=[('serie','in',(1,3,4,12))])  
     expediente_origen = fields.Integer(string='Número', help='Número Expediente', related='invoice_id.expediente.name')     
     expediente_serie = fields.Selection('jovimer_expedientes', related='expediente.campanya')
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')     
     fechasalida = fields.Date('jovimer_expedientes', related='expediente.fechasalida')
     fechallegada= fields.Date('jovimer_expedientes', related='expediente.fechallegada')
     clientefinal= fields.Many2one('res.partner', related='expediente.cliente')
     cantidadpedido = fields.Float(string='Palets' )  
     unidadpedido = fields.Many2one('uom.uom', string='Tipo', domain=[('invisiblecp','=','SI')])  
     bultos = fields.Float(string='Bultos')  
     unidabulto = fields.Many2one('uom.uom', string='Ud. NO FUN')
     plantilla = fields.Many2one('jovimer_plantillaproductos', string='Plantilla de Producto')
     codproducto = fields.Char(string='Codigo Cliente', related='plantilla.codproducto', Store=True)
     precioplantilla = fields.Float(string='Precio Plantilla', related='plantilla.pvpvta')
     precioudplantilla = fields.Many2one('uom.uom',string='Ud Plantilla', related='plantilla.pvptipo')
     variedad = fields.Many2one('jovimer_variedad', string='Variedad')
     variedadeng = fields.Char(string='Traduccion', related='variedad.abrev')
     calibre = fields.Many2one('jovimer_calibre', string='Calibre')
     categoria = fields.Many2one('jovimer_categoria', string='Categoria')
     confeccion = fields.Many2one('jovimer_confeccion', string='Confección')
     envase = fields.Many2one('jovimer_envase', string='Envase')
     envasecod = fields.Char(string='Envase Codigo', related='envase.codigo')
     marca = fields.Many2one('jovimer_marca', string='Marca')
     name  = fields.Char(string='Nombre')
     nocalcbultos = fields.Boolean(string='No Calcula Bultos')
     unidabulto = fields.Many2one('uom.uom', string='Unidad', domain=[('invisibleudvta','=','SI')])
     kgnetbulto = fields.Float(string='Kg/Net Bulto', store=True)
     totalbultos = fields.Float(string='Total Bultos', store=True)
     quedanbultos = fields.Float(string='Quedan', store=True)
     udfacturacion = fields.Many2one('uom.uom', string='Ud Albaran/Factura', related='plantilla.udfacturacion')	 
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
     product = fields.Many2one('product.product', string='Producto')
     pvpcoste = fields.Float(string='Coste') 
     pvptipo = fields.Many2one('uom.uom', string='PVP/Tipo')
     pvptrans = fields.Float(string='Transporte') 
     pvpvta = fields.Float(string='Venta') 
     tipouom = fields.Many2one('uom.uom', string='Tipo Medida')
     preparaalbvta = fields.Boolean(string='Prepara Albaran de Venta')   
     asignado = fields.Boolean(string='Asignada Compra')
     relalbvta = fields.Char(string='Relacion Albarán de Venta')   
     multicomp = fields.One2many('jovimer_lineascompra', 'orderline', string='Lineas de Compra')
     reclamacion = fields.One2many('jovimer_reclamaciones', 'detalledocumentos', string='Reclamaciones')
     reclamaciones = fields.Many2one('jovimer_reclamaciones', string='Reclamaciones')
     ordendecarganac = fields.Many2many('jovimer_ctn', string='Orden de Carga Nacional')
     ordendecargaint = fields.Many2many('jovimer_cti', string='Orden de Carga Internacional')
     lineacompra = fields.Many2one('purchase.order.line', string='Linea de Compra')
     fechallegadanac = fields.Date(string='Fecha LLegada Nacional')
     lineacompracalidadpartner = fields.Many2one('res.partner', string='Proveedor', related='lineacompra.partner_id')
     nobioline = fields.Boolean(string='NO BIO L')
     nobioexp = fields.Boolean(string='NO BIO EXP', related='expediente.nobio')
     ### lineacompracalidadpartnerbio = fields.Boolean(string='Entidad NO BIO', related='lineacompracalidadpartner.nobio')
     lineaventa = fields.Many2one('sale.order.line', string='Linea de Venta')
     precioscompra = fields.Text(string='Datos de la Compra', related='lineaventa.precioscompra')
     pvpcoste = fields.Float(string='Coste', related='lineaventa.pvpcoste')
     resultadoresto = fields.Float(string='Resultado')
     ## resultadorestocalc = fields.Float(string='Resultado'store=True, readonly=True, compute='_compute_resultadoresto')
     lineaventaud = fields.Many2one('uom.uom', string='Unidad Pedido Cliente', related='lineaventa.unidabulto')
     descctavta = fields.Char(string='Motivo')
     refcliente = fields.Char(related='invoice_id.reference')
     numberfact = fields.Char(related='invoice_id.move_id.name', store=True, readonly=True, copy=False)
     fechafact = fields.Date(string='Fecha Documento', related='invoice_id.date_invoice')
     fechafact2 = fields.Date(string='Fecha Documento INTRA / Guardado')
     ## camount_untaxed = fields.Float(string='Tot', related='invoice_id.amount_untaxed')
     ctavtarepasado = fields.Boolean(string='Repasado')   
     ctavtarepasadoas = fields.Boolean(string='Repasado Asignado') 
     priceas = fields.Float(string='Precio')
     discountas = fields.Float(string='Dto%')
     price_subtotalas = fields.Float(string='Total')
     ctavtaenviado = fields.Boolean(string='Para Enviar')
     ctavtafin = fields.Boolean(string='Enviado')
     valorcvvta = fields.Float(string='TOTAL C/V')
     pvpcvvta = fields.Float(string='Precio C/V', compute="_compute_pvpcvvta")
     fechactavtarepasado  = fields.Date(string='Fecha Repasado Cuenta de Venta')
     fechactavtarepasadoas  = fields.Date(string='Fecha Repasado Cuenta de Venta')
     fechactavtaenviado  = fields.Date(string='Fecha Enviado Cuenta de Venta') 
     ocultaimpresion = fields.Boolean(string='NO Imprime')
     devolucion = fields.Boolean(string='Devuelto')
     basura = fields.Boolean(string='Basura')
     basuralineamadre = fields.Many2one('account.invoice.line',string='Origen Basura')
     basuralineadestino = fields.Many2one('account.invoice.line',string='Destino Basura')
     albvtadestinolin = fields.Many2one('account.invoice.line',string='Linea Albarán Destino')
     unidabultoj = fields.Many2one('uom.uom', string='Tipo Cálculo Jovimer', related='lineacompra.product_uom', domain=[('invisible','=','NO')])
     cantidadj = fields.Float(string='Cantidad Jovimer') 
     subtotalj = fields.Float(string='Subtotal Jovimer') 
     pricej = fields.Float(string='Precio Jovimer', related='lineacompra.price_unit')
     unidabultoalb = fields.Many2one('uom.uom', string='Tipo Cálculo Albarán', domain=[('invisible','=','NO')])
     cantidadalb = fields.Float(string='Cantidad Albarán') 
     subtotalalb = fields.Float(string='Subtotal Albarán') 
     subtotalasignado = fields.Float(string='Subtotal Asignado', compute='_compute_subtotalasignado')
     pricealb = fields.Float(string='Precio Jovimer')
     paislins = fields.Many2one('res.country', string='Pais')
     totalkglin = fields.Float(string='Kg Net')
     totalkglinbr = fields.Float(string='Kg Brut')
     viaje = fields.Many2one('jovimer_viajes', string='Viaje Relacionado')
     paislin = fields.Many2one(string='Link Country', related='invoice_id.partner_id.country_id')
     albvtadestino = fields.Many2one('account.invoice',string='Albarán Destino')
     albvtadestinolin = fields.Many2one('account.invoice.line',string='Linea Albarán Destino')
     devoluvta = fields.Boolean(string='Devolución')
     devoluvtar = fields.Many2one('jovimer_devalbaranv', string='Devolución')
     factcompradestino = fields.Many2one('account.invoice',string='Factura Destino')
     docqueorigina = fields.Many2one('account.invoice',string='Documento Origen')
     buscaasignacion = fields.Many2one('purchase.order.line',string='Busca Asignacion', domain=[('asignado','=', True)])
     productomaestro = fields.Many2one('jovimer_productos_maestros', string='Producto Maestro')
     diariofactura = fields.Many2one(string='Diario', related='invoice_id.journal_id')
     descripcioncajas = fields.Float(string='CxP')
     idgeneraalbaranes = fields.Many2one('jovimer_generaalbaranes', string='ID Genera Albaranes')
     asignarexpediente = fields.Many2one('jovimer_expedientes', string='Expediente Destino', domain=[('serie','=', 12)])
     asignarexpediente_serien = fields.Many2one('jovimer_expedientes.series', related='asignarexpediente.serie') 
     asignarcantidad = fields.Integer(string='Cantidad Asignada')
     asignarunidad = fields.Many2one('uom.uom', string='Unidad Asignada', domain=[('invisiblecp','=','SI')])
     asignarquedaran = fields.Integer(string='Cantidad que Quedará')
     asignarnosale = fields.Boolean(string='No EL AlbCli')	 
     asignaroriginal = fields.Boolean(string='No Original')
     asignarprimera = fields.Boolean(string='Primera')
     asignarmadre = fields.Many2one('account.invoice.line', string='Linea Madre')
     asignarquedaranbultos = fields.Integer(string='Bultos que Quedarán')
     asignarpartner = fields.Many2one('res.partner', related='asignarexpediente.pedvta.partner_id')
     asignarcantidadviaje = fields.Integer(string="Asigna")
     asignarrestodviaje = fields.Float(string="Stock")
     lineaalbarancompra = fields.Many2one('account.invoice.line', string='Linea Albaran Compra')
     lineacabalbarancompra = fields.Many2one('account.invoice', string='Albaran Compra')
     cabeceraalbarancompra = fields.Char(string='Albaran Compra', related='lineaalbarancompra.invoice_id.reference')
     cabeceraalbarancompraid = fields.Many2one('account.invocie', string='Albaran Compra', related='lineaalbarancompra.invoice_id')
     algovamal = fields.Boolean(string='No cuadra')
     ## errorvamal = fields.Boolean(string='No cuadra')
     bultostotalesalbarancompra = fields.Float(string='Bultos Totales Albarán Compra')
     bultostotalespedidocompra = fields.Float(string='Bultos Totales Pedido Compra')
     remontado = fields.Boolean(string='Remontado')
     viajerel = fields.Many2one('jovimer_viajes', string='Viaje Relacionado')
     nocargar = fields.Boolean(string='NO CARGAR')
     nocargarasig = fields.Boolean(string='NO CARGAR LINEA ASIGNADA VIAJE')
     plataformaorigen = fields.Many2one('res.partner', string='Almacén Origen')
     plataformadestino = fields.Many2one('res.partner', string='Destino')
     preciomediaintra = fields.Float(string='Precio Intrastat KG', group_operator="avg")
     precioenkg = fields.Float(string='Precio en KG')
     tipomovalmacen = fields.Selection([('ENTRADA','ENTRADA'),('SALIDA','SALIDA'),('BASURA','BASURA')], string='Tipo Movimiento')
     cantidadalmacencajas = fields.Float(string='Cantidad Almacén Cajas')
     cantidadalmacenkg = fields.Float(string='Cantidad Almacén KG')
     fechaalmacen = fields.Date(string='Fecha de Almacén')
     precioalmacenkg = fields.Float(string='Precio Medio Almacén KG')
     fechapedidocompra = fields.Date(string='Fecha Pedido Compra')	 
     fechapedidoventa = fields.Date(string='Fecha Pedido Venta')	
     fechapedidosalida = fields.Date(string='Fecha Pedido/Salida')
     trasladaalbaran = fields.Many2one('account.invoice',string='Albarán Destino', domain=[('journal_id','=', 9),('state','=', 'draft')])
     numdelinea = fields.Integer(string='NLin')
     dividiralbarane = fields.Many2one('account.invoice', string='Albarán Existente')
     typefact = fields.Selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Vendor Bill'),
            ('out_refund','Customer Credit Note'),
            ('in_refund','Vendor Credit Note'),
        ], readonly=True, related='invoice_id.type', store=True)
     state = fields.Selection([
            ('draft','Draft'),
            ('open', 'Open'),
            ('in_payment', 'In Payment'),
            ('paid', 'Paid'),
            ('cancel', 'Cancelled'),
        ], string='Status', index=True, readonly=True, default='draft', related='invoice_id.state', store=True)
     correctoctavta = fields.Selection([
		('SI','SI'),
		('NO','NO'),
		('FALTA','FALTA'),
		],string='Estado',default='FALTA')

     correctoliqui = fields.Selection([
		('SI','SI'),
		('NO','NO'),
		('FALTA','FALTA'),
		],string='Estado',default='FALTA')
     descliqui = fields.Char(string='Motivo')
     statusrecla = fields.Selection([
		('OK','OK'),
		('RECLAMADA','RECLAMADA'),
		('DEVUELTA','DEVUELTA'),
		],string='Estado',default='OK')    

     ### def write(self, values):
     ###      if 'display_type' in values and self.filtered(lambda line: line.display_type != values.get('display_type')):
     ###           raise UserError(_("You cannot change the type of an invoice line. Instead you should delete the current line and create a new line of the proper type."))
     ###      coste = self.pvpcoste or 0
     ###      ingreso = self.price_subtotal
     ###      resultadoresto = float(ingreso) - float(coste)
     ###      values['resultadoresto'] = float(resultadoresto)
     ###      return super(ModelAccountInvoiceLine, self).write(values)



     @api.onchange('price_subtotal','price_subtotalas','subtotalasignado')
     def on_change_calcvalorcv(self):
        total = self.price_subtotal
        totalas = self.subtotalasignado
        valorcvvta = totalas
        ## print("\n --- Voy a escribir: " + str(totalas) + "\n\n")
        if totalas == 0:
            valorcvvta = total
        self.valorcvvta = valorcvvta


     def createalbarannuevo(self):
        idlin = self.id
        partner_id = self.invoice_id.partner_id.id
        expedienteid = self.invoice_id.expediente.id
        ## expedientesdecompra = self.invoice_id.expedientesdecompra
        dateinv_compra = self.invoice_id.dateinv_compra
        expedientesdecompra = []
        for expedientesdecompra_ids in self.invoice_id.expedientesdecompra:
            idlinalb = expedientesdecompra_ids.id
            expedientesdecompra += idlinalb,
        idlin = self.id
        print("\n\n EL EXPEDIENTE COMPRA ES: " + str(expedientesdecompra) + "")
        creaalbaran = self.env["account.invoice"].sudo().create({'partner_id': partner_id, 'journal_id': 9, 'expedientesdecompra': expedientesdecompra, 'expediente': expedienteid,'dateinv_compra': dateinv_compra })
        self.ensure_one()
        self.env.cr.execute("INSERT INTO account_invoice_jovimer_expedientes_rel (account_invoice_id,jovimer_expedientes_id) VALUES ('" + str(creaalbaran.id) + "','" + str(expedienteid) + "')")
        self.dividiralbarane = creaalbaran.id
        return {}


     def enviarloalbaran(self):
        idlinea = self.id
        iddoc = self.invoice_id.id
        dividiralbarane = self.dividiralbarane.id
        if dividiralbarane == False:
           raise AccessError("No veo Albarán para Asignar no puedo continuar")
        contadorrosas = self.env['account.invoice.line'].search_count([('invoice_id','=',iddoc),('asignaroriginal','=',True),('asignarmadre','=',idlinea)])
        ## raise AccessError("EL contador de churumbeles a la madre es: " + str(contadorrosas) + "")
        print ("\n\n")
        if contadorrosas != 0:
           print("Pasaremos Churumbeles")
           asignados = self.env['account.invoice.line'].search([('invoice_id','=',iddoc),('asignaroriginal','=',True),('asignarmadre','=',idlinea)])
           for asignados_ids in asignados:
               idasignado = asignados_ids.id
               asignados_ids.write({'invoice_id': dividiralbarane})
               print("Cambiando ASIGNADO: " + str(idasignado) + " a " + str(dividiralbarane) + "")
        print ("Cambiando LINEA MADRE: " + str(idlinea) + " a " + str(dividiralbarane) + "\n\n")
        self.write({'invoice_id': dividiralbarane})
        return {}


     def calcvalorcv(self):
        idlin = self.id
        total = self.price_subtotal
        totalas = self.subtotalasignado
        valorcvvta = totalas
        ## print("\n --- Voy a escribir: " + str(totalas) + "\n\n")
        if totalas == 0:
            valorcvvta = total
        self.write({'valorcvvta': valorcvvta})
        return {}

     def action_quitarasignacion(self):
        idlin = self.id
        plantilla = self.plantilla.id
        idfact = self.invoice_id.id
        stock = self.asignarrestodviaje
        totalbultos = self.totalbultos
        sumastok = stock + totalbultos
        self.env.cr.execute("DELETE FROM account_invoice_line where invoice_id='" + str(idfact) + "' and id='" + str(idlin) + "'") 
        self.env.cr.execute("UPDATE account_invoice_line SET asignarrestodviaje='" + str(sumastok) + "' where invoice_id='" + str(idfact) + "' and plantilla='" + str(plantilla) + "'")
        ### idlin.unlink()
        return {}

     def action_asignadesdeviaje(self, default=None):
        idlin = self.id
        idalb = self.invoice_id.id
        plantilla = self.plantilla.id
        totalbultos = self.totalbultos
        bultos = self.bultos
        asignarcantidadviaje = self.asignarcantidadviaje
        asignarrestodviaje = self.asignarrestodviaje
        resto = totalbultos - asignarcantidadviaje
        cantidadpedido = asignarcantidadviaje / bultos
        cantidadpedido = math.ceil(cantidadpedido)
        asignaroriginal = self.asignaroriginal
        asignaroriginal = self.asignaroriginal
        self.env.cr.execute("select sum(totalbultos) from account_invoice_line where invoice_id='" + str(idalb) + "' and plantilla='" + str(plantilla) + "' and ( asignaroriginal IS NULL or asignaroriginal='f')")
        resultv = self.env.cr.fetchone()
        totentrada = str(resultv[0])
        self.env.cr.execute("select sum(totalbultos) from account_invoice_line where invoice_id='" + str(idalb) + "' and plantilla='" + str(plantilla) + "' and asignaroriginal='t'")
        resultv = self.env.cr.fetchone()
        totalsalida = str(resultv[0])
        if str(totalsalida) == "None":
           totalsalida = "0"
        if str(totentrada) == "None":
           totentrada = "0"
        ## totentrada = float(totentrada)
        ## totalsalida = float(totalsalida)
        sumastok = float(totentrada) - float(totalsalida) -  float(asignarcantidadviaje)
        print("\n\n Resultado: " + str(plantilla) + " : " + str(totentrada) + " - " + str(totalsalida) + " = " + str(sumastok) + ".\n\n")
        viajeid = self.env['jovimer_viajes'].search([('linealbcompra', '=', idlin)], order='id desc', limit=1).id
        ## viajeid = 3108
        ## raise AccessError("Viaje que lo origina: " + str(viajeid) + "")
        if str(viajeid) == "False":
           raise AccessError("ERROR: No puedo Relacionar la linea del Albarán con EL viaje. Las asignaciones deben hacerse en el Albarán")
        try: 
           expedientes = self.env['jovimer_viajes'].search([('id', '=', viajeid)], order='id desc', limit=1).expedientes.id
        except:
           raise AccessError("Error al Seleccionar el Expediente, probablemente por múltiples J. Debes Asignar Manualmente el Destino en cada linea.")

        if resto < 0:
           raise AccessError("No Puedes Asignar más cantidad que la recibida. Datos: \n ID Linea Albarán: " + str(idlin) + "\n Linea Madre: " + str(asignaroriginal) + "\n Recibida: " + str(totalbultos) + "")
        if sumastok < 0:
           raise AccessError("NO hay suficiente Stock para La Asignación")
        ## raise AccessError("El ALbarán es: " + str(idalb))
        default.update({'expediente':expedientes, 'nocargarasig':False, 'totalbultosprev': 0, 'price_unit': 0,'sequence': 200, 'asignarmadre': idlin, 'totalbultos': asignarcantidadviaje, 'cantidadpedido': cantidadpedido,'asignaroriginal': True, 'ctavtarepasado': True,})
        duplica = super(ModelAccountInvoiceLine, self).copy(default)
        duplica.calcula_cantidad()
        self.env.cr.execute("UPDATE account_invoice_line SET asignarrestodviaje='" + str(sumastok) + "' where invoice_id='" + str(idalb) + "' and plantilla='" + str(plantilla) + "'")
        self.env.cr.execute("INSERT INTO account_invoice_line_jovimer_viajes_rel (jovimer_viajes_id,account_invoice_line_id) VALUES ('" + str(viajeid) + "','" + str(duplica.id) + "')")
        self.write({'asignarcantidadviaje':0,'nocargarasig':True,'asignarrestodviaje': resto})
        self.env.cr.execute("DELETE FROM account_invoice_line_jovimer_viajes_rel WHERE jovimer_viajes_id='" + str(viajeid) + "' and account_invoice_line_id='" + str(idlin) + "'")
        return {}



    
     def action_cargarlinea2(self):
        idalb = self.id
        usuario = self.env.user.id
        cargado = self.cargado
        ## Error Bultos Carga
        totalbultosc = self.totalbultos
        totalbultosprevc = self.totalbultosprev
        print("RESTO: " + str(totalbultosc) + "--" + str(totalbultosprevc))
        previstoserror = False
        if str(totalbultosc) != str(totalbultosprevc):
           previstoserror = True
        else:
            previstoserror = False

        if str(cargado) == "True":
            self.write({'cargado':False,'cargado_por':False,'cargado_cuandot':False,'previstoserror':previstoserror})
        else:
            id = self.id
            totalbultos = self.totalbultos
            cantidad = self.quantity
            today = date.today()
            ### default.update({
            ### 'state': 'draft'})
            duplica = super(ModelAccountInvoiceLine, self).copy()
            duplica.update({'sequence': 200,'asignarprimera': True, 'asignarmadre': idalb, 'asignaroriginal': True, 'ctavtarepasado': True,})


            self.write({'cargado':True,'cargado_por':usuario,'cargado_cuandot':fields.Datetime.now(),'previstoserror':previstoserror})
        return {}

     def action_cargarlineaform(self, default=None):
         ## raise AccessError("ERROR: El Asistente de Asignacion de Mercancia NO esta preparado")
         orderdevolu_obj = self.env['jovimer_preparaentrada']
         invoice = orderdevolu_obj.create({'name': self.id,'totalbultosentrada': self.totalbultos})
         invoice = int(invoice[0]) 
         ## self.env.cr.execute(""" UPDATE account_invoice_line SET devoluvtar='%s',devoluvta='t' where id='%s' """ % (invoice,id))       
         return {
          'name': ("Carga Linea"),
          'type': 'ir.actions.act_window',
          'res_model': 'jovimer_preparaentrada',
          'view_mode': 'form',
          'view_type': 'form',
          'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'},
          'res_id': invoice,
          'target': 'new',
         }

    
     def action_cargarlinea(self):
        idalb = self.id
        usuario = self.env.user.id
        cargado = self.cargado
        ## Error Bultos Carga
        totalbultosc = self.totalbultos
        totalbultosprevc = self.totalbultosprev
        print("RESTO: " + str(totalbultosc) + "--" + str(totalbultosprevc))
        previstoserror = False
        if str(self.nocargar) == True:
           raise AccessError("No Puedes CARGAR La linea sin desmarcar antes el Boton NO CARGAR")

        if str(totalbultosc) != str(totalbultosprevc):
           previstoserror = True
        else:
            previstoserror = False

        if str(cargado) == "True":
            self.write({'cargado':False,'cargado_por':False,'cargado_cuandot':False,'previstoserror':previstoserror})
        else:
            self.write({'nocargar':False,'cargado':True,'cargado_por':usuario,'cargado_cuandot':fields.Datetime.now(),'previstoserror':previstoserror})
        return {}

    
     def _get_total_bultos(self):
        self.totalbultos = self.bultos * self.cantidadpedido


     def action_pasaacti(self, default=None):
         id = str(self.id)
         args = ["/opt/jovimer12/bin/viajedirecto_desdealbaran.bash", id, "&"]
         subprocess.call(args)
         return {}


     @api.onchange('price_subtotal','price','discountas','priceas') 
     def on_change_priceas(self):
         try: 
             discountas = self.partner_id.comisionvta
             asignarmadre = self.asignarmadre
             ### self.env.cr.execute(""" select sum(totalbultos) from account_invoice_line where invoice_id='%s' and plantilla='%s'""" % (str(invoiceid),str(plantillaid)))
             ### resultv = self.env.cr.fetchone()
             ### totcxp = float(resultv[0])
             ## if asignarmadre != False:
             ##    discountas = self.env['account.invoice.line'].search([('id','=', asignarmadre)]).discount
             ## raise AccessError("EL Descuento es segun la linea " + str(asignarmadre) + " es: " + str(discountas))
             priceas = self.priceas
             quantity = self.quantity
             subtotalnd = ( quantity * priceas )
             dtodiv = discountas / 100
             subtotal = subtotalnd - (subtotalnd * dtodiv)
             self.price_subtotalas = subtotal
         except:
             discountas = 6

         self.discountas = discountas	 
             

     @api.onchange('price_subtotal') 
     def on_change_resultadoresto(self):
         try:
             coste = self.pvpcoste or 0
             ingreso = self.price_subtotal
             resultadoresto = float(ingreso) - float(coste)
         except:
             resultadoresto = 0
         self.resultadoresto = float(resultadoresto)
             ## result = {'resultadoresto': resultadoresto,}
             ## self.write({'resultadoresto': resultadoresto})
             ## return result


     @api.onchange('cantidadpedido','bultos','kgnetbulto','unidabulto','totalbultos') 
     def on_change_unidabulto(self):
             invoiceid = self.invoice_id.id
             plantillaid = self.plantilla.id
             ### self.env.cr.execute(""" select sum(totalbultos) from account_invoice_line where invoice_id='%s' and plantilla='%s'""" % (str(invoiceid),str(plantillaid)))
             ### resultv = self.env.cr.fetchone()
             ### totcxp = float(resultv[0])
             ### self.descripcioncajas = totcxp
             totalbultos = self.totalbultos           
             unidadesporbulto = self.confeccion.unidadesporbulto or 1
             if str(totalbultos) == "0":
                totalbultos = self.cantidadpedido * float(self.bultos)
                self.totalbultos = totalbultos
             ## raise AccessError("Tipo: " + str(self.unidabulto))
             ## Bultos
             unidabulto = self.unidabulto
             if self.unidabulto.id == 24:
                self.quantity = float(totalbultos)
             ## KG
             if self.unidabulto.id == 27:
                self.quantity = float(totalbultos) * float(self.kgnetbulto)
             ## Unidades
             if self.unidabulto.id == 1:
                self.quantity = float(totalbultos) * float(unidadesporbulto)
             self.totalkglin = float(totalbultos) * float(self.kgnetbulto)


             ## Error Bultos Carga
             totalbultosc = self.totalbultos
             totalbultosprevc = self.totalbultosprev
             print("RESTO: " + str(totalbultosc) + "--" + str(totalbultosprevc))
             if str(totalbultosc) != str(totalbultosprevc):
                self.previstoserror = True
             else:
                self.previstoserror = False


             return {}

     def action_cuentaventarepasado(self, default=None):
           ## id = str(self.id)
           ## args = ["/opt/jovimer12/bin/cuentaventarepasado.bash", id, "&"]
           ## subprocess.call(args)
           id = str(self.id)
           devolucion = str(self.devolucion)           
           ### raise UserError("La linea Esta marcada como Devolucion NO PUEDES Marcarla como Repasada: " + str(devolucion) + ".")	
           print("\n EL Valor de Cuneta de Venta es: " + str(self.valorcvvta) + "\n\n")
           if self.valorcvvta == 0:
               self.valorcvvta = self.subtotalasignado		   
           if self.valorcvvta == 0:
               raise UserError("EL Valor de Cuenta de Venta es 0 No se puede marcar como repasada")		   
           if str(devolucion) == "True":
               raise UserError("La linea Esta marcada como Devolucion NO PUEDES Marcarla como Repasada")		   
           invoiceid = str(self.invoice_id.id)
           today = date.today()
           d1hoy = today.strftime("%Y-%m-%d")
           self.write({'ctavtarepasado': True})
           self.write({'fechactavtarepasado': d1hoy})
           self.env.cr.execute(""" select count(*) from account_invoice_line where invoice_id='%s' and ( ctavtarepasado='f' OR ctavtarepasado is Null )""" % (str(invoiceid)))
           resultv = self.env.cr.fetchone()
           existerep = str(resultv[0])
           if existerep == "0":
              self.env.cr.execute(""" UPDATE account_invoice SET ctavtacompleto='t' where id='%s'""" % (str(invoiceid)))
              ## print ("Vamos a Marcar el Albarán como Pendiente de Enviar ya que esta repasado por completo")
           ## else:
              ### print ("EL Valor es: " + str(existerep))
           return {} 


     def action_cuentaventarepasado2(self, default=None):
           id = str(self.id)
           devolucion = str(self.devolucion)           
           asignarmadre = str(self.asignarmadre.id)  	
           if str(devolucion) == "True":
               raise UserError("La linea Esta marcada como Devolucion NO PUEDES Marcarla como Repasada")		   
           invoiceid = str(self.invoice_id.id)
           today = date.today()
           d1hoy = today.strftime("%Y-%m-%d")
           self.write({'ctavtarepasadoas': True})
           self.write({'fechactavtarepasadoas': d1hoy})
           self.env.cr.execute("select count(*) from account_invoice_line where invoice_id='" + str(invoiceid) + "' and ( ctavtarepasadoas='f' OR ctavtarepasadoas is Null ) and asignado='f' and asignarmadre='" + str(asignarmadre) + "'")
           resultv = self.env.cr.fetchone()
           existerep2 = str(resultv[0])
           if existerep2 == "0":
              self.env.cr.execute("UPDATE account_invoice_line SET ctavtarepasado='t',fechactavtarepasado='" + str(d1hoy) + "' where id='" + str(asignarmadre) + "'")
              ## raise AccessError("Vamos a Marcar la Linea Madre: " + str(asignarmadre) + "  como completada Ya que el contador de pendiente es: " + str(existerep2) + " perteneciente a la Factura: " + str(invoiceid) + "")
              self.env.cr.execute(""" select count(*) from account_invoice_line where invoice_id='%s' and ( ctavtarepasado='f' OR ctavtarepasado is Null )""" % (str(invoiceid)))
              resultv = self.env.cr.fetchone()
              existerep = str(resultv[0])
              if existerep == "0":
                  self.env.cr.execute(""" UPDATE account_invoice SET ctavtacompleto='t' where id='%s'""" % (str(invoiceid)))
           else:
              print("Marcada Asignada como repasada: " + str(id) + " Perteneciente a " + str(asignarmadre) + "")
           return {}

     def action_cuentaventadesrepasado2(self, default=None):
           ## self.write({'statusrecla': 'RECLAMADA'})
           id = str(self.id)
           invoiceid = str(self.invoice_id.id)
           self.env.cr.execute(""" UPDATE account_invoice SET ctavtacompleto='f' where id='%s'""" % (str(invoiceid)))
           self.write({'ctavtarepasadoas': False,'fechactavtarepasadoas': None})
           return {} 



     def action_cuentaventanorepasado(self, default=None):
           ## self.write({'statusrecla': 'RECLAMADA'})
           id = str(self.id)
           invoiceid = str(self.invoice_id.id)
           self.env.cr.execute(""" UPDATE account_invoice SET ctavtacompleto='f' where id='%s'""" % (str(invoiceid)))
           self.write({'ctavtarepasado': False})
           self.write({'fechactavtarepasado': None})
           return {} 


     def action_cuentaventaenviado(self, default=None):
           ## self.write({'statusrecla': 'RECLAMADA'})
           id = str(self.id)
           referencecli = str(self.invoice_id.reference)
           if referencecli:
               referenceclisql = '%' + str(self.invoice_id.reference) + '%'
           else:
               referenceclisql = 'XXXXXXXXXXXXXXXXXXXXXX'           
           partner = str(self.partner_id.id)
           ### self.env.cr.execute(""" select count(*) from account_invoice_line where expediente='%s' and partner_id='%s' and ctavtarepasado<>'t' and invoice_id in (select id from account_invoice where type='in_invoice' and journal_id='9') """ % (expediente,partner))
           self.env.cr.execute(""" select count(*) from account_invoice_line where ( ctavtarepasado='f' OR ctavtarepasado is Null ) and invoice_id in (select id from account_invoice where type='in_invoice' and journal_id='9' and reference LIKE '%s') """ % (str(referenceclisql)))
           resultv = self.env.cr.fetchone()
           existerep = str(resultv[0])
           if existerep != "0":
               raise AccessError("Existen Lineas de Cuentas de Venta NO repasadas. Debes marcarlas como repasadas TODAS las lineas Del albaran de proveedor " + referencecli + " si quieres enviar la cuenta de ventas del expediente")
           args = ["/opt/jovimer12/bin/cuentaventaenviado.bash", id, "&"]
           subprocess.call(args)
           return {} 



     def calcula_cantidad(self):
             invoiceid = self.invoice_id.id
             plantillaid = self.plantilla.id
             self.env.cr.execute(""" select sum(totalbultos) from account_invoice_line where invoice_id='%s' and plantilla='%s'""" % (str(invoiceid),str(plantillaid)))
             resultv = self.env.cr.fetchone()
             totcxp = float(resultv[0])
             self.descripcioncajas = totcxp
             ## raise AccessError("totcxp: " + str(totcxp))
             ## Bultos
             totalbultos = 0
             totalbultos = self.totalbultos or 0
             if totalbultos == 0:
                    totalbultos = float(self.cantidadpedido) * float(self.bultos)
                    self.totalbultos = totalbultos
             if self.unidabulto.id == 24:
                self.quantity = totalbultos
             unidadesporbulto = self.confeccion.unidadesporbulto or 1
             ## KG
             if self.unidabulto.id == 27:
                self.quantity = float(totalbultos) * float(self.kgnetbulto)
             ## Unidades
             if self.unidabulto.id == 1:
                self.quantity = float(totalbultos) * float(unidadesporbulto)

             if self.lineacompra:
                if self.lineacompra.product_uom.id == 24:
                   self.cantidadj = float(totalbultos)
                ## KG
                if self.lineacompra.product_uom.id == 27:
                   self.cantidadj = float(totalbultos) * float(self.kgnetbulto)
                ## Unidades
                if self.lineacompra.product_uom.id == 1:
                   self.cantidadj = float(totalbultos) * float(unidadesporbulto)
             return {}

     def calcula_cantidadcli(self):
             invoiceid = self.invoice_id.id
             lineaventaid = self.lineaventa.id
             plantillaid = self.plantilla.id
             udfacturacion = self.udfacturacion.id
             self.env.cr.execute(""" select sum(totalbultos) from account_invoice_line where invoice_id='%s' and plantilla='%s'""" % (str(invoiceid),str(plantillaid)))
             resultv = self.env.cr.fetchone()
             totcxp = float(resultv[0])
             self.descripcioncajas = totcxp
             ## raise AccessError("totcxp: " + str(totcxp))
             ## Bultos
             quantity = 0
             totalbultos = 0
             totalbultos = self.totalbultos or 0
             unidadesporbulto = self.confeccion.unidadesporbulto or 1
             if totalbultos == 0:
                    totalbultos = float(self.cantidadpedido) * float(self.bultos)
                    self.totalbultos = totalbultos
             ## raise UserError("La Linea de Venta es: " + str(lineaventaid) + ".")
             if self.lineacompra:
                if self.lineacompra.product_uom.id == 24:
                   self.cantidadj = float(totalbultos)
                ## KG
                if self.lineacompra.product_uom.id == 27:
                   self.cantidadj = float(totalbultos) * float(self.kgnetbulto)
                ## Unidades
                if self.lineacompra.product_uom.id == 1:
                   self.cantidadj = float(totalbultos) * float(unidadesporbulto)

             if str(lineaventaid) != "False":
                lineaventaprice = self.lineaventa.price_unit
                if self.lineaventa.unidabulto.id == 24:
                   quantity = float(totalbultos)
                ## KG
                if self.lineaventa.unidabulto.id == 27:
                   quantity = float(totalbultos) * float(self.kgnetbulto)
                ## Unidades
                if self.lineaventa.unidabulto.id == 1:
                   quantity = float(totalbultos) * float(unidadesporbulto)
                ## raise UserError("Paso por aqui")
                self.write({'quantity': float(quantity), 'unidabulto': self.lineaventa.unidabulto.id })
             else:
				 ### BULTOS
                if self.unidabulto.id == 24:
                   self.quantity = totalbultos
                ## KG
                if self.unidabulto.id == 27:
                   self.quantity = float(totalbultos) * float(self.kgnetbulto)
                ## Unidades
                if self.unidabulto.id == 1:
                   self.quantity = float(totalbultos) * float(unidadesporbulto)

             unidabultodef = self.lineaventa.unidabulto.id
             ## Miramos si tenemos definido Unidad de Facturación en la Plantilla de Producto
             if str(udfacturacion) != "False":
                print("\n LA Tenemos ud Facturacion: " + str(udfacturacion) + "\n")
                unidabultodef = self.udfacturacion.id
                lineaventaprice = self.lineaventa.price_unit
                if self.udfacturacion.id == 24:
                   quantity = float(totalbultos)
                ## KG
                if self.udfacturacion.id == 27:
                   quantity = float(totalbultos) * float(self.kgnetbulto)
                ## Unidades
                if self.udfacturacion.id == 1:
                   quantity = float(totalbultos) * float(unidadesporbulto)
                ## raise UserError("Paso por aqui")
                self.write({'quantity': float(quantity), 'unidabulto': unidabultodef })




             return {}




     def calcula_cantidadc(self):
             ## raise AccessError("Tipo: " + str(self.unidabulto))
             ## Bultos
             self.discount = 0
             try:
                 self.discount = self.partner_id.lineacompra.discount			 
             except:
                 self.discount = self.partner_id.comisionvta
             if self.unidabulto.id == 24:
                self.quantity = float(self.cantidadpedido) * float(self.bultos)
             unidadesporbulto = self.confeccion.unidadesporbulto or 1
             ## KG
             if self.unidabulto.id == 27:
                self.quantity = float(self.cantidadpedido) * float(self.bultos) * float(self.kgnetbulto)
             ## Unidades
             if self.unidabulto.id == 1:
                self.quantity = float(self.cantidadpedido) * float(self.bultos) * float(unidadesporbulto)

             if self.lineacompra:
                if self.lineacompra.product_uom.id == 24:
                   self.cantidadj = float(self.cantidadpedido) * float(self.bultos)
                ## KG
                if self.lineacompra.product_uom.id == 27:
                   self.cantidadj = float(self.cantidadpedido) * float(self.bultos) * float(self.kgnetbulto)
                ## Unidades
                if self.lineacompra.product_uom.id == 1:
                   self.cantidadj = float(self.cantidadpedido) * float(self.bultos) * float(unidadesporbulto)
             return {}



     def calcula_cantidadv(self):
             ## raise AccessError("Tipo: " + str(self.unidabulto))
             ## Bultos
             if self.unidabulto.id == 24:
                self.quantity = float(self.cantidadpedido) * float(self.bultos)
             unidadesporbulto = self.confeccion.unidadesporbulto or 1
             ## KG
             if self.unidabulto.id == 27:
                self.quantity = float(self.cantidadpedido) * float(self.bultos) * float(self.kgnetbulto)
             ## Unidades
             if self.unidabulto.id == 1:
                self.quantity = float(self.cantidadpedido) * float(self.bultos) * float(unidadesporbulto)

             if self.lineacompra:
                if self.lineacompra.product_uom.id == 24:
                   self.cantidadj = float(self.cantidadpedido) * float(self.bultos)
                ## KG
                if self.lineacompra.product_uom.id == 27:
                   self.cantidadj = float(self.cantidadpedido) * float(self.bultos) * float(self.kgnetbulto)
                ## Unidades
                if self.lineacompra.product_uom.id == 1:
                   self.cantidadj = float(self.cantidadpedido) * float(self.bultos) * float(unidadesporbulto)
             return {}


     def action_crearreclamacionacc(self, default=None):
           ## self.write({'statusrecla': 'RECLAMADA'})
           id = str(self.id)
           args = ["/opt/jovimer12/bin/creareclamacion_contable.bash", id, "&"]
           subprocess.call(args)
           return {}  
     def action_cerrarreclamacion(self, default=None):
           self.write({'statusrecla': 'OK'})
           return {}	

     def facturaifcos(self, default=None):
        idline = self.id
        idinvoiceid = self.invoice_id.id
        invoice = self.invoice_id
        partner_id = self.partner_id.id
        cantidad = self.totalbultos
        price_unit = 3.5
        ### args = ["/opt/jovimer12/bin/insertalineasifco.bash", id, "&"]
        ### args = ["/opt/jovimer12/bin/webservice/insertalineaifco.py", id, partner_id, "&"]
        ### subprocess.call(args)
        ### raise AccessError("Eres: " + str(idline) + "-" + str(idinvoiceid) + "-" + str(partner_id) + "-" + str(cantidad) + "")
        taxid = 21
        base = 0
        inlinetax_ids = self.env['account.invoice.tax'].search([('invoice_id', '=', int(idinvoiceid)),('tax_id','=',taxid)], limit=1)
        for linvoicetaxlines in inlinetax_ids:
           base = linvoicetaxlines.base
           amounttax = linvoicetaxlines.amount
           tasaimpuesto = linvoicetaxlines.x_impresion
           if str(tasaimpuesto) == "False":
              raise AccessError(" Hay Alguna Linea sin Porcentaje de Cuota de Impuesto")
           cuotaifco = cantidad * price_unit
           baset = base + cuotaifco
           amounttaxt = baset * 0.04
           ## raise AccessError("Base Original de la Factura: " + str(idinvoiceid) + " : " + str(base) + ". Base Total: " + str(baset) + ". Cuota IVA: " + str(amounttax) + ". Cuota Definitiva: " + str(amounttaxt) + ".")
           if baset != 0:
              linvoicetaxlines.write({'base': baset,'amount': amounttaxt})
        invlineifco_obj = self.env['account.invoice.line']
        invoicelinifco = invlineifco_obj.create({
           'price_unit': price_unit,
           'invoice_id': idinvoiceid,
           'partner_id': partner_id,
           'product_id': 159,
           'variedad': 214,
           'plantilla': 759,
           'account_id': 356,
           'quantity': cantidad,
		   'invoice_line_tax_ids':  [(4, taxid)]})
        invoicelinifco = int(invoicelinifco[0])


        ## recaltax = invoice.recalcular_amount_pyme()
        return {}


     def devoluclialb(self):
           id = self.id
           totalbultos = self.totalbultos
           cantidad = self.quantity
           today = date.today()
           d1hoy = today.strftime("%Y-%m-%d")
           observaciones = 'Cantidad Original: ' + str(totalbultos) + '. Cantidad Facturable: ' + str(cantidad) + '.' 
           orderdevolu_obj = self.env['jovimer_devalbaranv']
           invoice = orderdevolu_obj.create({
                   'name': id,
                   'observaciones': observaciones,
                   'cantidad': totalbultos,
                   'fecha': d1hoy,})
           invoice = int(invoice[0]) 
           ## self.env.cr.execute(""" UPDATE account_invoice_line SET devoluvtar='%s',devoluvta='t' where id='%s' """ % (invoice,id))       
           return {
           'name': ("Devoluciones"),
           'type': 'ir.actions.act_window',
           'res_model': 'jovimer_devalbaranv',
           'view_mode': 'form',
           'view_type': 'form',
           'res_id': invoice,
           'target': 'new',
           }

     def duplicalinea(self):
           id = self.id
           totalbultos = self.totalbultos
           cantidad = self.quantity
           today = date.today()
           ### default.update({
           ### 'state': 'draft'})
           super(ModelAccountInvoiceLine, self).copy()
           return {}


     def trasladaotroalbaran(self):
           lineid = self.id
           invoicew = self.trasladaalbaran.id
           if invoicew == False:
               raise AccessError("No se puede Copiar la Linea, NO has seleccionado el Albarán Destino")
           if invoicew == self.invoice_id.id:
               raise AccessError("Albarán Destino y Origen son el mismo. NO se traslada")

           totalbultos = self.totalbultos
           cantidad = self.quantity
           today = date.today()
           name = "PEPE"

           self.write({'invoice_id': invoicew,'trasladaalbaran': False,})
           ### invoiceline_obj = self.env['account.invoice.line']
           ### for lines in self:
           ###     linesapend = (4, lines.product_id.id)
           ###     invoicelinew = invoiceline_obj.create({
           ###         'invoice_id': invoicew,
           ###         'name': lines.product_id.name,
           ###         'plantilla': lines.,
           ###         'variedad': lines.,
           ###         'calibre': lines.,
           ###         'categoria': lines.,
           ###         'confeccion': lines.,
           ###         'envase': lines.,
           ###         '': lines.,
           ###         '': lines.,
           ###         'product_id': lines.product_id.id,        
           ###         'price_unit': lines.price_unit,  
           ###         'quantity': lines.cantidadpedido,  
           ###         'discount': lines.discount, 
           ###         'account_id': lines.account_id.id,})
           view_id = self.env.ref('pyme_jovimer.jovimer_facturas_prov_view_form').id
           return {
           'name': ("Nuevo Albarán"),
           'type': 'ir.actions.act_window',
           'view_id': view_id,
           'res_model': 'account.invoice',
           'view_mode': 'form',
           'view_type': 'form',
           'res_id': invoicew,
           'target': 'current',
           }
           ## return {}


     def duplicalineaymarcabasura(self, default=None):
           ### basura = fields.Boolean(string='Basura')
           ### basuralineamadre = fields.Many2one('account.invoice.line',string='Origen Basura')
           ### basuralineadestino = fields.Many2one('account.invoice.line',string='Destino Basura')

           id = self.id
           order = self.invoice_id.id
           totalbultos = self.totalbultos
           cantidad = self.quantity
           today = date.today()
           ### default.update({
           ### 'state': 'draft'})
           self.env.cr.execute(""" select sum(totalbultos) from account_invoice_line where ( asignaroriginal='f' or asignaroriginal is null ) and invoice_id='%s'""" % (order))
           resultv = self.env.cr.fetchone()
           totalbentrada = float(resultv[0])
           self.env.cr.execute(""" select sum(totalbultos) from account_invoice_line where asignaroriginal='t' and invoice_id='%s'""" % (order))
           resultv = self.env.cr.fetchone()
           totalbsalida = float(resultv[0])
           restobultos = totalbentrada - totalbsalida
           restobultos = -float(restobultos)
           default.update({
             'totalbultos': restobultos,
             'price_unit': 0,
             'viajerel': False,
             'basura': True,
             'asignaroriginal': False,
             'ctavtarepasado': True,})

           res_id = super(ModelAccountInvoiceLine, self).copy(default)
           for line in res_id:
             idline = line.id
             line.basura = True
             line.basuralineamadre = self.id
           self.write({'basuralineadestino': idline})
           return {}



     def asignarduplicalinea(self, default=None):
           idline = self.id
           quantity = 0
           totalkglin = 0
           asignarexpediente = self.asignarexpediente.id
           nombreproducto = self.plantilla.name
           cantidadoriginal = self.cantidadpedido
           unidadoriginal = self.unidadpedido           
           unidadoriginalname = self.unidadpedido.name
           asignarcantidad = self.asignarcantidad
           totalbultosoriginales = self.totalbultos
           bultosoriginales = self.bultos
           asignarquedaranbultos = totalbultosoriginales - ( asignarcantidad * bultosoriginales ) 		   
           asignarquedaran = cantidadoriginal - asignarcantidad
           self.discount = 0
           totalkglin = float(asignarcantidad) * float(bultosoriginales) * float(self.kgnetbulto)
           try:
               self.discount = self.partner_id.lineacompra.discount			 
           except:
               self.discount = self.partner_id.comisionvta
           if self.unidabulto.id == 24:
              quantity = float(asignarcantidad) * float(bultosoriginales)
           ## KG
           if self.unidabulto.id == 27:
              quantity = float(asignarcantidad) * float(bultosoriginales) * float(self.kgnetbulto)
           ## Unidades
           if self.unidabulto.id == 1:
              quantity = float(asignarcantidad) * float(bultosoriginales) * float(self.unidadesporbulto)
           asignarunidad = self.asignarunidad
           if unidadoriginal != asignarunidad:
               raise UserError("ERROR: No se puede Asignar cantidad de Palets de distinta medida")
               return {}
           ## raise UserError("Se va a generar una nueva linea de " + str(nombreproducto) + " de " + str(asignarcantidad) + " " + str(unidadoriginalname) + " y Total Bultos: " + str(asignarquedaranbultos) + ".")
           self.asignarcantidad = 0
           self.asignarquedaranbultos = 0
           self.asignarunidad = None
           default.update({
           'totalbultos': asignarquedaranbultos,
           'cantidadpedido': asignarcantidad,
           'quantity': quantity,
           'totalkglin': totalkglin,		   
           'expediente': asignarexpediente,
           'discount': 0,
           'price_unit': 0,
           'asignarmadre': idline,
           'asignaroriginal': True,
           'ctavtarepasado': True,
           })
           reslinresult = super(ModelAccountInvoiceLine, self).copy(default)		   
           

           return {} 

     @api.onchange('asignarcantidad') 
     def on_change_asignarcantidad(self):
           idline = self.id
           cantidadoriginal = self.cantidadpedido
           totalbultosoriginales = self.totalbultos
           bultosoriginales = self.bultos
           asignarcantidad = self.asignarcantidad
           self.asignarquedaran = cantidadoriginal - asignarcantidad
           self.asignarquedaranbultos = totalbultosoriginales - ( asignarcantidad * bultosoriginales ) 

           return {}



class ModelPrepAlbComp(models.Model):
      
     _name = 'jovimer_preparaalbaranc'
     _description = 'Prepara Albarán de Compra'


     # Campos 
     name  = fields.Many2one('account.invoice', string='Albarán Compra', domain=[('journal_id','=', 9)])
     partner  = fields.Many2one('res.partner', string='Partner')
     fecha = fields.Date(string='Fecha')
     pol = fields.Many2many("purchase.order.line", string="Lineas de Compra")


     def preparaalbarancompra(self, default=None):
           id = str(self.id)
           args = ["/opt/jovimer12/bin/importalineascompra.bash", id, "&"]
           subprocess.call(args)
           return {}


class ModelPrepFactVta(models.Model):
      
     _name = 'jovimer_preparafacturav'
     _description = 'Prepara Factura de Venta'


     # Campos 
     name  = fields.Many2one('account.invoice', string='Factura Venta')
     partner  = fields.Many2one('res.partner', string='Partner')
     fecha = fields.Date(string='Fecha')
     pol = fields.Many2many("account.invoice.line", string="Lineas de Albarán de Venta")

     def preparafacturaventa(self, default=None):
           id = str(self.id)
           args = ["/opt/jovimer12/bin/importalineasalbaranventa.bash", id, "&"]
           subprocess.call(args)
           return {}


class ModelPrepAlbVta(models.Model):
      
     _name = 'jovimer_preparaalbaranv'
     _description = 'Prepara Albarán de Venta'


     # Campos 
     name  = fields.Many2one('account.invoice', string='Albarán Venta', domain=[('journal_id','=', 10)])
     partner  = fields.Many2one('res.partner', string='Partner')
     fecha = fields.Date(string='Fecha')
     pol = fields.Many2many("account.invoice.line", string="Lineas de Albarán de Compra")

     def preparaalbaranventa(self, default=None):
           id = str(self.id)
           args = ["/opt/jovimer12/bin/importalineasventa.bash", id, "&"]
           subprocess.call(args)
           return {}


class ModelPrepALMAlbVta(models.Model):
      
     _name = 'jovimer_preparaalmalbaranv'
     _description = 'Prepara Insertar desde Almacén'


     # Campos 
     name  = fields.Many2one('account.invoice', string='Albarán Venta', domain=[('journal_id','=', 10)])
     partner  = fields.Many2one('res.partner', string='Partner')
     fecha = fields.Date(string='Fecha')
     cantidad = fields.Float(string='Cantidad')
     pol = fields.Many2many("jovimer_devalbaranv", string="Lineas de Albarán de Compra")
     pol2 = fields.Many2one("jovimer_devalbaranv", string="Lineas de Albarán de Compra")
     exporig = fields.Many2one('jovimer_expedientes', string='Entidad', related='pol2.expediente')	 
     cantidadorig = fields.Integer(string='Cantidad Origen', related='pol2.cantidad')	
     proveedororig = fields.Many2one('res.partner', string='Proveedor', related='pol2.proveedorrel')	 
     lineaafcetada = fields.Many2one('account.invoice.line', string='Linea BASE', related='pol2.name')
     cantidadorig = fields.Integer(string='Cantidad Origen', related='pol2.cantidad')	


     def preparaimportacion(self, default=None):
           id = self.id
           observaciones = ''
           albdest = self.name.id
           cantidad = self.cantidad
           cantidadorigen = float(self.cantidadorig)
           lineaafcetadaid = self.lineaafcetada.id
           lineaafcetadaexpname = self.lineaafcetada.expediente.name
           lineaafcetadaexpserie = self.lineaafcetada.expediente.campanya
           expedientedestino = self.name.expediente.id
           lineacompra = self.lineaafcetada.lineacompra.id
           lineaventa = self.lineaafcetada.lineaventa.id
           ## Basicos
           today = date.today()
           parent = albdest
           partner = self.partner.id       

           ## Arrastrados
           plantilla = self.lineaafcetada.plantilla.id
           product_id = self.lineaafcetada.product_id.id
           productname = self.lineaafcetada.product_id.product_tmpl_id.productomaestro.name
           variedad = self.lineaafcetada.variedad.id
           variedadname = self.lineaafcetada.variedad.name
           calibre = self.lineaafcetada.calibre.id
           categoria = self.lineaafcetada.categoria.id
           confeccion = self.lineaafcetada.confeccion.id
           confeccionname = self.lineaafcetada.confeccion.name
           envase = self.lineaafcetada.envase.id
           marca = self.lineaafcetada.marca.id
           bultos = self.lineaafcetada.bultos
           kgnetbulto = self.lineaafcetada.kgnetbulto
           cantidadpedido = self.lineaafcetada.cantidadpedido
           unidadpedido = self.lineaafcetada.unidadpedido.id
           unidabulto = self.lineaafcetada.unidabulto.id
           namedesc = str(productname) + ' ' + str(confeccionname) + ' ' + str(variedadname) + ''	   
           totalbultos = cantidad

		   


           if cantidad > cantidadorigen:
              raise UserError("No puedes Asignar " + str(cantidad) + " Bultos, es más de lo que tiene el Almacén: " + str(cantidadorigen) + ".")
           else:
              resultado = cantidadorigen - cantidad
              observaciones += str(self.pol2.observaciones) + '\nEL ' + str(today) + ' se envian ' + str(cantidad) + ' a '  + str(lineaafcetadaexpserie) + '-'  + str(self.name.expediente.name) + '. Con un ORIGINAL de ' + str (cantidadorigen) + ', quedando ' + str(resultado) + '\n' 
              ## raise UserError("Insertaremos en el Documento: " + str(albdest) + " La informacion de la linea del producto: " + str(lineaafcetadaid) + ". Done recogeras: " + str(cantidad) + " y el Almacén se quedará con " + str(resultado) + ", de los " + str(cantidadorigen) + " que quedaban.")
              orderline_obj = self.env['account.invoice.line']
              invoice = orderline_obj.create({
                   'invoice_id': parent,
                   'partner_id': partner,
                   'product_id': 17,
                   'price_unit': 0,
                   'account_id': 480,
                   'plantilla': plantilla,
                   'expediente': expedientedestino,
                   'lineacompra': lineacompra,
                   'lineaventa': lineaventa,
                   'product_id': product_id,
                   'variedad': variedad,
                   'calibre': calibre,
                   'unidabulto': unidabulto,
                   'categoria': categoria,
                   'confeccion': confeccion,
                   'envase': envase,
                   'marca': marca,
                   'name': namedesc,
                   'bultos': bultos,
                   'totalbultos': cantidad,   
                   'kgnetbulto': kgnetbulto, 
                   'cantidadpedido': 1, 
                   'unidadpedido': unidadpedido, 				   
                   'obsbultos': 'DESDE ALMACEN: '  + str(lineaafcetadaexpserie) + '-'  + str(lineaafcetadaexpname) + '', 
                   'currency_id': 1, })

              self.pol2.write({'observaciones': observaciones,'cantidad': resultado})
           return {}



class ModelDevAlbVta(models.Model):
      
     _name = 'jovimer_devalbaranv'
     _description = 'Prepara Devolución'


     # Campos 
     name = fields.Many2one('account.invoice.line', string='Linea Albarán Venta', domain=[('journal_id','=', 10)])  
     lininv = fields.Many2one('account.invoice.line', string='Linea Albarán Venta', domain=[('journal_id','=', 10)])
     partner  = fields.Many2one('res.partner', string='Entidad', related='name.partner_id')
     product_id  = fields.Many2one('product.product', string='Producto', related='name.product_id')
     expediente  = fields.Many2one('jovimer_expedientes', string='Expediente', related='name.expediente')
     expediente_serien = fields.Many2one('jovimer_expedientes.series', related='expediente.serie')  
     proveedorrel = fields.Many2one('res.partner', string='Proveedor', related='name.lineacompra.partner_id')	 
     documentodestino  = fields.Many2one('account.invoice', string='Documento Destino')
     clientefinal= fields.Many2one('res.partner', related='expediente.cliente')
     plantilla = fields.Many2one('jovimer_plantillaproductos', string='Plantilla de Producto', related='name.plantilla')
     variedad = fields.Many2one('jovimer_variedad', string='Variedad', related='name.variedad')
     confeccion = fields.Many2one('jovimer_confeccion', string='Confección', related='name.confeccion')
     totalbultos = fields.Float(string='Total Bultos Origen', related='name.totalbultos')

     ## albproveedorrel = fields.Many2one('account.invoice', string='Num Compra', related='name.lineacompra.name')
     fecha = fields.Date(string='Fecha Devolucion')
     cantidad = fields.Integer(string='Bultos')
     asignar = fields.Integer(string='ASIGNACION')
     observaciones  = fields.Text(string='Observaciones')
     confirmado  = fields.Boolean(string='Confirmado')
     almacen = fields.Selection([
		('CHEQUIA','CHEQUIA'),
		('ESLOVENIA','ESLOVENIA'),
		('XERESA','XERESA'),
		],string='Almacen',default='CHEQUIA')

     def devuelvealbaranventa(self, default=None):
           id = self.id
           inlineid = self.name.id
           cantidadoriginal = self.name.totalbultos
           cantidaddevuelta = self.cantidad
           if cantidaddevuelta > cantidadoriginal:
              raise UserError("No puedes Devolver más que lo que tiene el albarán")
           else:
              cantidadresultante = cantidadoriginal - cantidaddevuelta
              ## self.env.cr.execute(""" UPDATE account_invoice_line SET totalbultos='%s',quantity='0',obsbultos='Devolucion %s' where id='%s' """ % (cantidadresultante,cantidaddevuelta,inlineid)) 
              self.write({'confirmado': True})			  
           return {}



class ModelDevAlbVta(models.Model):
      
     _name = 'jovimer_generaalbaranes'
     _description = 'Genera Albaranes'


     # Campos 
     name = fields.Char(string='Nombre')
     expedientes = fields.Many2many('jovimer_expedientes', string='Expediente')
     lineascompra = fields.Many2many('purchase.order.line', string='Lineas de Compra')
     lineasventa = fields.Many2many('sale.order.line', string='Lineas de Venta')
     estado = fields.Char(string='Estado')
     observaciones  = fields.Text(string='Observaciones')


     @api.onchange('expedientes')
     def on_change_expedientes(self):
            idline = self.id
            fecha =  datetime.today()
            strexp = ""         
            for x in self.expedientes:
                idexp = x.id
                serieexp = x.campanya
                numexp = x.name
                self.env.cr.execute(""" select id from sale_order_line where expediente='%s' """ % (idexp))
                resultvta = self.env.cr.fetchall()
                ### self.write({'lineasventa':[(4,resultvta)]})
                for v in resultvta:
                    idlinevta = resultvta[0]
                    idlinevta = 4433
                    ## self.write({'lineasventa':[(4,idlinevta)]})
                    ### raise UserError("Esta es la linea: " + str(idlinevta) + ".")
                    ### self.env.cr.execute(""" INSERT INTO jovimer_generaalbaranes_sale_order_line_rel (jovimer_generaalbaranes_id,sale_order_line_id) VALUES ('%s','%s') """ % (idline,idlinevta))
                ## raise UserError("Esta es la linea: " + str(result) + ".")
                strexp += str(serieexp) + "-" + str(numexp) + ","
			## self.env.cr.execute(""" select sum(numpalets) from jovimer_lineascompra where order_id='%s'""" % (order))
            self.name = str(fecha) + " : " + str(strexp)
            return {}


     def buscarlineas(self, default=None):
            idline = self.id
            observaciones = 'ID= ' + str(idline) + ': ' 
            self.env.cr.execute(""" DELETE FROM jovimer_generaalbaranes_sale_order_line_rel where jovimer_generaalbaranes_id='%s' """ % (idline))
            self.env.cr.execute(""" DELETE FROM jovimer_generaalbaranes_purchase_order_line_rel where jovimer_generaalbaranes_id='%s' """ % (idline))
            for x in self.expedientes:
                idexp = x.id 
                self.env.cr.execute(""" select id from purchase_order_line where expediente='%s' and lineafacturacompra is null """ % (idexp))
                resultcompra = self.env.cr.fetchall()
                for c in resultcompra:
                    ## self.write({'observaciones': 'ID: ' + str(idline) + '-' + str(resultvta) + str '.'})
                    idlinecomp = c[0]
                    observaciones += str(idlinecomp) + ','
                    self.write({'lineascompra':[(4,idlinecomp)]})

                self.env.cr.execute(""" select id from sale_order_line where expediente='%s' """ % (idexp))
                resultvta = self.env.cr.fetchall()
                for v in resultvta:
                    ## self.write({'observaciones': 'ID: ' + str(idline) + '-' + str(resultvta) + str '.'})
                    idlinevta = v[0]
                    observaciones += str(idlinevta) + ','
                    self.write({'lineasventa':[(4,idlinevta)]})
            self.write({'observaciones': str(observaciones)})

     def crearalbaranes(self, default=None):
            idline = self.id            
            self.env.cr.execute(""" SELECT purchase_order_line_id FROM jovimer_generaalbaranes_purchase_order_line_rel where jovimer_generaalbaranes_id='%s' """ % (idline))
            resultcompra = self.env.cr.fetchall()
            quehago = ""
            for c in resultcompra:
                ## self.write({'observaciones': 'ID: ' + str(idline) + '-' + str(resultvta) + str '.'})
                idlinecomp = c[0]
                quehago += str(idlinecomp) + ','
                self.env.cr.execute(""" UPDATE purchase_order_line SET  idgeneraalbaranes='%s' where id='%s'""" % (idline,idlinecomp))
            args = ["/opt/jovimer12/bin/crearalbaran_genera.bash", str(idline), "&"]
            subprocess.call(args)


            ## raise UserError("Voy a editar las lineas: " + str(quehago) + ".")


class ModelImpuestosybases(models.Model):
      
     _inherit = 'account.invoice.tax'

     diariofactura = fields.Many2one(string='Diario', related='invoice_id.journal_id')
     state = fields.Selection([('draft','Draft'),('open', 'Open'),('in_payment', 'In Payment'),('paid', 'Paid'),('cancel', 'Cancelled'),('albcv', 'Albaran Compra'),('albcvv', 'Albaran Venta'),], string='Status', related='invoice_id.state')



     def rest1cent(self, default=None):
         try:
            idline = self.id            
            base = self.base
            amount = self.amount
            resultado = float(base) - 0.01
            factura = self.invoice_id.id
            amount_untaxed = self.invoice_id.amount_untaxed
            amount_total = self.invoice_id.amount_total
            self.base = resultado
            self.invoice_id.amount_untaxed = amount_untaxed - 0.01           ## raise AccessError("A la factura: " + str(factura) + " Restaremos 1 CT a la base " + str(base) + " y se quedará en " + str(resultado) + "")
            self.invoice_id.amount_total = amount_total - 0.01
            self.invoice_id.totalesmanuales = True
         except:
            raise AccessError("Ha habido un Error al realizar el redondeo de la base del iva")


     def sum1cent(self, default=None):
         try:
            idline = self.id            
            base = self.base
            amount = self.amount
            resultado = float(base) + 0.01
            factura = self.invoice_id.id
            amount_untaxed = self.invoice_id.amount_untaxed
            amount_total = self.invoice_id.amount_total
            self.base = resultado
            self.invoice_id.amount_untaxed = amount_untaxed + 0.01           ## raise AccessError("A la factura: " + str(factura) + " Restaremos 1 CT a la base " + str(base) + " y se quedará en " + str(resultado) + "")
            self.invoice_id.amount_total = amount_total + 0.01
            self.invoice_id.totalesmanuales = True
         except:
            raise AccessError("Ha habido un Error al realizar el redondeo de la base del iva")



class ModelGeneraAbonoCliente(models.Model):
      
     _name = 'jovimer_abonocliente'
     _description = 'Generar Factura Abono'


     # Campos 
     name  = fields.Many2one('res.partner', string='Cliente', domain=[('customer','=',True)])
     fecha = fields.Date(string='Fecha Factura', default=date.today())
     fecharect = fields.Date(string='Fecha Operacion Rectificativa')
     diario = fields.Many2one('account.journal', string="Diario Destino", domain=[('id','in',[22,21,20,15])])
     facturaresultante = fields.Many2one('account.invoice', string="Factura Resultante", domain=[('type','=','out_refound')])
     facturas = fields.Many2many('account.invoice.line', string="Lineas Facturas Afectadas", domain=[('invoice_id.type','=','out_invoice'),('diariofactura','!=',9)])
     estado = fields.Char(string="Estado")

     def facturaifcos(self, default=None):
           id = str(self.id)
           partner_id = str(self.partner_id)
           args = ["/opt/jovimer12/bin/insertalineasifco.bash", id, "&"]
           ## args = ["/opt/jovimer12/bin/webservice/insertalineaifco.py", id, partner_id, "&"]
           subprocess.call(args)
           return {}
		   
class ModelBasuraoDevolucionAlbaran(models.Model):
      
     _name = 'jovimer_basuraodevolucion'
     _description = 'Wozard Devolucion o Basura'


     # Campos 
     name  = fields.Many2one('account.invocie.line', string='Linea que lo Genera')
     ## plantilla  = fields.Many2one('jovimer_plantillaproductos', string='Plantilla de Producto', related='name.plantilla')
     ## variedad  = fields.Many2one('jovimer_variedad', string='Variedad', related='name.variedad')
     ## confeccion  = fields.Many2one('jovimer_confeccion', string='Confeccion', related='name.confeccion')
     fecha = fields.Date(string='Fecha Movimiento', default=date.today())
     totalbultos = fields.Float(string='Total Bultos')
     totalkilos = fields.Float(string="Total Bultos")
     albarandestino = fields.Many2one('account.invoice', string="Documento Destino", domain=[('id','in',[9,10])])
     estado = fields.Char(string="Estado")

     def generamovimiento(self, default=None):
           raise UserError("HOLA")
           return {}		   
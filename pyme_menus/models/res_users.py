# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError
	
class CreateCustomPyme(models.Model):
    _inherit = "res.users"
    
    # Personalizacion
    ## estadopyme = fields.Char(store=True, readonly=False)
    



    def action_create_pyme(self):
         raise UserError(_("No Puedes Generar Usuarios"))
         return self.action_cancel()

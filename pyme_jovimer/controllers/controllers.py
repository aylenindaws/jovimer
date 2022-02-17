# -*- coding: utf-8 -*-
from odoo import http

# class ../custom-addons/dialogflow(http.Controller):
#     @http.route('/../custom-addons/dialogflow/../custom-addons/dialogflow/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/../custom-addons/dialogflow/../custom-addons/dialogflow/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('../custom-addons/dialogflow.listing', {
#             'root': '/../custom-addons/dialogflow/../custom-addons/dialogflow',
#             'objects': http.request.env['../custom-addons/dialogflow.../custom-addons/dialogflow'].search([]),
#         })

#     @http.route('/../custom-addons/dialogflow/../custom-addons/dialogflow/objects/<model("../custom-addons/dialogflow.../custom-addons/dialogflow"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('../custom-addons/dialogflow.object', {
#             'object': obj
#         })
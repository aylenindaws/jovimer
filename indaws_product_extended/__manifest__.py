# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Ajustes de Productos",
    "author" : "Indaws",
    "version":"14.0.4",
    "depends" : ['sale', 'base', 'product','stock','bi_convert_purchase_from_sales','purchase_discount','stock_picking_batch','report_py3o'],
    "data": [
        "security/security.xml",
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/jovimer_calibre.xml',
        'views/jovimer_categoria.xml',
        'views/jovimer_confeccion.xml',
        'views/jovimer_envase.xml',
        'views/jovimer_etiquetas.xml',
        'views/jovimer_etiquetas_plantillas.xml',
        'views/jovimer_expedientes.xml',
        'views/jovimer_expedientes_series.xml',
        'views/jovimer_marca.xml',
        'views/jovimer_variedad.xml',
        'views/jovimer_conflote.xml',
        'views/jovimer_palet.xml',
        'views/jovimer_plataforma.xml',
        'views/jovimer_partner_code.xml',
        'views/purchase_order.xml',
        'views/jovimer_reclamaciones.xml',
        'views/stock_picking_batch.xml',
        'views/sale_order.xml',
        'wizard/purchase_order_wizard_views.xml',
        'views/product_template.xml',
        'views/stock_move.xml',
        'views/account_move.xml',
        'views/ir_menus.xml',
        'views/prints.xml',
        'views/purchase_order_wizard_view.xml',
        'data/template_email_claim.xml',
        'data/template_email_purchase_claim.xml'
    ],
    "images": ["static/description/background.png",],              
    "application": True,
    "auto_install":False,
    "installable" : True,
    "currency": "EUR"   
}

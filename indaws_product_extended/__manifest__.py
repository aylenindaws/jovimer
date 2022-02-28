# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Ajustes de Productos",
    "author" : "Indaws",
    "version":"14.0.1",
    "depends" : ['sale', "base", "product","stock","bi_convert_purchase_from_sales"],
    "data": [
        "security/security.xml",
        'security/ir.model.access.csv',
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
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/product_template.xml',
        'views/ir_menus.xml',
        'views/prints.xml',
    ],
    "images": ["static/description/background.png",],              
    "application": True,
    "auto_install":False,
    "installable" : True,
    "currency": "EUR"   
}

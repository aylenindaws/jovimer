# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Ajustes de Ventas y Compras",
    "author" : "Indaws",
    "version":"14.0.1",
    "depends" : ['sale', "base", "indaws_product_extended",'purchase'],
    "data": [
        "security/security.xml",
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'security/ir.model.access.csv',
    ],
    "images": ["static/description/background.png",],              
    "application": True,
    "auto_install":False,
    "installable" : True,
    "currency": "EUR"   
}

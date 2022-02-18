# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Ajustes de Productos",
    "author" : "Indaws",
    "version":"14.0.1",
    "depends" : ['sale', "base", "product","stock"],
    "data": [
        "security/security.xml",
        'views/product_template.xml',
        'security/ir.model.access.csv',
        'views/jovimer_calibre.xml',
        'views/ir_menus.xml',
    ],
    "images": ["static/description/background.png",],              
    "application": True,
    "auto_install":False,
    "installable" : True,
    "currency": "EUR"   
}

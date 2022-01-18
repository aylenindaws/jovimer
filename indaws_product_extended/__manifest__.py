# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Ajustes de Productos",
    "author" : "Indaws",
    "version":"14.0.1",
    "depends" : ['sale', "base", "product"],
    "data": [
        "security/security.xml",
        'views/product_template.xml',
        #'security/ir.model.access.csv',
    ],
    "images": ["static/description/background.png",],              
    "application": True,
    "auto_install":False,
    "installable" : True,
    "currency": "EUR"   
}

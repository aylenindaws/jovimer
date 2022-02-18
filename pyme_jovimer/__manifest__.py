# -*- coding: utf-8 -*-
{
    'name': "PYME - Jovimer",

    'summary': """
        Perosnalizacion JOVIMER Proceso de Compra Venta
    """,

    'description': """
        Modulo Extendido de Llamadas para Contacto y Relacion de DialogFlow
    """,

    'author': "MAIN INFORMATICA GANDIA SL",
    'website': "http://www.main-informatica.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'pyme_menus'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/transporte.xml',
        'views/reclamaciones.xml',
        'views/facturacion.xml',
        'views/jovimer_caracteristicas.xml',
        'views/menus.xml',
        'views/etiquetas.xml',        
        'views/impresora.xml',
        'views/calidad.xml',
        'views/tesoreria.xml',
        'views/almacen.xml',
    ],
    
    'installable': True,
    'auto_install': False,
    'application': True,       
}
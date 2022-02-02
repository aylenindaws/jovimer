# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Importación de datos de proveedores",
    "summary": "Importación de datos de proveedores",
    'version': '14.0.1.0.0',
    "category": "Project",
    "website": "www.indaws.es",
    "author": "INDAWS",

    "license": "AGPL-3",
    'application': False,
    'installable': True,
    'auto_install': False,
    "depends": [
        "sale",
        "purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase.xml",
    ],

}

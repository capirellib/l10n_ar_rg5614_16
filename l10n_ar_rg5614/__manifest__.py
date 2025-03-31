# -*- coding: utf-8 -*-
{
    "name": " RG 5614 ",
    "version": "15.0.0.0.0",
    "summary": """ 
                   comprobantes emitidos a consumidores finales deberán discriminar 
                   los impuestos nacionales indirectos, incluido el IVA.a  """,
    "author": "Carlos Esteban Pirelli - BettaErp",
    "website": "",
    "category": "Localizacion",
    "depends": ["account", "l10n_ar"],
    "data": [
        
        "views/report_invoice_views.xml"
    ],
    "assets": {
        "web.assets_backend": [],
        "web.assets_qweb": [],
    },
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}

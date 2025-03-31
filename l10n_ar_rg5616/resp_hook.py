# -*- coding: utf-8 -*-
import logging
from odoo import api, SUPERUSER_ID


_logger = logging.getLogger(__name__)


def _create_or_update_afip_responsibility_type(cr, registry):
    _logger.info("Ejecutando post_init_hook")

    env = api.Environment(cr, SUPERUSER_ID, {})

    # Modificar el registro existente con ID l10n_ar.res_EXT
    ext_record = env["l10n_ar.afip.responsibility.type"].search(
        [("id", "=", env.ref("l10n_ar.res_EXT").id)]
    )
    if ext_record:
        ext_record.write(
            {
                "code": 9,
                "name": "Cliente del Exterior",
                "active": True,
            }
        )
    else:
        env["l10n_ar.afip.responsibility.type"].create(
            {
                "code": 9,
                "name": "Cliente del Exterior",
                "active": True,
            }
        )

    # Crear un nuevo registro con código 8 para Proveedores del Exterior
    prov_ext_record = env["l10n_ar.afip.responsibility.type"].search([("code", "=", 8)])
    if not prov_ext_record:
        env["l10n_ar.afip.responsibility.type"].create(
            {
                "code": 8,
                "name": "Proveedores del Exterior",
                "active": True,
            }
        )
    _logger.info("post_init_hook completado")

# def post_init_hook(cr, registry):
#     _logger.info("Ejecutando post_init_hook")
#     _create_or_update_afip_responsibility_type(cr, registry)
#     _logger.info("post_init_hook completado")
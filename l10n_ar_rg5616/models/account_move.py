##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import float_repr

# from odoo.addons.l10n_ar_afipws_fe.afip_utils import get_invoice_number_from_response
import base64

base64.encodestring = base64.encodebytes
import json
import logging
import sys
import traceback
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


try:
    from pysimplesoap.client import SoapFault
except ImportError:
    _logger.debug("Can not `from pyafipws.soap import SoapFault`.")
_


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_ar_payment_foreign_currency = fields.Selection(
        [("S", "Yes"), ("N", "No")],
        compute="compute_l10n_ar_payment_foreign_currency",
        store=True,
        readonly=False,
    )
    l10n_ar_currency_code = fields.Char("Currency Code", related="currency_id.name")

    @api.onchange("currency_id", "line_ids")
    @api.depends("currency_id")
    def compute_l10n_ar_payment_foreign_currency(
        self,
    ):  # odoo 15 no tiene el campo account_type en account.account. entonces se usa lo que tiene.
        self.l10n_ar_payment_foreign_currency = False
        for move in self:
            default_value = move.company_id.l10n_ar_payment_foreign_currency
            if default_value == "account":
                # Se filtran las cuentas que tengan un user_type_id cuyo type sea "receivable"
                receivable_accounts = move.line_ids.account_id.filtered(
                    lambda a: a.user_type_id.type == "receivable"
                )
                # Se usa la primera cuenta recibida para determinar si la moneda de la cuenta
                # difiere de la moneda de la compañía.
                if (
                    receivable_accounts
                    and receivable_accounts[0].currency_id
                    and receivable_accounts[0].currency_id != move.company_currency_id
                ):
                    default_value = "S"
                else:
                    default_value = "N"
            move.l10n_ar_payment_foreign_currency = default_value

    
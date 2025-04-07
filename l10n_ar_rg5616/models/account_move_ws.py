# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime
import logging
import pprint

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def wsfe_pyafipws_create_invoice(self, ws, invoice_info):
        
        ws.CrearFactura(
            invoice_info["concepto"],
            invoice_info["tipo_doc"],
            invoice_info["nro_doc"],
            invoice_info["doc_afip_code"],
            invoice_info["pos_number"],
            invoice_info["cbt_desde"],
            invoice_info["cbt_hasta"],
            invoice_info["imp_total"],
            invoice_info["imp_tot_conc"],
            invoice_info["imp_neto"],
            invoice_info["imp_iva"],
            invoice_info["imp_trib"],
            invoice_info["imp_op_ex"],
            invoice_info["fecha_cbte"],
            invoice_info["fecha_venc_pago"],
            invoice_info["fecha_serv_desde"],
            invoice_info["fecha_serv_hasta"],
            invoice_info["moneda_id"],
            invoice_info["moneda_ctz"],
            invoice_info["cancela_misma_moneda_ext"],
            invoice_info["condicion_iva_receptor_id"],
        )

    def wsmtxca_pyafipws_create_invoice(self, ws, invoice_info):
        ws.CrearFactura(
            invoice_info["concepto"],
            invoice_info["tipo_doc"],
            invoice_info["nro_doc"],
            invoice_info["doc_afip_code"],
            invoice_info["pos_number"],
            invoice_info["cbt_desde"],
            invoice_info["cbt_hasta"],
            invoice_info["imp_total"],
            invoice_info["imp_tot_conc"],
            invoice_info["imp_neto"],
            invoice_info["imp_subtotal"],
            invoice_info["imp_trib"],
            invoice_info["imp_op_ex"],
            invoice_info["fecha_cbte"],
            invoice_info["fecha_venc_pago"],
            invoice_info["fecha_serv_desde"],
            invoice_info["fecha_serv_hasta"],
            invoice_info["moneda_id"],
            invoice_info["moneda_ctz"],
            invoice_info["obs_generales"],
            invoice_info["cancela_misma_moneda_ext"],
            invoice_info["condicion_iva_receptor_id"],
        )

    def wsfex_pyafipws_create_invoice(self, ws, invoice_info):
        ws.CrearFactura(
            invoice_info["doc_afip_code"],
            invoice_info["pos_number"],
            invoice_info["cbte_nro"],
            invoice_info["fecha_cbte"],
            invoice_info["imp_total"],
            invoice_info["tipo_expo"],
            invoice_info["permiso_existente"],
            invoice_info["pais_dst_cmp"],
            invoice_info["nombre_cliente"],
            invoice_info["cuit_pais_cliente"],
            invoice_info["domicilio_cliente"],
            invoice_info["id_impositivo"],
            invoice_info["moneda_id"],
            invoice_info["moneda_ctz"],
            invoice_info["obs_comerciales"],
            invoice_info["obs_generales"],
            invoice_info["forma_pago"],
            invoice_info["incoterms"],
            invoice_info["idioma_cbte"],
            invoice_info["incoterms_ds"],
            invoice_info["fecha_pago"],
            invoice_info["cancela_misma_moneda_ext"],
            invoice_info["condicion_iva_receptor_id"],
        )

    def wsbfe_pyafipws_create_invoice(self, ws, invoice_info):
        ws.CrearFactura(
            invoice_info["tipo_doc"],
            invoice_info["nro_doc"],
            invoice_info["zona"],
            invoice_info["doc_afip_code"],
            invoice_info["pos_number"],
            invoice_info["cbte_nro"],
            invoice_info["fecha_cbte"],
            invoice_info["imp_total"],
            invoice_info["imp_neto"],
            invoice_info["imp_iva"],
            invoice_info["imp_tot_conc"],
            invoice_info["impto_liq_rni"],
            invoice_info["imp_op_ex"],
            invoice_info["imp_perc"],
            invoice_info["imp_iibb"],
            invoice_info["imp_perc_mun"],
            invoice_info["imp_internos"],
            invoice_info["moneda_id"],
            invoice_info["moneda_ctz"],
            invoice_info["fecha_venc_pago"],
            invoice_info["cancela_misma_moneda_ext"],
            invoice_info["condicion_iva_receptor_id"],
        )

    def base_map_invoice_info(self):
        journal = self.journal_id
        invoice_info = {}

        invoice_info["cancela_misma_moneda_ext"] = self.l10n_ar_payment_foreign_currency
        invoice_info["condicion_iva_receptor_id"] = (
            self.partner_id.l10n_ar_afip_responsibility_type_id.code
        )

        invoice_info["commercial_partner"] = self.commercial_partner_id
        invoice_info["country"] = invoice_info["commercial_partner"].country_id
        invoice_info["journal"] = self.journal_id
        invoice_info["pos_number"] = journal.l10n_ar_afip_pos_number
        invoice_info["doc_afip_code"] = self.l10n_latam_document_type_id.code
        invoice_info["ws_next_invoice_number"] = (
            int(
                self.journal_id.get_pyafipws_last_invoice(
                    self.l10n_latam_document_type_id
                )
            )
            + 1
        )

        invoice_info["partner_id_code"] = invoice_info[
            "commercial_partner"
        ].l10n_latam_identification_type_id.l10n_ar_afip_code
        invoice_info["tipo_doc"] = invoice_info["partner_id_code"] or "99"
        invoice_info["nro_doc"] = (
            invoice_info["partner_id_code"]
            and invoice_info["commercial_partner"].vat
            or "0"
        )
        invoice_info["cbt_desde"] = invoice_info["cbt_hasta"] = invoice_info[
            "cbte_nro"
        ] = invoice_info["ws_next_invoice_number"]
        invoice_info["concepto"] = invoice_info["tipo_expo"] = int(
            self.l10n_ar_afip_concept
        )

        invoice_info["fecha_cbte"] = self.invoice_date or fields.Date.today()
        invoice_info["mipyme_fce"] = int(invoice_info["doc_afip_code"]) in [
            201,
            206,
            211,
        ]
        invoice_info["fecha_venc_pago"] = None

        # due date only for concept "services" and mipyme_fce
        if (
            invoice_info["concepto"] != 1
            and int(invoice_info["doc_afip_code"]) not in [202, 203, 207, 208, 212, 213]
            or invoice_info["mipyme_fce"]
        ):
            invoice_info["fecha_venc_pago"] = self.invoice_date_due or self.invoice_date
        invoice_info["fecha_serv_desde"] = invoice_info["fecha_serv_hasta"] = None

        # fecha de servicio solo si no es 1
        if int(invoice_info["concepto"]) != 1:
            invoice_info["fecha_serv_desde"] = self.l10n_ar_afip_service_start
            invoice_info["fecha_serv_hasta"] = self.l10n_ar_afip_service_end

        amounts = self._l10n_ar_get_amounts()
        invoice_info["amounts"] = amounts
        # invoice amount totals:
        invoice_info["imp_total"] = str("%.2f" % self.amount_total)
        # ImpTotConc es el iva no gravado
        invoice_info["imp_tot_conc"] = str("%.2f" % amounts["vat_untaxed_base_amount"])
        # tal vez haya una mejor forma, la idea es que para facturas c
        # no se pasa iva. Probamos hacer que vat_taxable_amount
        # incorpore a los imp cod 0, pero en ese caso termina reportando
        # iva y no lo queremos
        if self.l10n_latam_document_type_id.l10n_ar_letter == "C":
            invoice_info["imp_neto"] = str("%.2f" % self.amount_untaxed)
        else:
            invoice_info["imp_neto"] = str("%.2f" % amounts["vat_taxable_amount"])

        invoice_info["imp_iva"] = str("%.2f" % amounts["vat_amount"])
        invoice_info["imp_trib"] = str("%.2f" % amounts["not_vat_taxes_amount"])
        invoice_info["imp_op_ex"] = str("%.2f" % amounts["vat_exempt_base_amount"])
        invoice_info["moneda_id"] = self.currency_id.l10n_ar_afip_code
        invoice_info["moneda_ctz"] = self.l10n_ar_currency_rate or 1
        invoice_info["CbteAsoc"] = self.get_related_invoices_data()

        invoice_info["afip_associated_period_from"] = self.afip_associated_period_from
        invoice_info["afip_associated_period_to"] = self.afip_associated_period_to
        _logger.warning("*********************************************")
        _logger.warning("*********************************************")
        
        _logger.warning(f"Datos enviados a WSFE: {invoice_info}")
        _logger.warning(f"Responsabilidad fiscal: {self.partner_id.l10n_ar_afip_responsibility_type_id}")
        return invoice_info

    def wsfe_request_autorization(self, ws):
        ws.CAESolicitar()

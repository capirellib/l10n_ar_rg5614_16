# -*- coding: utf-8 -*-

import logging
from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import sys
import traceback
from datetime import datetime, date
from collections import defaultdict
from odoo.tools.misc import formatLang 


_logger = logging.getLogger(__name__)


# try:
#     from pysimplesoap.client import SoapFault
# except ImportError:
#     _logger.debug("Can not `from pyafipws.soap import SoapFault`.")

# _logger = logging.getLogger(__name__)


_logger = logging.getLogger(__name__)

# WS_DATE_FORMAT = {"wsfe": "%Y%m%d", "wsfex": "%Y%m%d", "wsbfe": "%Y%m%d"}


class AccountMove(models.Model):
    _inherit = "account.move"

    def _l10n_ar_get_invoice_totals_for_report_5614(self):
        self.ensure_one()
        tax_ids_filter = tax_line_id_filter = None
        include_vat = self._l10n_ar_include_vat_5614()

        if include_vat:
            tax_ids_filter = lambda aml, tax: not bool(
                tax.tax_group_id.l10n_ar_vat_afip_code
            )
            tax_line_id_filter = lambda aml, tax: not bool(
                tax.tax_group_id.l10n_ar_vat_afip_code
            )

        tax_lines_data = self._prepare_tax_lines_data_for_totals_from_invoice(
            tax_ids_filter=tax_ids_filter, tax_line_id_filter=tax_line_id_filter
        )

        if include_vat:
            amount_untaxed = self.currency_id.round(
                self.amount_total
                - sum([x["tax_amount"] for x in tax_lines_data if "tax_amount" in x])
            )
        else:
            amount_untaxed = self.amount_untaxed

        # _logger.warning(
        #     self._get_tax_totals(
        #         self.partner_id,
        #         tax_lines_data,
        #         self.amount_total,
        #         amount_untaxed,
        #         self.currency_id,
        #     )
        # )

        return self._get_tax_totals_5614(
            self.partner_id,
            tax_lines_data,
            self.amount_total,
            amount_untaxed,
            self.currency_id,
        )

    def _l10n_ar_include_vat_5614(self):
        self.ensure_one()
        return self.l10n_latam_document_type_id.l10n_ar_letter in ["C", "X", "R"]

    # def do_pyafipws_request_cae(self):
    #     "Request to AFIP the invoices' Authorization Electronic Code (CAE)"
    #     for inv in self:
    #         # Ignore invoices with cae (do not check date)
    #         if inv.afip_auth_code:
    #             continue

    #         if inv.journal_id.l10n_ar_afip_pos_system not in ["RLI_RLM", "FEERCEL"]:
    #             continue
    #         if inv.journal_id.l10n_ar_afip_pos_system != "FEERCEL":
    #             afip_ws = inv.journal_id.afip_ws
    #         else:
    #             afip_ws = "wsfex"
    #         # Ignore invoice if not ws on point of sale
    #         if not afip_ws:
    #             raise UserError(
    #                 _(
    #                     "If you use electronic journals (invoice id %s) you need "
    #                     "configure AFIP WS on the journal"
    #                 )
    #                 % (inv.id)
    #             )

    #         # if no validation type and we are on electronic invoice, it means
    #         # that we are on a testing database without homologation
    #         # certificates
    #         if not inv.validation_type and afip_ws != "wsfex":
    #             msg = (
    #                 "Factura validada solo localmente por estar en ambiente "
    #                 "de homologación sin claves de homologación"
    #             )
    #             inv.write(
    #                 {
    #                     "afip_auth_mode": "CAE",
    #                     "afip_auth_code": "68448767638166",
    #                     "afip_auth_code_due": inv.invoice_date,
    #                     "afip_result": "",
    #                     "afip_message": msg,
    #                 }
    #             )
    #             inv.message_post(body=msg)
    #             continue

    #         # get the electronic invoice type, point of sale and afip_ws:
    #         # import pdb;pdb.set_trace()
    #         commercial_partner = inv.commercial_partner_id
    #         country = commercial_partner.country_id
    #         journal = inv.journal_id
    #         pos_number = journal.l10n_ar_afip_pos_number
    #         doc_afip_code = inv.l10n_latam_document_type_id.code

    #         # authenticate against AFIP:
    #         ws = inv.company_id.get_connection(afip_ws).connect()

    #         if afip_ws == "wsfex":
    #             if not country:
    #                 raise UserError(
    #                     _('For WS "%s" country is required on partner' % (afip_ws))
    #                 )
    #             elif not country.code:
    #                 raise UserError(
    #                     _(
    #                         'For WS "%s" country code is mandatory'
    #                         "Country: %s" % (afip_ws, country.name)
    #                     )
    #                 )
    #             elif not country.l10n_ar_afip_code:
    #                 raise UserError(
    #                     _(
    #                         'For WS "%s" country afip code is mandatory'
    #                         "Country: %s" % (afip_ws, country.name)
    #                     )
    #                 )
    #         # ws_next_invoice_number = int(
    #         #    inv.journal_document_type_id.get_pyafipws_last_invoice(
    #         #    )['result']) + 1
    #         ws_next_invoice_number = (
    #             int(
    #                 inv.l10n_latam_document_type_id.get_pyafipws_last_invoice(inv)[
    #                     "result"
    #                 ]
    #             )
    #             + 1
    #         )
    #         # verify that the invoice is the next one to be registered in AFIP
    #         # if inv.invoice_number != ws_next_invoice_number:
    #         #    raise UserError(_(
    #         #        'Error!'
    #         #        'Invoice id: %i'
    #         #        'Next invoice number should be %i and not %i' % (
    #         #            inv.id,
    #         #            ws_next_invoice_number,
    #         #            inv.invoice_number)))

    #         partner_id_code = (
    #             commercial_partner.l10n_latam_identification_type_id.l10n_ar_afip_code
    #         )
    #         tipo_doc = partner_id_code or "99"
    #         nro_doc = partner_id_code and commercial_partner.vat or "0"
    #         # cbt_desde = cbt_hasta = cbte_nro = inv.invoice_number
    #         cbt_desde = cbt_hasta = cbte_nro = ws_next_invoice_number
    #         concepto = tipo_expo = int(inv.l10n_ar_afip_concept)

    #         fecha_cbte = inv.invoice_date
    #         if afip_ws != "wsmtxca":
    #             fecha_cbte = inv.invoice_date.strftime("%Y%m%d")

    #         mipyme_fce = int(doc_afip_code) in [201, 206, 211]
    #         # due date only for concept "services" and mipyme_fce
    #         if (
    #             int(concepto) != 1
    #             and int(doc_afip_code) not in [202, 203, 207, 208, 212, 213]
    #             or mipyme_fce
    #         ):
    #             fecha_venc_pago = inv.invoice_date_due or inv.invoice_date
    #             if afip_ws != "wsmtxca":
    #                 fecha_venc_pago = fecha_venc_pago.strftime("%Y%m%d")
    #         else:
    #             fecha_venc_pago = None

    #         # fecha de servicio solo si no es 1
    #         if int(concepto) != 1:
    #             fecha_serv_desde = inv.l10n_ar_afip_service_start
    #             fecha_serv_hasta = inv.l10n_ar_afip_service_end
    #             if afip_ws != "wsmtxca":
    #                 fecha_serv_desde = fecha_serv_desde.strftime("%Y%m%d")
    #                 fecha_serv_hasta = fecha_serv_hasta.strftime("%Y%m%d")
    #         else:
    #             fecha_serv_desde = fecha_serv_hasta = None

    #         # invoice amount totals:
    #         amount_total = inv.amount_untaxed
    #         for move_tax in inv.move_tax_ids:
    #             amount_total += move_tax.tax_amount

    #         imp_total = str("%.2f" % amount_total)
    #         # ImpTotConc es el iva no gravado
    #         imp_tot_conc = str("%.2f" % inv.vat_untaxed_base_amount)
    #         # imp_tot_conc = str("%.2f" % inv.amount_untaxed)
    #         # tal vez haya una mejor forma, la idea es que para facturas c
    #         # no se pasa iva. Probamos hacer que vat_taxable_amount
    #         # incorpore a los imp cod 0, pero en ese caso termina reportando
    #         # iva y no lo queremos
    #         if inv.l10n_latam_document_type_id.l10n_ar_letter == "C":
    #             imp_neto = str("%.2f" % inv.amount_untaxed)
    #         else:
    #             # imp_neto = str("%.2f" % inv.vat_taxable_amount)
    #             imp_neto = str("%.2f" % inv.vat_taxable_amount)
    #         imp_trib = str("%.2f" % inv.other_taxes_amount)
    #         # imp_iva = str("%.2f" % (inv.amount_total - (inv.amount_untaxed + inv.other_taxes_amount)))
    #         imp_iva = str("%.2f" % (inv.vat_amount))
    #         # se usaba para wsca..
    #         # imp_subtotal = str("%.2f" % inv.amount_untaxed)
    #         imp_op_ex = str("%.2f" % inv.vat_exempt_base_amount)
    #         moneda_id = inv.currency_id.l10n_ar_afip_code
    #         # moneda_ctz = round(1/inv.currency_id.rate,2)
    #         moneda_ctz = inv.currency_id.rate
    #         if not moneda_id:
    #             raise ValidationError("No esta definido el codigo AFIP en la moneda")

    #         CbteAsoc = inv.get_related_invoices_data()

    #         # create the invoice internally in the helper
    #         if afip_ws == "wsfe":
    #             moneda_ctz = 1 / moneda_ctz
    #             inv.l10n_ar_currency_rate = moneda_ctz
    #             ws.CrearFactura(
    #                 concepto,
    #                 tipo_doc,
    #                 nro_doc,
    #                 doc_afip_code,
    #                 pos_number,
    #                 cbt_desde,
    #                 cbt_hasta,
    #                 imp_total,
    #                 imp_tot_conc,
    #                 imp_neto,
    #                 imp_iva,
    #                 imp_trib,
    #                 imp_op_ex,
    #                 fecha_cbte,
    #                 fecha_venc_pago,
    #                 fecha_serv_desde,
    #                 fecha_serv_hasta,
    #                 moneda_id,
    #                 round(moneda_ctz, 2),
    #             )
    #             if inv.other_taxes_amount > 0:
    #                 for move_tax in inv.move_tax_ids:
    #                     if move_tax.tax_id.tax_group_id.tax_type != "vat":
    #                         tributo_id = (
    #                             move_tax.tax_id.tax_group_id.l10n_ar_tribute_afip_code
    #                         )
    #                         base_imp = str("%.2f" % move_tax.base_amount)
    #                         desc = move_tax.tax_id.name
    #                         importe = str("%.2f" % move_tax.tax_amount)
    #                         alic = None
    #                         ws.AgregarTributo(tributo_id, desc, base_imp, alic, importe)

    #             ######################################################
    #             ######   Agrega Campos Necesarios para res 5416 ######
    #             ######################################################

    #             ws.WSFE.EstablecerCampoFactura("cancela_misma_moneda_ext", "S")

    #             condicion_iva_receptor = inv.l10n_ar_afip_responsibility_type_id.id
    #             ws.EstablecerCampoFactura(
    #                 "condicion_iva_receptor_id", condicion_iva_receptor
    #             )

    #             ######################################################

    #         # elif afip_ws == 'wsmtxca':
    #         #     obs_generales = inv.coment
    #         #     ws.CrearFactura(
    #         #         concepto, tipo_doc, nro_doc, doc_afip_code, pos_number,
    #         #         cbt_desde, cbt_hasta, imp_total, imp_tot_conc, imp_neto,
    #         #         imp_subtotal,   # difference with wsfe
    #         #         imp_trib, imp_op_ex, fecha_cbte, fecha_venc_pago,
    #         #         fecha_serv_desde, fecha_serv_hasta,
    #         #         moneda_id, moneda_ctz,
    #         #         obs_generales   # difference with wsfe
    #         #     )
    #         elif afip_ws == "wsfex":
    #             # # foreign trade data: export permit, country code, etc.:
    #             if inv.invoice_incoterm_id:
    #                 incoterms = inv.invoice_incoterm_id.code
    #                 incoterms_ds = inv.invoice_incoterm_id.name
    #                 # máximo de 20 caracteres admite
    #                 incoterms_ds = incoterms_ds and incoterms_ds[:20]
    #             else:
    #                 incoterms = incoterms_ds = None
    #             # por lo que verificamos, se pide permiso existente solo
    #             # si es tipo expo 1 y es factura (codigo 19), para todo el
    #             # resto pasamos cadena vacia
    #             if int(doc_afip_code) == 19 and tipo_expo == 1:
    #                 # TODO investigar si hay que pasar si ("S")
    #                 permiso_existente = "N"
    #             else:
    #                 permiso_existente = ""
    #             obs_generales = inv.narration

    #             if inv.invoice_payment_term_id:
    #                 forma_pago = inv.invoice_payment_term_id.name
    #                 obs_comerciales = inv.invoice_payment_term_id.name
    #             else:
    #                 forma_pago = obs_comerciales = None

    #             idioma_cbte = 1  # invoice language: spanish / español

    #             # TODO tal vez podemos unificar este criterio con el del
    #             # citi que pide el cuit al partner
    #             # customer data (foreign trade):
    #             nombre_cliente = commercial_partner.name
    #             # se debe informar cuit pais o id_impositivo
    #             if nro_doc:
    #                 id_impositivo = nro_doc
    #                 cuit_pais_cliente = None
    #             elif country.code != "AR" and nro_doc:
    #                 id_impositivo = None
    #                 if commercial_partner.is_company:
    #                     cuit_pais_cliente = country.cuit_juridica
    #                 else:
    #                     cuit_pais_cliente = country.cuit_fisica
    #                 if not cuit_pais_cliente:
    #                     raise UserError(
    #                         _(
    #                             "No vat defined for the partner and also no CUIT "
    #                             "set on country"
    #                         )
    #                     )

    #             domicilio_cliente = " - ".join(
    #                 [
    #                     commercial_partner.name or "",
    #                     commercial_partner.street or "",
    #                     commercial_partner.street2 or "",
    #                     commercial_partner.zip or "",
    #                     commercial_partner.city or "",
    #                 ]
    #             )
    #             pais_dst_cmp = commercial_partner.country_id.l10n_ar_afip_code
    #             ws.CrearFactura(
    #                 doc_afip_code,
    #                 pos_number,
    #                 cbte_nro,
    #                 fecha_cbte,
    #                 imp_total,
    #                 tipo_expo,
    #                 permiso_existente,
    #                 pais_dst_cmp,
    #                 nombre_cliente,
    #                 cuit_pais_cliente,
    #                 domicilio_cliente,
    #                 id_impositivo,
    #                 moneda_id,
    #                 moneda_ctz,
    #                 obs_comerciales,
    #                 obs_generales,
    #                 forma_pago,
    #                 incoterms,
    #                 idioma_cbte,
    #                 incoterms_ds,
    #             )
    #         elif afip_ws == "wsbfe":
    #             zona = 1  # Nacional (la unica devuelta por afip)
    #             # los responsables no inscriptos no se usan mas
    #             impto_liq_rni = 0.0
    #             imp_iibb = sum(
    #                 inv.tax_line_ids.filtered(
    #                     lambda r: (
    #                         r.tax_id.tax_group_id.type == "perception"
    #                         and r.tax_id.tax_group_id.application == "provincial_taxes"
    #                     )
    #                 ).mapped("amount")
    #             )
    #             imp_perc_mun = sum(
    #                 inv.tax_line_ids.filtered(
    #                     lambda r: (
    #                         r.tax_id.tax_group_id.type == "perception"
    #                         and r.tax_id.tax_group_id.application == "municipal_taxes"
    #                     )
    #                 ).mapped("amount")
    #             )
    #             imp_internos = sum(
    #                 inv.tax_line_ids.filtered(
    #                     lambda r: r.tax_id.tax_group_id.application == "others"
    #                 ).mapped("amount")
    #             )
    #             imp_perc = sum(
    #                 inv.tax_line_ids.filtered(
    #                     lambda r: (
    #                         r.tax_id.tax_group_id.type == "perception"
    #                         and
    #                         # r.tax_id.tax_group_id.tax != 'vat' and
    #                         r.tax_id.tax_group_id.application == "national_taxes"
    #                     )
    #                 ).mapped("amount")
    #             )

    #             ws.CrearFactura(
    #                 tipo_doc,
    #                 nro_doc,
    #                 zona,
    #                 doc_afip_code,
    #                 pos_number,
    #                 cbte_nro,
    #                 fecha_cbte,
    #                 imp_total,
    #                 imp_neto,
    #                 imp_iva,
    #                 imp_tot_conc,
    #                 impto_liq_rni,
    #                 imp_op_ex,
    #                 imp_perc,
    #                 imp_iibb,
    #                 imp_perc_mun,
    #                 imp_internos,
    #                 moneda_id,
    #                 round(moneda_ctz, 2),
    #                 fecha_venc_pago,
    #             )

    #         if afip_ws in ["wsfe", "wsbfe"]:
    #             if mipyme_fce:
    #                 # agregamos cbu para factura de credito electronica
    #                 ws.AgregarOpcional(opcional_id=2101, valor=inv.partner_bank_id.cbu)
    #                 ws.AgregarOpcional(opcional_id=27, valor=inv.afip_mypyme_sca_adc)
    #             elif int(doc_afip_code) in [202, 203, 207, 208, 212, 213]:
    #                 valor = inv.afip_fce_es_anulacion and "S" or "N"
    #                 ws.AgregarOpcional(opcional_id=22, valor=valor)

    #         # TODO ver si en realidad tenemos que usar un vat pero no lo
    #         # subimos
    #         if afip_ws not in ["wsfex", "wsbfe"]:
    #             # for vat in inv.move_tax_ids:vat_taxable_ids:
    #             for vat in inv.move_tax_ids:
    #                 if (
    #                     vat.tax_id.tax_group_id.tax_type == "vat"
    #                     and vat.tax_id.tax_group_id.l10n_ar_vat_afip_code != "2"
    #                 ):
    #                     _logger.info("Adding VAT %s" % vat.tax_id.tax_group_id.name)
    #                     ws.AgregarIva(
    #                         vat.tax_id.tax_group_id.l10n_ar_vat_afip_code,
    #                         "%.2f" % vat.base_amount,
    #                         # "%.2f" % abs(vat.base_amount),
    #                         "%.2f" % vat.tax_amount,
    #                     )

    #             # for tax in inv.not_vat_tax_ids:
    #             #    _logger.info(
    #             #        'Adding TAX %s' % tax.tax_id.tax_group_id.name)
    #             #    ws.AgregarTributo(
    #             #        tax.tax_id.tax_group_id.application_code,
    #             #        tax.tax_id.tax_group_id.name,
    #             #        "%.2f" % tax.base,
    #             #        # "%.2f" % abs(tax.base_amount),
    #             #        # TODO pasar la alicuota
    #             #        # como no tenemos la alicuota pasamos cero, en v9
    #             #        # podremos pasar la alicuota
    #             #        0,
    #             #        "%.2f" % tax.amount,
    #             #    )

    #         if CbteAsoc:
    #             # fex no acepta fecha
    #             doc_number = CbteAsoc.document_number.split("-")[1]
    #             invoice_date = str(CbteAsoc.invoice_date).replace("-", "")
    #             if afip_ws == "wsfex":
    #                 ws.AgregarCmpAsoc(
    #                     CbteAsoc.l10n_latam_document_type_id.document_type_id.code,
    #                     CbteAsoc.journal_id.l10n_ar_afip_pos_number,
    #                     doc_number,
    #                     self.company_id.vat,
    #                 )
    #             else:
    #                 ws.AgregarCmpAsoc(
    #                     CbteAsoc.l10n_latam_document_type_id.code,
    #                     CbteAsoc.journal_id.l10n_ar_afip_pos_number,
    #                     doc_number,
    #                     self.company_id.vat,
    #                     invoice_date,
    #                 )
    #         # Notas de debito
    #         if inv.l10n_latam_document_type_id.code in ["2", "7"]:
    #             year = date.today().year
    #             month = date.today().month
    #             day = date.today().day
    #             fecha_desde = str(year) + str(month).zfill(2) + "01"
    #             fecha_hasta = str(year) + str(month).zfill(2) + str(day).zfill(2)
    #             ws.AgregarPeriodoComprobantesAsociados(fecha_desde, fecha_hasta)

    #         # analize line items - invoice detail
    #         # wsfe do not require detail
    #         if afip_ws != "wsfe":
    #             for line in inv.invoice_line_ids:
    #                 codigo = line.product_id.default_code
    #                 # unidad de referencia del producto si se comercializa
    #                 # en una unidad distinta a la de consumo
    #                 # uom is not mandatory, if no UOM we use "unit"
    #                 if not line.product_uom_id:
    #                     umed = "7"
    #                 elif not line.product_uom_id.l10n_ar_afip_code:
    #                     raise UserError(
    #                         _(
    #                             "Not afip code con producto UOM %s"
    #                             % (line.product_uom_id.name)
    #                         )
    #                     )
    #                 else:
    #                     umed = line.product_uom_id.l10n_ar_afip_code
    #                 # cod_mtx = line.uom_id.afip_code
    #                 ds = line.name
    #                 qty = line.quantity
    #                 precio = line.price_unit
    #                 importe = line.price_subtotal
    #                 # calculamos bonificacion haciendo teorico menos importe
    #                 bonif = (
    #                     line.discount and str("%.2f" % (precio * qty - importe)) or None
    #                 )
    #                 if afip_ws in ["wsmtxca", "wsbfe"]:
    #                     # TODO No lo estamos usando. Borrar?
    #                     # if not line.product_id.uom_id.afip_code:
    #                     #     raise UserError(_(
    #                     #         'Not afip code con producto UOM %s' % (
    #                     #             line.product_id.uom_id.name)))
    #                     # u_mtx = (
    #                     #     line.product_id.uom_id.afip_code or
    #                     #     line.uom_id.afip_code)
    #                     iva_id = line.vat_tax_id.tax_group_id.afip_code
    #                     vat_taxes_amounts = line.vat_tax_id.compute_all(
    #                         line.price_unit,
    #                         inv.currency_id,
    #                         line.quantity,
    #                         product=line.product_id,
    #                         partner=inv.partner_id,
    #                     )
    #                     imp_iva = sum([x["amount"] for x in vat_taxes_amounts["taxes"]])
    #                     if afip_ws == "wsmtxca":
    #                         raise UserError(_("WS wsmtxca Not implemented yet"))
    #                         # ws.AgregarItem(
    #                         #     u_mtx, cod_mtx, codigo, ds, qty, umed,
    #                         #     precio, bonif, iva_id, imp_iva,
    #                         #     importe + imp_iva)
    #                     elif afip_ws == "wsbfe":
    #                         sec = ""  # Código de la Secretaría (TODO usar)
    #                         ws.AgregarItem(
    #                             codigo,
    #                             sec,
    #                             ds,
    #                             qty,
    #                             umed,
    #                             precio,
    #                             bonif,
    #                             iva_id,
    #                             importe + imp_iva,
    #                         )
    #                 elif afip_ws == "wsfex":
    #                     ws.AgregarItem(
    #                         codigo, ds, qty, umed, precio, "%.2f" % importe, bonif
    #                     )

    #         # Request the authorization! (call the AFIP webservice method)
    #         vto = None
    #         msg = False
    #         try:
    #             if afip_ws == "wsfe":
    #                 ws.CAESolicitar()
    #                 vto = ws.Vencimiento
    #             elif afip_ws == "wsmtxca":
    #                 ws.AutorizarComprobante()
    #                 vto = ws.Vencimiento
    #             elif afip_ws == "wsfex":
    #                 ws.Authorize(inv.id)
    #                 vto = ws.FchVencCAE
    #             elif afip_ws == "wsbfe":
    #                 ws.Authorize(inv.id)
    #                 vto = ws.Vencimiento
    #         except SoapFault as fault:
    #             msg = "Falla SOAP %s: %s" % (fault.faultcode, fault.faultstring)
    #         except Exception as e:
    #             msg = e
    #         except Exception:
    #             if ws.Excepcion:
    #                 # get the exception already parsed by the helper
    #                 msg = ws.Excepcion
    #             else:
    #                 # avoid encoding problem when raising error
    #                 msg = traceback.format_exception_only(sys.exc_type, sys.exc_value)[
    #                     0
    #                 ]
    #         if msg:
    #             _logger.info(
    #                 _("AFIP Validation Error. %s" % msg)
    #                 + " XML Request: %s XML Response: %s"
    #                 % (ws.XmlRequest, ws.XmlResponse)
    #             )
    #             raise UserError(_("AFIP Validation Error. %s" % msg))

    #         msg = "\n".join([ws.Obs or "", ws.ErrMsg or ""])
    #         if not ws.CAE or ws.Resultado != "A":
    #             raise UserError(_("AFIP Validation Error. %s" % msg))
    #         # TODO ver que algunso campos no tienen sentido porque solo se
    #         # escribe aca si no hay errores
    #         _logger.info(
    #             "CAE solicitado con exito. CAE: %s. Resultado %s"
    #             % (ws.CAE, ws.Resultado)
    #         )
    #         if afip_ws == "wsbfe":
    #             vto = datetime.strftime(datetime.strptime(vto, "%d/%m/%Y"), "%Y%m%d")
    #         vto = vto[:4] + "-" + vto[4:6] + "-" + vto[6:8]
    #         inv.write(
    #             {
    #                 "afip_auth_mode": "CAE",
    #                 "afip_auth_code": ws.CAE,
    #                 "afip_auth_code_due": vto,
    #                 "afip_result": ws.Resultado,
    #                 "afip_message": msg,
    #                 "afip_xml_request": ws.XmlRequest,
    #                 "afip_xml_response": ws.XmlResponse,
    #                 "document_number": str(pos_number).zfill(5)
    #                 + "-"
    #                 + str(cbte_nro).zfill(8),
    #                 "name": inv.l10n_latam_document_type_id.doc_code_prefix
    #                 + " "
    #                 + str(pos_number).zfill(5)
    #                 + "-"
    #                 + str(cbte_nro).zfill(8),
    #             }
    #         )
    #         # si obtuvimos el cae hacemos el commit porque estoya no se puede
    #         # volver atras
    #         # otra alternativa seria escribir con otro cursor el cae y que
    #         # la factura no quede validada total si tiene cae no se vuelve a
    #         # solicitar. Lo mismo podriamos usar para grabar los mensajes de
    #         # afip de respuesta
    #         inv._cr.commit()
    #     """AI is creating summary for do_pyafipws_request_cae
    #     """
        
        
    @api.model
    def _get_tax_totals_5614(self, partner, tax_lines_data, amount_total, amount_untaxed, currency):
        """ Compute the tax totals for the provided data.

        :param partner:        The partner to compute totals for
        :param tax_lines_data: All the data about the base and tax lines as a list of dictionaries.
                               Each dictionary represents an amount that needs to be added to either a tax base or amount.
                               A tax amount looks like:
                                   {
                                       'line_key':             unique identifier,
                                       'tax_amount':           the amount computed for this tax
                                       'tax':                  the account.tax object this tax line was made from
                                   }
                               For base amounts:
                                   {
                                       'line_key':             unique identifier,
                                       'base_amount':          the amount to add to the base of the tax
                                       'tax':                  the tax basing itself on this amount
                                       'tax_affecting_base':   (optional key) the tax whose tax line is having the impact
                                                               denoted by 'base_amount' on the base of the tax, in case of taxes
                                                               affecting the base of subsequent ones.
                                   }
        :param amount_total:   Total amount, with taxes.
        :param amount_untaxed: Total amount without taxes.
        :param currency:       The currency in which the amounts are computed.

        :return: A dictionary in the following form:
            {
                'amount_total':                              The total amount to be displayed on the document, including every total types.
                'amount_untaxed':                            The untaxed amount to be displayed on the document.
                'formatted_amount_total':                    Same as amount_total, but as a string formatted accordingly with partner's locale.
                'formatted_amount_untaxed':                  Same as amount_untaxed, but as a string formatted accordingly with partner's locale.
                'allow_tax_edition':                         True if the user should have the ability to manually edit the tax amounts by group
                                                             to fix rounding errors.
                'groups_by_subtotals':                       A dictionary formed liked {'subtotal': groups_data}
                                                             Where total_type is a subtotal name defined on a tax group, or the default one: 'Untaxed Amount'.
                                                             And groups_data is a list of dict in the following form:
                                                                {
                                                                    'tax_group_name':                  The name of the tax groups this total is made for.
                                                                    'tax_group_amount':                The total tax amount in this tax group.
                                                                    'tax_group_base_amount':           The base amount for this tax group.
                                                                    'formatted_tax_group_amount':      Same as tax_group_amount, but as a string
                                                                                                       formatted accordingly with partner's locale.
                                                                    'formatted_tax_group_base_amount': Same as tax_group_base_amount, but as a string
                                                                                                       formatted accordingly with partner's locale.
                                                                    'tax_group_id':                    The id of the tax group corresponding to this dict.
                                                                    'group_key':                       A unique key identifying this total dict,
                                                                }
                'subtotals':                                 A list of dictionaries in the following form, one for each subtotal in groups_by_subtotals' keys
                                                                {
                                                                    'name':                            The name of the subtotal
                                                                    'amount':                          The total amount for this subtotal, summing all
                                                                                                       the tax groups belonging to preceding subtotals and the base amount
                                                                    'formatted_amount':                Same as amount, but as a string
                                                                                                       formatted accordingly with partner's locale.
                                                                }
            }
        """
        account_tax = self.env['account.tax']

        grouped_taxes = defaultdict(lambda: defaultdict(lambda: {'base_amount': 0.0, 'tax_amount': 0.0, 'base_line_keys': set()}))
        subtotal_priorities = {}
        for line_data in tax_lines_data:
            tax_group = line_data['tax'].tax_group_id

            # Update subtotals priorities
            if tax_group.preceding_subtotal:
                subtotal_title = tax_group.preceding_subtotal
                new_priority = tax_group.sequence
            else:
                # When needed, the default subtotal is always the most prioritary
                subtotal_title = _("Untaxed Amount")
                new_priority = 0

            if subtotal_title not in subtotal_priorities or new_priority < subtotal_priorities[subtotal_title]:
                subtotal_priorities[subtotal_title] = new_priority

            # Update tax data
            tax_group_vals = grouped_taxes[subtotal_title][tax_group]

            if 'base_amount' in line_data:
                # Base line
                if tax_group == line_data.get('tax_affecting_base', account_tax).tax_group_id:
                    # In case the base has a tax_line_id belonging to the same group as the base tax,
                    # the base for the group will be computed by the base tax's original line (the one with tax_ids and no tax_line_id)
                    continue

                if line_data['line_key'] not in tax_group_vals['base_line_keys']:
                    # If the base line hasn't been taken into account yet, at its amount to the base total.
                    tax_group_vals['base_line_keys'].add(line_data['line_key'])
                    tax_group_vals['base_amount'] += line_data['base_amount']

            else:
                # Tax line
                tax_group_vals['tax_amount'] += line_data['tax_amount']

        # Compute groups_by_subtotal
        groups_by_subtotal = {}
        for subtotal_title, groups in grouped_taxes.items():
            groups_vals = [{
                'tax_group_name': group.name,
                'tax_group_amount': amounts['tax_amount'],
                'tax_group_base_amount': amounts['base_amount'],
                'formatted_tax_group_amount': formatLang(self.env, amounts['tax_amount'], currency_obj=currency),
                'formatted_tax_group_base_amount': formatLang(self.env, amounts['base_amount'], currency_obj=currency),
                'tax_group_id': group.id,
                'group_key': '%s-%s' %(subtotal_title, group.id),
            } for group, amounts in sorted(groups.items(), key=lambda l: l[0].sequence)]

            groups_by_subtotal[subtotal_title] = groups_vals

        # Compute subtotals
        subtotals_list = [] # List, so that we preserve their order
        previous_subtotals_tax_amount = 0
        for subtotal_title in sorted((sub for sub in subtotal_priorities), key=lambda x: subtotal_priorities[x]):
            subtotal_value = amount_untaxed + previous_subtotals_tax_amount
            subtotals_list.append({
                'name': subtotal_title,
                'amount': subtotal_value,
                'formatted_amount': formatLang(self.env, subtotal_value, currency_obj=currency),
            })

            subtotal_tax_amount = sum(group_val['tax_group_amount'] for group_val in groups_by_subtotal[subtotal_title])
            previous_subtotals_tax_amount += subtotal_tax_amount

        # Assign json-formatted result to the field
        return {
            'amount_total': amount_total,
            'amount_untaxed': amount_untaxed,
            'formatted_amount_total': formatLang(self.env, amount_total, currency_obj=currency),
            'formatted_amount_untaxed': formatLang(self.env, amount_untaxed, currency_obj=currency),
            'groups_by_subtotal': groups_by_subtotal,
            'subtotals': subtotals_list,
            'allow_tax_edition': False,
        }


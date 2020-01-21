# © 2004-2010 Tiny SPRL (<http://tiny.be>)
# © Thinkopen Solutions (<http://www.thinkopensolutions.com.br>)
# © Akretion (<http://www.akretion.com>)
# © KMEE (<http://www.kmee.com.br>)
# © 2016 Danimar Ribeiro <danimaribeiro@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import re
import logging
import base64
from datetime import datetime
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

try:
    from OpenSSL import crypto
except ImportError:
    _logger.error('Cannot import OpenSSL.crypto', exc_info=True)


class ResCompany(models.Model):

    _inherit = 'res.company'

    def _get_address_data(self):
        for rec in self:
            rec.city_id = rec.partner_id.city_id
            rec.district = rec.partner_id.district
            rec.number = rec.partner_id.number

    def _get_br_data(self):
        """ Read the l10n_br specific functional fields. """
        for rec in self:
            rec.legal_name = rec.partner_id.legal_name
            rec.cnpj_cpf = rec.partner_id.cnpj_cpf
            rec.inscr_est = rec.partner_id.inscr_est
            rec.inscr_mun = rec.partner_id.inscr_mun
            rec.suframa = rec.partner_id.suframa

    def _set_br_suframa(self):
        """ Write the l10n_br specific functional fields. """
        for rec in self:
            rec.partner_id.suframa = rec.suframa

    def _set_br_legal_name(self):
        """ Write the l10n_br specific functional fields. """
        for rec in self:
            rec.partner_id.legal_name = rec.legal_name

    def _set_br_cnpj_cpf(self):
        """ Write the l10n_br specific functional fields. """
        for rec in self:
            rec.partner_id.cnpj_cpf = rec.cnpj_cpf

    def _set_br_inscr_est(self):
        """ Write the l10n_br specific functional fields. """
        for rec in self:
            rec.partner_id.inscr_est = rec.inscr_est

    def _set_br_inscr_mun(self):
        """ Write the l10n_br specific functional fields. """
        for rec in self:
            rec.partner_id.inscr_mun = rec.inscr_mun

    def _set_br_number(self):
        """ Write the l10n_br specific functional fields. """
        for rec in self:
            rec.partner_id.number = rec.number

    def _set_br_district(self):
        """ Write the l10n_br specific functional fields. """
        for rec in self:
            rec.partner_id.district = rec.district

    def _set_city_id(self):
        """ Write the l10n_br specific functional fields. """
        for rec in self:
            rec.partner_id.city_id = rec.city_id

    def _compute_expiry_date(self):
        for rec in self:
            try:
                pfx = base64.decodestring(
                    rec.with_context(bin_size=False).nfe_a1_file)
                pfx = crypto.load_pkcs12(pfx, rec.nfe_a1_password)
                cert = pfx.get_certificate()
                end = datetime.strptime(
                    cert.get_notAfter().decode(), '%Y%m%d%H%M%SZ')
                subj = cert.get_subject()
                rec.cert_expire_date = end.date()
                if datetime.now() < end:
                    rec.cert_state = 'valid'
                else:
                    rec.cert_state = 'expired'
                rec.cert_information = "%s\n%s\n%s\n%s" % (
                    subj.CN, subj.L, subj.O, subj.OU)
            except crypto.Error:
                rec.cert_state = 'invalid_password'
            except Exception as exc:
                rec.cert_state = 'unknown'
                _logger.warning(
                    _('Unknown error when validating certificate. %s', exc),
                    exc_info=True)

    cnpj_cpf = fields.Char(
        compute=_get_br_data, inverse=_set_br_cnpj_cpf, size=18,
        string=_("CNPJ"))

    inscr_est = fields.Char(
        compute=_get_br_data, inverse=_set_br_inscr_est, size=16,
        string=_("State Inscription"))

    inscr_mun = fields.Char(
        compute=_get_br_data, inverse=_set_br_inscr_mun, size=18,
        string=_("Municipal Inscription"))

    suframa = fields.Char(
        compute=_get_br_data, inverse=_set_br_suframa, size=18,
        string=_("Suframa"))

    legal_name = fields.Char(
        compute=_get_br_data, inverse=_set_br_legal_name, size=128,
        string=_("Legal Name"))

    city_id = fields.Many2one(
        compute=_get_address_data, inverse='_set_city_id',
        comodel_name='res.state.city', string=_("City"), multi='address')

    district = fields.Char(
        compute=_get_address_data, inverse='_set_br_district', size=32,
        string=_("District"), multi='address')

    number = fields.Char(
        compute=_get_address_data, inverse='_set_br_number', size=10,
        string=_("Number"), multi='address')

    nfe_a1_file = fields.Binary(_("NFe A1 File"))
    nfe_a1_password = fields.Char(_("NFe A1 Password"), size=64)

    cert_state = fields.Selection(
        [('not_loaded', _("Not loaded")),
         ('expired',  _("Expired")),
         ('invalid_password', _("Invalid Password")),
         ('unknown', _("Unknown")),
         ('valid', _("Valid"))],
        string=_("Cet. State"), compute=_compute_expiry_date,
        default='not_loaded')
    cert_information = fields.Text(
        string=_("Cert. Info"), compute=_compute_expiry_date)
    cert_expire_date = fields.Date(
        string=_("Cert. Expiration Date"), compute=_compute_expiry_date)

    @api.onchange('cnpj_cpf')
    def onchange_mask_cnpj_cpf(self):
        for rec in self:
            if rec.cnpj_cpf:
                val = re.sub('[^0-9]', '', rec.cnpj_cpf)
                if len(val) == 14:
                    cnpj_cpf = "%s.%s.%s/%s-%s"\
                        % (val[0:2], val[2:5], val[5:8], val[8:12], val[12:14])
                    rec.cnpj_cpf = cnpj_cpf

    @api.onchange('city_id')
    def onchange_city_id(self):
        """ Ao alterar o campo city_id copia o nome
        do município para o campo city que é o campo nativo do módulo base
        para manter a compatibilidade entre os demais módulos que usam o
        campo city.
        """
        for rec in self:
            if rec.city_id:
                rec.city = rec.city_id.name

    @api.onchange('zip')
    def onchange_mask_zip(self):
        for rec in self:
            if rec.zip:
                val = re.sub('[^0-9]', '', rec.zip)
                if len(val) == 8:
                    zip = "%s-%s" % (val[0:5], val[5:8])
                    rec.zip = zip

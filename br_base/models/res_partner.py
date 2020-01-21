# © 2009 Gabriel C. Stabel
# © 2009 Renato Lima (Akretion)
# © 2012 Raphaël Valyi (Akretion)
# © 2015  Michell Stuttgart (KMEE)
# © 2016 Danimar Ribeiro <danimaribeiro@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import re
import base64
import logging

from odoo import models, fields, api, _
from ..tools import fiscal
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

try:
    from pytrustnfe.nfe import consulta_cadastro
    from pytrustnfe.certificado import Certificado
except ImportError:
    _logger.error('Cannot import pytrustnfe', exc_info=True)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    cnpj_cpf = fields.Char(_("CNPJ/CPF"), size=18, copy=False)
    inscr_est = fields.Char(_("State Inscription"), size=16, copy=False)
    rg_fisica = fields.Char(_("RG"), size=16, copy=False)
    inscr_mun = fields.Char(_("Municipal Inscription"), size=18)
    suframa = fields.Char(_("Suframa"), size=18)
    legal_name = fields.Char(
        _("Legal Name"), size=60, help=_("Name used in fiscal documents"))
    city_id = fields.Many2one(
        'res.state.city', _("City"),
        domain="[('state_id','=',state_id)]")
    district = fields.Char(_("District"), size=32)
    number = fields.Char(_("Number"), size=10)

    _sql_constraints = [
        ('res_partner_cnpj_cpf_uniq', 'unique (cnpj_cpf)',
         _('This CPF/CNPJ number is already being used by another partner!'))
    ]

    def _display_address(self, without_company=False):
        address = self

        if address.country_id and address.country_id.code != 'BR':
            # this ensure other localizations could do what they want
            return super(ResPartner, self)._display_address(
                without_company=False)
        else:
            address_format = (
                address.country_id and address.country_id.address_format or
                "%(street)s\n%(street2)s\n%(city)s %(state_code)s"
                "%(zip)s\n%(country_name)s")
            args = {
                'state_code': address.state_id and address.state_id.code or '',
                'state_name': address.state_id and address.state_id.name or '',
                'country_code': address.country_id and
                address.country_id.code or '',
                'country_name': address.country_id and
                address.country_id.name or '',
                'company_name': address.parent_id and
                address.parent_id.name or '',
                'city_name': address.city_id and
                address.city_id.name or '',
            }
            address_field = ['title', 'street', 'street2', 'zip', 'city',
                             'number', 'district']
            for field in address_field:
                args[field] = getattr(address, field) or ''
            if without_company:
                args['company_name'] = ''
            elif address.parent_id:
                address_format = '%(company_name)s\n' + address_format
            return address_format % args

    @api.constrains('cnpj_cpf', 'country_id', 'is_company')
    def _check_cnpj_cpf(self):
        for item in self:
            country_code = item.country_id.code or ''
            if item.cnpj_cpf and country_code.upper() == 'BR':
                if item.is_company:
                    if not fiscal.validate_cnpj(item.cnpj_cpf):
                        raise ValidationError(_('Invalid CNPJ Number!'))
                elif not fiscal.validate_cpf(item.cnpj_cpf):
                    raise ValidationError(_('Invalid CPF Number!'))
        return True

    def _validate_ie_param(self, uf, inscr_est):
        try:
            mod = __import__(
                'odoo.addons.br_base.tools.fiscal', globals(),
                locals(), 'fiscal')

            validate = getattr(mod, 'validate_ie_%s' % uf)
            if not validate(inscr_est):
                return False
        except AttributeError:
            if not fiscal.validate_ie_param(uf, inscr_est):
                return False
        return True

    @api.constrains('inscr_est', 'state_id', 'is_company')
    def _check_ie(self):
        """Checks if company register number in field insc_est is valid,
        this method call others methods because this validation is State wise
        :Return: True or False."""
        for partner in self:
            if not partner.inscr_est or partner.inscr_est == 'ISENTO' \
                    or not partner.is_company:
                return True
            uf = partner.state_id and partner.state_id.code.lower() or ''
            res = partner._validate_ie_param(uf, partner.inscr_est)
            if not res:
                raise ValidationError(_('Invalid State Inscription!'))
        return True

    @api.constrains('inscr_est')
    def _check_ie_duplicated(self):
        """ Check if the field inscr_est has duplicated value
        """
        if not self.inscr_est or self.inscr_est == 'ISENTO':
            return True
        partner_ids = self.search(
            ['&', ('inscr_est', '=', self.inscr_est), ('id', '!=', self.id)])

        if len(partner_ids) > 0:
            raise ValidationError(
                _('This State Inscription/RG number \
                  is already being used by another partner!'))
        return True

    @api.onchange('cnpj_cpf')
    def _onchange_cnpj_cpf(self):
        for rec in self:
            country_code = rec.country_id.code or ''
            if rec.cnpj_cpf and country_code.upper() == 'BR':
                val = re.sub('[^0-9]', '', rec.cnpj_cpf)
                if len(val) == 14:
                    cnpj_cpf = "%s.%s.%s/%s-%s"\
                        % (val[0:2], val[2:5], val[5:8], val[8:12], val[12:14])
                    rec.cnpj_cpf = cnpj_cpf
                elif not rec.is_company and len(val) == 11:
                    cnpj_cpf = "%s.%s.%s-%s"\
                        % (val[0:3], val[3:6], val[6:9], val[9:11])
                    rec.cnpj_cpf = cnpj_cpf
                else:
                    raise UserError(_('Verify CNPJ/CPF number'))

    @api.onchange('city_id')
    def _onchange_city_id(self):
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

    @api.model
    def _address_fields(self):
        """ Returns the list of address fields that are synced from the parent
        when the `use_parent_address` flag is set.
        Extenção para os novos campos do endereço """
        address_fields = super(ResPartner, self)._address_fields()
        return list(address_fields + ['city_id', 'number', 'district'])

    def action_check_sefaz(self):
        for rec in self:
            if rec.cnpj_cpf and rec.state_id:
                if rec.state_id.code == 'AL':
                    raise UserError(_('Alagoas doesn\'t have this service'))
                if rec.state_id.code == 'RJ':
                    raise UserError(_(
                        'Rio de Janeiro doesn\'t have this service'))
                company = rec.env.user.company_id
                if not company.nfe_a1_file and not company.nfe_a1_password:
                    raise UserError(_(
                        'Configure the company\'s certificate and password'))
                cert = company.with_context({'bin_size': False}).nfe_a1_file
                cert_pfx = base64.decodestring(cert)
                certificado = Certificado(cert_pfx, company.nfe_a1_password)
                cnpj = re.sub('[^0-9]', '', rec.cnpj_cpf)
                obj = {'cnpj': cnpj, 'estado': rec.state_id.code}
                resposta = consulta_cadastro(
                    certificado, obj=obj, ambiente=1,
                    estado=rec.state_id.ibge_code)

                info = resposta['object'].getchildren()[0]
                info = info.infCons
                if info.cStat == 111 or info.cStat == 112:
                    if not rec.inscr_est:
                        rec.inscr_est = info.infCad.IE.text
                    if not rec.cnpj_cpf:
                        rec.cnpj_cpf = info.infCad.CNPJ.text

                    def get_value(obj, prop):
                        if prop not in dir(obj):
                            return None
                        return getattr(obj, prop)
                    rec.legal_name = get_value(info.infCad, 'xNome')
                    if "ender" not in dir(info.infCad):
                        return
                    cep = get_value(info.infCad.ender, 'CEP') or ''
                    rec.zip = str(cep).zfill(8) if cep else ''
                    rec.street = get_value(info.infCad.ender, 'xLgr')
                    rec.number = get_value(info.infCad.ender, 'nro')
                    rec.street2 = get_value(info.infCad.ender, 'xCpl')
                    rec.district = get_value(info.infCad.ender, 'xBairro')
                    cMun = get_value(info.infCad.ender, 'cMun')
                    xMun = get_value(info.infCad.ender, 'xMun')
                    city = None
                    if cMun:
                        city = rec.env['res.state.city'].search(
                            [('ibge_code', '=', str(cMun)[2:]),
                             ('state_id', '=', rec.state_id.id)])
                    if not city and xMun:
                        city = rec.env['res.state.city'].search(
                            [('name', 'ilike', xMun),
                             ('state_id', '=', rec.state_id.id)])
                    if city:
                        rec.city_id = city.id
                else:
                    msg = "%s - %s" % (info.cStat, info.xMotivo)
                    raise UserError(msg)
            else:
                raise UserError(_('Fill the State and CNPJ fields to search'))

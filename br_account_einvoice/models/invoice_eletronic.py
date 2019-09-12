# © 2016 Danimar Ribeiro <danimaribeiro@gmail.com>, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
import base64
import copy
import logging
from datetime import datetime, timedelta
import dateutil.relativedelta as relativedelta
from odoo.exceptions import UserError
from odoo import api, fields, models, tools, _
from odoo.addons.br_account.models.cst import CST_ICMS
from odoo.addons.br_account.models.cst import CSOSN_SIMPLES
from odoo.addons.br_account.models.cst import CST_IPI
from odoo.addons.br_account.models.cst import CST_PIS_COFINS
from odoo.addons.br_account.models.cst import ORIGEM_PROD
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

_logger = logging.getLogger(__name__)

STATE = {'edit': [('readonly', False)]}


# format_amount function for fiscal observation
# This way we can format numbers in currency template on fiscal observation msg
# We'll call this function when setting the variables env below
def format_amount(env, amount, currency):
    fmt = "%.{0}f".format(currency.decimal_places)
    lang = env['res.lang']._lang_get(env.context.get('lang') or 'en_US')

    formatted_amount = lang.format(
        fmt, currency.round(amount), grouping=True, monetary=True).replace(
            r' ', '\N{NO-BREAK SPACE}').replace(
                r'-', '-\N{ZERO WIDTH NO-BREAK SPACE}')

    pre = post = ''
    if currency.position == 'before':
        pre = '{symbol}\N{NO-BREAK SPACE}'.format(
            symbol=currency.symbol or '')
    else:
        post = '\N{NO-BREAK SPACE}{symbol}'.format(
            symbol=currency.symbol or '')

    return '{pre}{0}{post}'.format(formatted_amount, pre=pre, post=post)


class InvoiceEletronic(models.Model):
    _name = 'invoice.eletronic'
    _description = "Nota Fiscal"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    code = fields.Char(
        'Código', size=100, required=True, readonly=True, states=STATE)
    name = fields.Char(
        'Nome', size=100, required=True, readonly=True, states=STATE)
    company_id = fields.Many2one(
        'res.company', 'Empresa', readonly=True, states=STATE)
    state = fields.Selection(
        [('draft', 'Provisório'),
         ('edit', 'Editar'),
         ('error', 'Erro'),
         ('done', 'Enviado'),
         ('cancel', 'Cancelado')],
        string='State', default='draft', readonly=True, states=STATE,
        track_visibility='always')
    schedule_user_id = fields.Many2one(
        'res.users', string="Agendado por", readonly=True,
        track_visibility='always')
    tipo_operacao = fields.Selection(
        [('entrada', 'Entrada'),
         ('saida', 'Saída')],
        string='Tipo de Operação', readonly=True, states=STATE)
    model = fields.Selection(
        [('55', '55 - NFe'),
         ('65', '65 - NFCe'),
         ('001', 'NFS-e - Nota Fiscal Paulistana'),
         ('002', 'NFS-e - Provedor GINFES'),
         ('008', 'NFS-e - Provedor SIMPLISS'),
         ('009', 'NFS-e - Provedor SUSESU'),
         ('010', 'NFS-e Imperial - Petrópolis'),
         ('012', 'NFS-e - Florianópolis')],
        string='Modelo', readonly=True, states=STATE)
    serie = fields.Many2one(
        'br_account.document.serie', string='Série',
        readonly=True, states=STATE)
    serie_documento = fields.Char(string='Série Documento', size=6)
    numero = fields.Integer(
        string='Número', readonly=True, states=STATE)
    numero_controle = fields.Integer(
        string='Número de Controle', readonly=True, states=STATE)
    data_agendada = fields.Date(
        string='Data agendada',
        readonly=True,
        default=fields.Date.today,
        states=STATE)
    data_emissao = fields.Datetime(
        string='Data emissão', readonly=True, states=STATE)
    data_autorizacao = fields.Char(
        string='Data de autorização', size=30, readonly=True, states=STATE)
    ambiente = fields.Selection(
        [('homologacao', 'Homologação'),
         ('producao', 'Produção')],
        string='Ambiente', readonly=True, states=STATE)
    finalidade_emissao = fields.Selection(
        [('1', '1 - Normal'),
         ('2', '2 - Complementar'),
         ('3', '3 - Ajuste'),
         ('4', '4 - Devolução')],
        string='Finalidade', help="Finalidade da emissão de NFe",
        readonly=True, states=STATE)
    invoice_id = fields.Many2one(
        'account.invoice', string='Fatura', readonly=True, states=STATE)
    partner_id = fields.Many2one(
        'res.partner', string='Parceiro', readonly=True, states=STATE)
    commercial_partner_id = fields.Many2one(
        'res.partner', string='Commercial Entity',
        related='partner_id.commercial_partner_id', store=True)
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Entrega', readonly=True, states=STATE)
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Condição pagamento',
        readonly=True, states=STATE)
    fiscal_position_id = fields.Many2one(
        'account.fiscal.position', string='Posição Fiscal',
        readonly=True, states=STATE)
    eletronic_item_ids = fields.One2many(
        'invoice.eletronic.item', 'invoice_eletronic_id', string="Linhas",
        readonly=True, states=STATE)
    eletronic_event_ids = fields.One2many(
        'invoice.eletronic.event', 'invoice_eletronic_id', string="Eventos",
        readonly=True, states=STATE)
    valor_bruto = fields.Monetary(
        string='Total Produtos', readonly=True, states=STATE)
    valor_frete = fields.Monetary(
        string='Total Frete', readonly=True, states=STATE)
    valor_seguro = fields.Monetary(
        string='Total Seguro', readonly=True, states=STATE)
    valor_desconto = fields.Monetary(
        string='Total Desconto', readonly=True, states=STATE)
    valor_despesas = fields.Monetary(
        string='Total Despesas', readonly=True, states=STATE)
    valor_bc_icms = fields.Monetary(
        string="Base de Cálculo ICMS", readonly=True, states=STATE)
    valor_icms = fields.Monetary(
        string="Total do ICMS", readonly=True, states=STATE)
    valor_icms_deson = fields.Monetary(
        string='ICMS Desoneração', readonly=True, states=STATE)
    valor_bc_icmsst = fields.Monetary(
        string='Total Base ST', help="Total da base de cálculo do ICMS ST",
        readonly=True, states=STATE)
    valor_icmsst = fields.Monetary(
        string='Total ST', readonly=True, states=STATE)
    valor_ii = fields.Monetary(
        string='Total II', readonly=True, states=STATE)
    valor_ipi = fields.Monetary(
        string="Total IPI", readonly=True, states=STATE)
    valor_pis = fields.Monetary(
        string="Total PIS", readonly=True, states=STATE)
    valor_cofins = fields.Monetary(
        string="Total COFINS", readonly=True, states=STATE)
    valor_estimado_tributos = fields.Monetary(
        string="Tributos Estimados", readonly=True, states=STATE)

    valor_servicos = fields.Monetary(
        string="Total Serviços", readonly=True, states=STATE)
    valor_bc_issqn = fields.Monetary(
        string="Base ISS", readonly=True, states=STATE)
    valor_issqn = fields.Monetary(
        string="Total ISS", readonly=True, states=STATE)
    valor_pis_servicos = fields.Monetary(
        string="Total PIS Serviços", readonly=True, states=STATE)
    valor_cofins_servicos = fields.Monetary(
        string="Total Cofins Serviço", readonly=True, states=STATE)

    valor_retencao_issqn = fields.Monetary(
        string="Retenção ISSQN", readonly=True, states=STATE)
    valor_retencao_pis = fields.Monetary(
        string="Retenção PIS", readonly=True, states=STATE)
    valor_retencao_cofins = fields.Monetary(
        string="Retenção COFINS", readonly=True, states=STATE)
    valor_bc_irrf = fields.Monetary(
        string="Base de Cálculo IRRF", readonly=True, states=STATE)
    valor_retencao_irrf = fields.Monetary(
        string="Retenção IRRF", readonly=True, states=STATE)
    valor_bc_csll = fields.Monetary(
        string="Base de Cálculo CSLL", readonly=True, states=STATE)
    valor_retencao_csll = fields.Monetary(
        string="Retenção CSLL", readonly=True, states=STATE)
    valor_bc_inss = fields.Monetary(
        string="Base de Cálculo INSS", readonly=True, states=STATE)
    valor_retencao_inss = fields.Monetary(
        string="Retenção INSS", help="Retenção Previdência Social",
        readonly=True, states=STATE)

    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id',
        string="Company Currency")
    valor_final = fields.Monetary(
        string='Valor Final', readonly=True, states=STATE)

    informacoes_legais = fields.Text(
        string='Informações legais', readonly=True, states=STATE)
    informacoes_complementares = fields.Text(
        string='Informações complementares', readonly=True, states=STATE)

    codigo_retorno = fields.Char(
        string='Código Retorno', readonly=True, states=STATE,
        track_visibility='onchange')
    mensagem_retorno = fields.Char(
        string='Mensagem Retorno', readonly=True, states=STATE,
        track_visibility='onchange')
    numero_nfe = fields.Char(
        string="Numero Formatado NFe", readonly=True, states=STATE)

    xml_to_send = fields.Binary(string="Xml a Enviar", readonly=True)
    xml_to_send_name = fields.Char(
        string="Nome xml a ser enviado", size=100, readonly=True)

    email_sent = fields.Boolean(string="Email enviado", default=False,
                                readonly=True, states=STATE)

    def _create_attachment(self, prefix, event, data):
        file_name = '%s-%s.xml' % (
            prefix, datetime.now().strftime('%Y-%m-%d-%H-%M'))
        self.env['ir.attachment'].create(
            {
                'name': file_name,
                'datas': base64.b64encode(data.encode()),
                'datas_fname': file_name,
                'description': '',
                'res_model': 'invoice.eletronic',
                'res_id': event.id
            })

    def _hook_validation(self):
        """
            Override this method to implement the validations specific
            for the city you need
            @returns list<string> errors
        """
        errors = []
        # Emitente
        if not self.company_id.nfe_a1_file:
            errors.append('Emitente - Certificado Digital')
        if not self.company_id.nfe_a1_password:
            errors.append('Emitente - Senha do Certificado Digital')
        if not self.company_id.partner_id.legal_name:
            errors.append('Emitente - Razão Social')
        if not self.company_id.partner_id.cnpj_cpf:
            errors.append('Emitente - CNPJ/CPF')
        if not self.company_id.partner_id.street:
            errors.append('Emitente / Endereço - Logradouro')
        if not self.company_id.partner_id.number:
            errors.append('Emitente / Endereço - Número')
        if not self.company_id.partner_id.zip or len(
                re.sub(r"\D", "", self.company_id.partner_id.zip)) != 8:
            errors.append('Emitente / Endereço - CEP')
        if not self.company_id.partner_id.state_id:
            errors.append('Emitente / Endereço - Estado')
        else:
            if not self.company_id.partner_id.state_id.ibge_code:
                errors.append('Emitente / Endereço - Cód. do IBGE do estado')
            if not self.company_id.partner_id.state_id.name:
                errors.append('Emitente / Endereço - Nome do estado')

        if not self.company_id.partner_id.city_id:
            errors.append('Emitente / Endereço - município')
        else:
            if not self.company_id.partner_id.city_id.name:
                errors.append('Emitente / Endereço - Nome do município')
            if not self.company_id.partner_id.city_id.ibge_code:
                errors.append('Emitente/Endereço - Cód. do IBGE do município')

        if not self.company_id.partner_id.country_id:
            errors.append('Emitente / Endereço - país')
        else:
            if not self.company_id.partner_id.country_id.name:
                errors.append('Emitente / Endereço - Nome do país')
            if not self.company_id.partner_id.country_id.bc_code:
                errors.append('Emitente / Endereço - Código do BC do país')

        # produtos
        for eletr in self.eletronic_item_ids:
            if eletr.product_id:
                if not eletr.product_id.default_code:
                    errors.append(
                        'Prod: %s - Código do produto' % (
                            eletr.product_id.name))

        partner = self.partner_id.commercial_partner_id
        if not partner:  # NFC-e pode não ter partner, mas se tiver valida
            return errors
        company = self.company_id
        # Destinatário
        if partner.is_company and not partner.legal_name:
            errors.append('Destinatário - Razão Social')

        if partner.country_id.id == company.partner_id.country_id.id:
            if not partner.cnpj_cpf:
                errors.append('Destinatário - CNPJ/CPF')

        if not partner.street:
            errors.append('Destinatário / Endereço - Logradouro')

        if not partner.number:
            errors.append('Destinatário / Endereço - Número')

        if partner.country_id.id == company.partner_id.country_id.id:
            if not partner.zip or len(
                    re.sub(r"\D", "", partner.zip)) != 8:
                errors.append('Destinatário / Endereço - CEP')

        if partner.country_id.id == company.partner_id.country_id.id:
            if not partner.state_id:
                errors.append('Destinatário / Endereço - Estado')
            else:
                if not partner.state_id.ibge_code:
                    errors.append('Destinatário / Endereço - Código do IBGE \
                                  do estado')
                if not partner.state_id.name:
                    errors.append('Destinatário / Endereço - Nome do estado')

        if partner.country_id.id == company.partner_id.country_id.id:
            if not partner.city_id:
                errors.append('Destinatário / Endereço - Município')
            else:
                if not partner.city_id.name:
                    errors.append('Destinatário / Endereço - Nome do \
                                  município')
                if not partner.city_id.ibge_code:
                    errors.append('Destinatário / Endereço - Código do IBGE \
                                  do município')

        if not partner.country_id:
            errors.append('Destinatário / Endereço - País')
        else:
            if not partner.country_id.name:
                errors.append('Destinatário / Endereço - Nome do país')
            if not partner.country_id.bc_code:
                errors.append('Destinatário / Endereço - Cód. do BC do país')
        return errors

    def _compute_legal_information(self):
        fiscal_ids = self.invoice_id.fiscal_observation_ids.filtered(
            lambda x: x.tipo == 'fiscal')
        obs_ids = self.invoice_id.fiscal_observation_ids.filtered(
            lambda x: x.tipo == 'observacao')

        prod_obs_ids = self.env['br_account.fiscal.observation'].browse()
        for item in self.invoice_id.invoice_line_ids:
            prod_obs_ids |= item.product_id.fiscal_observation_ids

        fiscal_ids |= prod_obs_ids.filtered(lambda x: x.tipo == 'fiscal')
        obs_ids |= prod_obs_ids.filtered(lambda x: x.tipo == 'observacao')

        fiscal = self._compute_msg(fiscal_ids) + (
            self.invoice_id.fiscal_comment or '')
        observacao = self._compute_msg(obs_ids) + (
            self.invoice_id.comment or '')

        self.informacoes_legais = fiscal
        self.informacoes_complementares = observacao

    def _compute_msg(self, observation_ids):
        from jinja2.sandbox import SandboxedEnvironment
        mako_template_env = SandboxedEnvironment(
            block_start_string="<%",
            block_end_string="%>",
            variable_start_string="${",
            variable_end_string="}",
            comment_start_string="<%doc>",
            comment_end_string="</%doc>",
            line_statement_prefix="%",
            line_comment_prefix="##",
            trim_blocks=True,               # do not output newline after
            autoescape=True,                # XML/HTML automatic escaping
        )
        mako_template_env.globals.update({
            'str': str,
            'datetime': datetime,
            'len': len,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'filter': filter,
            'map': map,
            'round': round,
            # dateutil.relativedelta is an old-style class and cannot be
            # instanciated wihtin a jinja2 expression, so a lambda "proxy" is
            # is needed, apparently.
            'relativedelta': lambda *a, **kw: relativedelta.relativedelta(
                *a, **kw),
            # adding format amount
            # now we can format values like currency on fiscal observation
            'format_amount': lambda amount, currency,
            context=self._context: format_amount(self.env, amount, currency),
        })
        mako_safe_env = copy.copy(mako_template_env)
        mako_safe_env.autoescape = False

        result = ''
        for item in observation_ids:
            if item.document_id and item.document_id.code != self.model:
                continue
            template = mako_safe_env.from_string(tools.ustr(item.message))
            variables = self._get_variables_msg()
            render_result = template.render(variables)
            result += render_result + '\n'
        return result

    def _get_variables_msg(self):
        return {
            'user': self.env.user,
            'ctx': self._context,
            'invoice': self.invoice_id
            }

    def validate_invoice(self):
        self.ensure_one()
        errors = self._hook_validation()
        if len(errors) > 0:
            msg = "\n".join(
                ["Por favor corrija os erros antes de prosseguir"] + errors)
            self.sudo().unlink()
            raise UserError(msg)

    def action_post_validate(self):
        self._compute_legal_information()

    def _prepare_eletronic_invoice_item(self, item, invoice):
        return {}

    def _prepare_eletronic_invoice_values(self):
        return {}

    def action_send_eletronic_invoice(self):
        pass

    def action_cancel_document(self, context=None, justificativa=None):
        pass

    def action_back_to_draft(self):
        self.action_post_validate()
        self.state = 'draft'

    def action_edit_edoc(self):
        self.state = 'edit'

    def can_unlink(self):
        if self.state not in ('done', 'cancel'):
            return True
        return False

    def unlink(self):
        for item in self:
            if not item.can_unlink():
                raise UserError(
                    _('Documento Eletrônico enviado - Proibido excluir'))
        super(InvoiceEletronic, self).unlink()

    def log_exception(self, exc):
        self.codigo_retorno = -1
        self.mensagem_retorno = str(exc)

    def notify_user(self):
        msg = _('Verifique a %s, ocorreu um problema com o envio de \
                documento eletrônico!') % self.name
        self.create_uid.notify_warning(
            msg, sticky=True, title="Ação necessária!")
        try:
            activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        except ValueError:
            activity_type_id = False
        self.env['mail.activity'].create({
            'activity_type_id': activity_type_id,
            'note': _('Please verify the eletronic document'),
            'user_id': self.schedule_user_id.id,
            'res_id': self.id,
            'res_model_id': self.env.ref(
                'br_account_einvoice.model_invoice_eletronic').id,
        })

    def _get_state_to_send(self):
        return ('draft',)

    def cron_send_nfe(self, limit=50):
        inv_obj = self.env['invoice.eletronic'].with_context({
            'lang': self.env.user.lang, 'tz': self.env.user.tz})
        states = self._get_state_to_send()
        nfes = inv_obj.search([('state', 'in', states),
                               ('data_agendada', '<=', fields.Date.today())],
                              limit=limit)
        for item in nfes:
            try:
                _logger.info('Sending edoc id: %s (number: %s) by cron' % (
                    item.id, item.numero))
                item.action_send_eletronic_invoice()
                self.env.cr.commit()
            except Exception as e:
                item.log_exception(e)
                item.notify_user()
                _logger.error(
                    'Erro no envio de documento eletrônico', exc_info=True)

    def _find_attachment_ids_email(self):
        return []

    def send_email_nfe(self):
        mail = self.env.user.company_id.nfe_email_template
        if not mail:
            raise UserError(_('Modelo de email padrão não configurado'))
        atts = self._find_attachment_ids_email()
        _logger.info('Sending e-mail for e-doc %s (number: %s)' % (
            self.id, self.numero))

        values = mail.generate_email([self.invoice_id.id])[self.invoice_id.id]
        subject = values.pop('subject')
        values.pop('body')
        values.pop('attachment_ids')
        self.invoice_id.message_post(
            body=values['body_html'], subject=subject,
            message_type='email', subtype='mt_comment',
            attachment_ids=atts + mail.attachment_ids.ids, **values)

    def send_email_nfe_queue(self):
        after = datetime.now() + timedelta(days=-1)
        nfe_queue = self.env['invoice.eletronic'].search(
            [('data_emissao', '>=', after.strftime(DATETIME_FORMAT)),
             ('email_sent', '=', False),
             ('state', '=', 'done')], limit=5)
        for nfe in nfe_queue:
            nfe.send_email_nfe()
            nfe.email_sent = True

    def copy(self, default=None):
        raise UserError(_('Não é possível duplicar uma Nota Fiscal.'))


class InvoiceEletronicEvent(models.Model):
    _name = 'invoice.eletronic.event'
    _description = "Eventos de nota fiscal eletrônica"
    _order = 'id desc'

    code = fields.Char(string='Código', readonly=True, states=STATE)
    name = fields.Char(string='Mensagem', readonly=True, states=STATE)
    invoice_eletronic_id = fields.Many2one(
        'invoice.eletronic', string="Fatura Eletrônica",
        readonly=True, states=STATE)
    state = fields.Selection(
        related='invoice_eletronic_id.state', string="State")


class InvoiceEletronicItem(models.Model):
    _name = 'invoice.eletronic.item'
    _description = "Item da nota fiscal eletrônica"

    name = fields.Text('Nome', readonly=True, states=STATE)
    company_id = fields.Many2one(
        'res.company', 'Empresa', index=True, readonly=True, states=STATE)
    invoice_eletronic_id = fields.Many2one(
        'invoice.eletronic', string='Documento', readonly=True, states=STATE)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id',
        string="Company Currency")
    state = fields.Selection(
        related='invoice_eletronic_id.state', string="State")

    product_id = fields.Many2one(
        'product.product', string='Produto', readonly=True, states=STATE)
    tipo_produto = fields.Selection(
        [('product', 'Produto'),
         ('service', 'Serviço')],
        string="Tipo Produto", readonly=True, states=STATE)
    cfop = fields.Char('CFOP', size=5, readonly=True, states=STATE)
    ncm = fields.Char('NCM', size=10, readonly=True, states=STATE)

    uom_id = fields.Many2one(
        'uom.uom', string='Unidade Medida', readonly=True, states=STATE)
    quantidade = fields.Float(
        string='Quantidade', readonly=True, states=STATE,
        digits=('Product Unit of Measure'))
    preco_unitario = fields.Monetary(
        string='Preço Unitário', digits=('Product Price'),
        readonly=True, states=STATE)

    pedido_compra = fields.Char(
        string="Pedido Compra", size=60,
        help="Se setado aqui sobrescreve o pedido de compra da fatura")
    item_pedido_compra = fields.Char(
        string="Item de compra", size=20,
<<<<<<< HEAD
        help='Item do pedido de compra do cliente')
=======
        help=u'Item do pedido de compra do cliente')
>>>>>>> 481dd379... [FIX] Correção dos campos de pedido de compra e item da compra

    frete = fields.Monetary(
        string='Frete', digits=('Account'),
        readonly=True, states=STATE)
    seguro = fields.Monetary(
        string='Seguro', digits=('Account'),
        readonly=True, states=STATE)
    desconto = fields.Monetary(
        string='Desconto', digits=('Account'),
        readonly=True, states=STATE)
    outras_despesas = fields.Monetary(
        string='Outras despesas', digits=('Account'),
        readonly=True, states=STATE)

    tributos_estimados = fields.Monetary(
        string='Valor Estimado Tributos', digits=('Account'),
        readonly=True, states=STATE)

    valor_bruto = fields.Monetary(
        string='Valor Bruto', digits=('Account'),
        readonly=True, states=STATE)
    valor_liquido = fields.Monetary(
        string='Valor Líquido', digits=('Account'),
        readonly=True, states=STATE)
    indicador_total = fields.Selection(
        [('0', '0 - Não'), ('1', '1 - Sim')],
        string="Compõe Total da Nota?", default='1',
        readonly=True, states=STATE)

    origem = fields.Selection(
        ORIGEM_PROD, string='Origem Mercadoria', readonly=True, states=STATE)
    icms_cst = fields.Selection(
        CST_ICMS + CSOSN_SIMPLES, string='Situação Tributária',
        readonly=True, states=STATE)
    icms_aliquota = fields.Float(
        string='Alíquota', digits=('Account'),
        readonly=True, states=STATE)
    icms_tipo_base = fields.Selection(
        [('0', '0 - Margem Valor Agregado (%)'),
         ('1', '1 - Pauta (Valor)'),
         ('2', '2 - Preço Tabelado Máx. (valor)'),
         ('3', '3 - Valor da operação')],
        string='Modalidade BC do ICMS', readonly=True, states=STATE)
    icms_base_calculo = fields.Monetary(
        string='Base de cálculo', digits=('Account'),
        readonly=True, states=STATE)
    icms_aliquota_reducao_base = fields.Float(
        string='% Redução Base', digits=('Account'),
        readonly=True, states=STATE)
    icms_valor = fields.Monetary(
        string='Valor Total', digits=('Account'),
        readonly=True, states=STATE)
    icms_valor_credito = fields.Monetary(
        string="Valor de Cŕedito", digits=('Account'),
        readonly=True, states=STATE)
    icms_aliquota_credito = fields.Float(
        string='% de Crédito', digits=('Account'),
        readonly=True, states=STATE)

    icms_st_tipo_base = fields.Selection(
        [('0', '0- Preço tabelado ou máximo  sugerido'),
         ('1', '1 - Lista Negativa (valor)'),
         ('2', '2 - Lista Positiva (valor)'),
         ('3', '3 - Lista Neutra (valor)'),
         ('4', '4 - Margem Valor Agregado (%)'), ('5', '5 - Pauta (valor)')],
        string='Tipo Base ICMS ST', required=True, default='4',
        readonly=True, states=STATE)
    icms_st_aliquota_mva = fields.Float(
        string='% MVA', digits=('Account'),
        readonly=True, states=STATE)
    icms_st_aliquota = fields.Float(
        string='Alíquota', digits=('Account'),
        readonly=True, states=STATE)
    icms_st_base_calculo = fields.Monetary(
        string='Base de cálculo', digits=('Account'),
        readonly=True, states=STATE)
    icms_st_aliquota_reducao_base = fields.Float(
        string='% Redução Base', digits=('Account'),
        readonly=True, states=STATE)
    icms_st_valor = fields.Monetary(
        string='Valor Total', digits=('Account'),
        readonly=True, states=STATE)

    icms_aliquota_diferimento = fields.Float(
        string='% Diferimento', digits=('Account'),
        readonly=True, states=STATE)
    icms_valor_diferido = fields.Monetary(
        string='Valor Diferido', digits=('Account'),
        readonly=True, states=STATE)

    icms_motivo_desoneracao = fields.Char(
        string='Motivo Desoneração', size=2, readonly=True, states=STATE)
    icms_valor_desonerado = fields.Monetary(
        string='Valor Desonerado', digits=('Account'),
        readonly=True, states=STATE)

    # ----------- IPI -------------------
    ipi_cst = fields.Selection(CST_IPI, string='Situação tributária')
    ipi_aliquota = fields.Float(
        string='Alíquota', digits=('Account'),
        readonly=True, states=STATE)
    ipi_base_calculo = fields.Monetary(
        string='Base de cálculo', digits=('Account'),
        readonly=True, states=STATE)
    ipi_reducao_bc = fields.Float(
        string='% Redução Base', digits=('Account'),
        readonly=True, states=STATE)
    ipi_valor = fields.Monetary(
        string='Valor Total', digits=('Account'),
        readonly=True, states=STATE)

    # ----------- II ----------------------
    ii_base_calculo = fields.Monetary(
        string='Base de Cálculo', digits=('Account'),
        readonly=True, states=STATE)
    ii_aliquota = fields.Float(
        string='Alíquota II', digits=('Account'),
        readonly=True, states=STATE)
    ii_valor_despesas = fields.Monetary(
        string='Despesas Aduaneiras', digits=('Account'),
        readonly=True, states=STATE)
    ii_valor = fields.Monetary(
        string='Imposto de Importação', digits=('Account'),
        readonly=True, states=STATE)
    ii_valor_iof = fields.Monetary(
        string='IOF', digits=('Account'),
        readonly=True, states=STATE)

    # ------------ PIS ---------------------
    pis_cst = fields.Selection(
        CST_PIS_COFINS, string='Situação Tributária',
        readonly=True, states=STATE)
    pis_aliquota = fields.Float(
        string='Alíquota', digits=('Account'),
        readonly=True, states=STATE)
    pis_base_calculo = fields.Monetary(
        string='Base de Cálculo', digits=('Account'),
        readonly=True, states=STATE)
    pis_valor = fields.Monetary(
        string='Valor Total', digits=('Account'),
        readonly=True, states=STATE)
    pis_valor_retencao = fields.Monetary(
        string='Valor Retido', digits=('Account'),
        readonly=True, states=STATE)

    # ------------ COFINS ------------
    cofins_cst = fields.Selection(
        CST_PIS_COFINS, string='Situação Tributária',
        readonly=True, states=STATE)
    cofins_aliquota = fields.Float(
        string='Alíquota', digits=('Account'),
        readonly=True, states=STATE)
    cofins_base_calculo = fields.Monetary(
        string='Base de Cálculo', digits=('Account'),
        readonly=True, states=STATE)
    cofins_valor = fields.Monetary(
        string='Valor Total', digits=('Account'),
        readonly=True, states=STATE)
    cofins_valor_retencao = fields.Monetary(
        string='Valor Retido', digits=('Account'),
        readonly=True, states=STATE)

    # ----------- ISSQN -------------
    issqn_codigo = fields.Char(
        string='Código', size=10, readonly=True, states=STATE)
    issqn_aliquota = fields.Float(
        string='Alíquota', digits=('Account'),
        readonly=True, states=STATE)
    issqn_base_calculo = fields.Monetary(
        string='Base de Cálculo', digits=('Account'),
        readonly=True, states=STATE)
    issqn_valor = fields.Monetary(
        string='Valor Total', digits=('Account'),
        readonly=True, states=STATE)
    issqn_valor_retencao = fields.Monetary(
        string='Valor Retenção', digits=('Account'),
        readonly=True, states=STATE)

    # ------------ RETENÇÔES ------------
    csll_base_calculo = fields.Monetary(
        string='Base de Cálculo', digits=('Account'),
        readonly=True, states=STATE)
    csll_aliquota = fields.Float(
        string='Alíquota', digits=('Account'),
        readonly=True, states=STATE)
    csll_valor_retencao = fields.Monetary(
        string='Valor Retenção', digits=('Account'),
        readonly=True, states=STATE)
    irrf_base_calculo = fields.Monetary(
        string='Base de Cálculo', digits=('Account'),
        readonly=True, states=STATE)
    irrf_aliquota = fields.Float(
        string='Alíquota', digits=('Account'),
        readonly=True, states=STATE)
    irrf_valor_retencao = fields.Monetary(
        string='Valor Retenção', digits=('Account'),
        readonly=True, states=STATE)
    inss_base_calculo = fields.Monetary(
        string='Base de Cálculo', digits=('Account'),
        readonly=True, states=STATE)
    inss_aliquota = fields.Float(
        string='Alíquota', digits=('Account'),
        readonly=True, states=STATE)
    inss_valor_retencao = fields.Monetary(
        string='Valor Retenção', digits=('Account'),
        readonly=True, states=STATE)

    account_invoice_line_id = fields.Many2one(
        string="Account Invoice Line",
        comodel_name="account.invoice.line",
        )

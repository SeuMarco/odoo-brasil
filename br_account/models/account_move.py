# © 2009 Renato Lima - Akretion
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError

<<<<<<< HEAD

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('invoice_line_ids.price_subtotal', 'line_ids', 'currency_id',
                 'company_id')
    def _compute_amount(self):
        for rec in self:
            lines = rec.line_ids
            rec.total_tax = sum(l.price_tax for l in lines)
            rec.icms_base = sum(l.icms_base_calculo for l in lines)
            rec.icms_value = sum(l.icms_valor for l in lines)
            rec.icms_st_base = sum(l.icms_st_base_calculo for l in lines)
            rec.icms_st_value = sum(l.icms_st_valor for l in lines)
            rec.valor_icms_uf_remet = sum(l.icms_uf_remet for l in lines)
            rec.valor_icms_uf_dest = sum(l.icms_uf_dest for l in lines)
            rec.valor_icms_fcp_uf_dest = sum(l.icms_fcp_uf_dest for l in lines)
            rec.issqn_base = sum(l.issqn_base_calculo for l in lines)
            rec.issqn_value = sum(abs(l.issqn_valor) for l in lines)
            rec.ipi_base = sum(l.ipi_base_calculo for l in lines)
            rec.ipi_value = sum(l.ipi_valor for l in lines)
            rec.pis_base = sum(l.pis_base_calculo for l in lines)
            rec.pis_value = sum(abs(l.pis_valor) for l in lines)
            rec.cofins_base = sum(l.cofins_base_calculo for l in lines)
            rec.cofins_value = sum(abs(l.cofins_valor) for l in lines)
            rec.ii_base = sum(l.ii_base_calculo for l in lines)
            rec.ii_value = sum(l.ii_valor for l in lines)
            rec.csll_base = sum(l.csll_base_calculo for l in lines)
            rec.csll_value = sum(abs(l.csll_valor) for l in lines)
            rec.irrf_base = sum(l.irrf_base_calculo for l in lines)
            rec.irrf_value = sum(abs(l.irrf_valor) for l in lines)
            rec.inss_base = sum(l.inss_base_calculo for l in lines)
            rec.inss_value = sum(abs(l.inss_valor) for l in lines)

            # Retenções
            rec.issqn_retention = sum(
                abs(l.issqn_valor) if l.issqn_valor < 0 else 0.0

                for l in lines)
            rec.pis_retention = sum(
                abs(l.pis_valor) if l.pis_valor < 0 else 0.0 for l in lines)
            rec.cofins_retention = sum(
                abs(l.cofins_valor) if l.cofins_valor < 0 else 0.0

                for l in lines)
            rec.csll_retention = sum(
                abs(l.csll_valor) if l.csll_valor < 0 else 0 for l in lines)
            rec.irrf_retention = sum(
                abs(l.irrf_valor) if l.irrf_valor < 0 else 0.0 for l in lines)
            rec.inss_retention = sum(
                abs(l.inss_valor) if l.inss_valor < 0 else 0.0 for l in lines)

            rec.total_bruto = sum(l.valor_bruto for l in lines)
            rec.total_desconto = sum(l.valor_desconto for l in lines)
            rec.total_tributos_federais = sum(l.tributos_estimados_federais
                                              for l in lines)
            rec.total_tributos_estaduais = sum(l.tributos_estimados_estaduais
                                               for l in lines)
            rec.total_tributos_municipais = sum(l.tributos_estimados_municipais
                                                for l in lines)
            rec.total_tributos_estimados = sum(l.tributos_estimados
                                               for l in lines)
            # TOTAL
            rec.amount_total = rec.total_bruto - \
                rec.total_desconto + rec.total_tax
            sign = rec.type in ['in_refund', 'out_refund'] and -1 or 1
            rec.amount_total_company_signed = rec.amount_total * sign
            rec.amount_total_signed = rec.amount_total * sign

        return super(AccountMove, self)._compute_amount()


    @api.depends('move_id.line_ids')
    def _compute_receivables(self):
        self.receivable_move_line_ids = self.move_id.line_ids.filtered(
            lambda m: m.account_id.user_type_id.type == 'receivable').sorted(
                key=lambda m: m.date_maturity)

    @api.depends('move_id.line_ids')
    def _compute_payables(self):
        self.payable_move_line_ids = self.move_id.line_ids.filtered(
            lambda m: m.account_id.user_type_id.type == 'payable')

    total_tax = fields.Float(string='Impostos ( + )',
                             readonly=True,
                             compute='_compute_amount',
                             digits=('Account'),
                             store=True)

    receivable_move_line_ids = fields.Many2many('account.move.line',
                                                string='Receivable Move Lines',
                                                compute='_compute_receivables')

    payable_move_line_ids = fields.Many2many('account.move.line',
                                             string='Payable Move Lines',
                                             compute='_compute_payables')

    product_serie_id = fields.Many2one(
        'br_account.document.serie',
        string='Série produtos',
        domain="[('fiscal_document_id', '=', product_document_id),\
        ('company_id','=',company_id)]",
        readonly=True,
        states={'draft': [('readonly', False)]})
    product_document_id = fields.Many2one(
        'br_account.fiscal.document',
        string='Documento produtos',
        readonly=True,
        states={'draft': [('readonly', False)]})
    service_serie_id = fields.Many2one(
        'br_account.document.serie',
        string='Série serviços',
        domain="[('fiscal_document_id', '=', service_document_id),\
        ('company_id','=',company_id)]",
        readonly=True,
        states={'draft': [('readonly', False)]})
    service_document_id = fields.Many2one(
        'br_account.fiscal.document',
        string='Documento serviços',
        readonly=True,
        states={'draft': [('readonly', False)]})
    fiscal_document_related_ids = fields.One2many(
        'br_account.document.related',
        'move_id',
        _("Documento Fiscal Relacionado"),
        readonly=True,
        states={'draft': [('readonly', False)]})
    fiscal_observation_ids = fields.Many2many(
        'br_account.fiscal.observation',
        string="Observações Fiscais",
        readonly=True,
        states={'draft': [('readonly', False)]})
    fiscal_comment = fields.Text('Observação Fiscal',
                                 readonly=True,
                                 states={'draft': [('readonly', False)]})

    total_bruto = fields.Float(string='Total Bruto ( = )',
                               store=True,
                               digits=('Account'),
                               compute='_compute_amount')
    total_desconto = fields.Float(string='Desconto ( - )',
                                  store=True,
                                  digits=('Account'),
                                  compute='_compute_amount')

    icms_base = fields.Float(string='Base ICMS',
                             store=True,
                             compute='_compute_amount',
                             digits=('Account'))
    icms_value = fields.Float(string='Valor ICMS',
                              digits=('Account'),
                              compute='_compute_amount',
                              store=True)
    icms_st_base = fields.Float(string='Base ICMS ST',
                                store=True,
                                compute='_compute_amount',
                                digits=('Account'))
    icms_st_value = fields.Float(string='Valor ICMS ST',
                                 store=True,
                                 compute='_compute_amount',
                                 digits=('Account'))
    valor_icms_fcp_uf_dest = fields.Float(
        string="Total ICMS FCP",
        store=True,
        compute='_compute_amount',
        help='Total total do ICMS relativo Fundo de Combate à Pobreza (FCP) \
        da UF de destino')
    valor_icms_uf_dest = fields.Float(
        string="ICMS Destino",
        store=True,
        compute='_compute_amount',
        help='Valor total do ICMS Interestadual para a UF de destino')
    valor_icms_uf_remet = fields.Float(
        string="ICMS Remetente",
        store=True,
        compute='_compute_amount',
        help='Valor total do ICMS Interestadual para a UF do Remetente')
    issqn_base = fields.Float(string='Base ISSQN',
                              store=True,
                              digits=('Account'),
                              compute='_compute_amount')
    issqn_value = fields.Float(string='Valor ISSQN',
                               store=True,
                               digits=('Account'),
                               compute='_compute_amount')
    issqn_retention = fields.Float(string='ISSQN Retido',
                                   store=True,
                                   digits=('Account'),
                                   compute='_compute_amount')
    ipi_base = fields.Float(string='Base IPI',
                            store=True,
                            digits=('Account'),
                            compute='_compute_amount')
    ipi_base_other = fields.Float(string="Base IPI Outras",
                                  store=True,
                                  digits=('Account'),
                                  compute='_compute_amount')
    ipi_value = fields.Float(string='Valor IPI',
                             store=True,
                             digits=('Account'),
                             compute='_compute_amount')
    pis_base = fields.Float(string='Base PIS',
                            store=True,
                            digits=('Account'),
                            compute='_compute_amount')
    pis_value = fields.Float(string='Valor PIS',
                             store=True,
                             digits=('Account'),
                             compute='_compute_amount')
    pis_retention = fields.Float(string='PIS Retido',
                                 store=True,
                                 digits=('Account'),
                                 compute='_compute_amount')
    cofins_base = fields.Float(string='Base COFINS',
                               store=True,
                               digits=('Account'),
                               compute='_compute_amount')
    cofins_value = fields.Float(string='Valor COFINS',
                                store=True,
                                digits=('Account'),
                                compute='_compute_amount',
                                readonly=True)
    cofins_retention = fields.Float(string='COFINS Retido',
                                    store=True,
                                    digits=('Account'),
                                    compute='_compute_amount',
                                    readonly=True)
    ii_base = fields.Float(string='Base II',
                           store=True,
                           digits=('Account'),
                           compute='_compute_amount')
    ii_value = fields.Float(string='Valor II',
                            store=True,
                            digits=('Account'),
                            compute='_compute_amount')
    csll_base = fields.Float(string='Base CSLL',
                             store=True,
                             digits=('Account'),
                             compute='_compute_amount')
    csll_value = fields.Float(string='Valor CSLL',
                              store=True,
                              digits=('Account'),
                              compute='_compute_amount')
    csll_retention = fields.Float(string='CSLL Retido',
                                  store=True,
                                  digits=('Account'),
                                  compute='_compute_amount')
    irrf_base = fields.Float(string='Base IRRF',
                             store=True,
                             digits=('Account'),
                             compute='_compute_amount')
    irrf_value = fields.Float(string='Valor IRRF',
                              store=True,
                              digits=('Account'),
                              compute='_compute_amount')
    irrf_retention = fields.Float(string='IRRF Retido',
                                  store=True,
                                  digits=('Account'),
                                  compute='_compute_amount')
    inss_base = fields.Float(string='Base INSS',
                             store=True,
                             digits=('Account'),
                             compute='_compute_amount')
    inss_value = fields.Float(string='Valor INSS',
                              store=True,
                              digits=('Account'),
                              compute='_compute_amount')
    inss_retention = fields.Float(string='INSS Retido',
                                  store=True,
                                  digits=('Account'),
                                  compute='_compute_amount')
    total_tributos_federais = fields.Float(string='Total de Tributos Federais',
                                           store=True,
                                           digits=('Account'),
                                           compute='_compute_amount')
    total_tributos_estaduais = fields.Float(
        string='Total de Tributos Estaduais',
        store=True,
        digits=('Account'),
        compute='_compute_amount')
    total_tributos_municipais = fields.Float(
        string='Total de Tributos Municipais',
        store=True,
        digits=('Account'),
        compute='_compute_amount')
    total_tributos_estimados = fields.Float(string='Total de Tributos',
                                            store=True,
                                            digits=('Account'),
                                            compute='_compute_amount')

    @api.onchange('fiscal_position_id')
    def _onchange_br_account_fiscal_position_id(self):
        if self.fiscal_position_id and self.fiscal_position_id.account_id:
            self.account_id = self.fiscal_position_id.account_id.id

        if self.fiscal_position_id and self.fiscal_position_id.journal_id:
            self.journal_id = self.fiscal_position_id.journal_id

        self.product_serie_id = self.fiscal_position_id.product_serie_id.id
        self.product_document_id = \
            self.fiscal_position_id.product_document_id.id

        self.service_serie_id = self.fiscal_position_id.service_serie_id.id
        self.service_document_id = \
            self.fiscal_position_id.service_document_id.id

        ob_ids = [x.id for x in self.fiscal_position_id.fiscal_observation_ids]
        self.fiscal_observation_ids = [(6, False, ob_ids)]

    def action_invoice_cancel_paid(self):
        if self.filtered(lambda inv: inv.state not in
                         ['proforma2', 'draft', 'open', 'paid']):
            raise UserError(
                _("Invoice must be in draft, Pro-forma or open \
                  state in order to be cancelled."))

        return self.action_cancel()

    @api.model
    def invoice_line_move_line_get(self):
        res = super(AccountInvoice, self).invoice_line_move_line_get()

        contador = 0

        for line in self.invoice_line_ids:
            if line.quantity == 0:
                continue
            res[contador]['price'] = line.valor_liquido

            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            ctx = line._prepare_tax_context()
            tax_ids = line.invoice_line_tax_ids.with_context(**ctx)

            taxes_dict = tax_ids.compute_all(price,
                                             self.currency_id,
                                             line.quantity,
                                             product=line.product_id,
                                             partner=self.partner_id)

            for tax in line.invoice_line_tax_ids:
                tax_dict = next(x for x in taxes_dict['taxes']
                                if x['id'] == tax.id)

                if tax.price_include and (not tax.account_id
                                          or not tax.deduced_account_id):

                    if tax_dict['amount'] > 0.0:  # Negativo é retido
                        res[contador]['price'] -= round(tax_dict['amount'], 2)

            contador += 1

        return res

    def finalize_invoice_move_lines(self, move_lines):
        res = super(AccountInvoice, self).\
            finalize_invoice_move_lines(move_lines)
        count = 1

        for invoice_line in res:
            line = invoice_line[2]
            line['ref'] = self.origin

            if line['name'] == '/' or (line['name'] == self.name
                                       and self.name):
                line['name'] = "%02d" % count
                count += 1

        return res

    def get_taxes_values(self):
        tax_grouped = {}

        for line in self.invoice_line_ids:
            other_taxes = line.invoice_line_tax_ids.filtered(
                lambda x: not x.domain)
            line.invoice_line_tax_ids = other_taxes | line.tax_icms_id | \
                line.tax_ipi_id | line.tax_pis_id | line.tax_cofins_id | \
                line.tax_issqn_id | line.tax_ii_id | line.tax_icms_st_id | \
                line.tax_csll_id | line.tax_irrf_id | \
                line.tax_inss_id

            ctx = line._prepare_tax_context()
            tax_ids = line.invoice_line_tax_ids.with_context(**ctx)

            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_ids.compute_all(price_unit, self.currency_id,
                                        line.quantity, line.product_id,
                                        self.partner_id)['taxes']

            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(
                    tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += round(val['amount'], 2)
                    tax_grouped[key]['base'] += val['base']

        return tax_grouped

    @api.model
    def tax_line_move_line_get(self):
        res = super(AccountInvoice, self).tax_line_move_line_get()

        done_taxes = []

        for tax_line in sorted(self.line_ids, key=lambda x: -x.sequence):
            if tax_line.amount and tax_line.tax_id.deduced_account_id:
                tax = tax_line.tax_id
                done_taxes.append(tax.id)
                res.append({
                    'invoice_tax_line_id':
                    tax_line.id,
                    'tax_line_id':
                    tax_line.tax_id.id,
                    'type':
                    'tax',
                    'name':
                    tax_line.name,
                    'price_unit':
                    tax_line.amount * -1,
                    'quantity':
                    1,
                    'price':
                    tax_line.amount * -1,
                    'account_id':
                    tax_line.tax_id.deduced_account_id.id,
                    'account_analytic_id':
                    tax_line.account_analytic_id.id,
                    'invoice_id':
                    self.id,
                    'tax_ids': [(6, 0, done_taxes)]

                    if tax_line.tax_id.include_base_amount else []
                })

        return res

    @api.model
    def _prepare_refund(self,
                        invoice,
                        date_invoice=None,
                        date=None,
                        description=None,
                        journal_id=None):
        res = super(AccountInvoice,
                    self)._prepare_refund(invoice,
                                          date_invoice=date_invoice,
                                          date=date,
                                          description=description,
                                          journal_id=journal_id)
        docs_related = self._prepare_related_documents(invoice)
        res['fiscal_document_related_ids'] = docs_related
        res['product_document_id'] = invoice.product_document_id.id
        res['product_serie_id'] = invoice.product_serie_id.id
        res['service_document_id'] = invoice.service_document_id.id
        res['service_serie_id'] = invoice.service_serie_id.id

        return res

    def _prepare_related_documents(self, invoice):
        doc_related = self.env['br_account.document.related']
        related_vals = []

        for doc in invoice.invoice_eletronic_ids:
            vals = {
                'invoice_related_id':
                invoice.id,
                'document_type':
                doc_related.translate_document_type(
                    invoice.product_document_id.code),
                'access_key':
                doc.chave_nfe,
                'numero':
                doc.numero
            }
            related = (0, False, vals)
            related_vals.append(related)

        return related_vals

<<<<<<< HEAD
=======
=======
>>>>>>> 2614df42964d4858c2816b3e0adb82b10261ed30
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

<<<<<<< HEAD
    @api.depends('invoice_line_ids.price_subtotal', 'line_ids', 'currency_id',
                 'company_id')
=======
    @api.depends('invoice_line_ids.price_subtotal', 'line_ids',
                 'currency_id', 'company_id')
>>>>>>> 2614df42964d4858c2816b3e0adb82b10261ed30
    def _compute_amount(self):
        for rec in self:
            lines = rec.line_ids
            rec.total_tax = sum(l.price_tax for l in lines)
            rec.icms_base = sum(l.icms_base_calculo for l in lines)
            rec.icms_value = sum(l.icms_valor for l in lines)
            rec.icms_st_base = sum(l.icms_st_base_calculo for l in lines)
            rec.icms_st_value = sum(l.icms_st_valor for l in lines)
            rec.valor_icms_uf_remet = sum(l.icms_uf_remet for l in lines)
            rec.valor_icms_uf_dest = sum(l.icms_uf_dest for l in lines)
            rec.valor_icms_fcp_uf_dest = sum(l.icms_fcp_uf_dest for l in lines)
            rec.issqn_base = sum(l.issqn_base_calculo for l in lines)
            rec.issqn_value = sum(abs(l.issqn_valor) for l in lines)
            rec.ipi_base = sum(l.ipi_base_calculo for l in lines)
            rec.ipi_value = sum(l.ipi_valor for l in lines)
            rec.pis_base = sum(l.pis_base_calculo for l in lines)
            rec.pis_value = sum(abs(l.pis_valor) for l in lines)
            rec.cofins_base = sum(l.cofins_base_calculo for l in lines)
            rec.cofins_value = sum(abs(l.cofins_valor) for l in lines)
            rec.ii_base = sum(l.ii_base_calculo for l in lines)
            rec.ii_value = sum(l.ii_valor for l in lines)
            rec.csll_base = sum(l.csll_base_calculo for l in lines)
            rec.csll_value = sum(abs(l.csll_valor) for l in lines)
            rec.irrf_base = sum(l.irrf_base_calculo for l in lines)
            rec.irrf_value = sum(abs(l.irrf_valor) for l in lines)
            rec.inss_base = sum(l.inss_base_calculo for l in lines)
            rec.inss_value = sum(abs(l.inss_valor) for l in lines)

            # Retenções
            rec.issqn_retention = sum(
                abs(l.issqn_valor) if l.issqn_valor < 0 else 0.0

                for l in lines)
            rec.pis_retention = sum(
                abs(l.pis_valor) if l.pis_valor < 0 else 0.0 for l in lines)
            rec.cofins_retention = sum(
                abs(l.cofins_valor) if l.cofins_valor < 0 else 0.0

                for l in lines)
            rec.csll_retention = sum(
                abs(l.csll_valor) if l.csll_valor < 0 else 0 for l in lines)
            rec.irrf_retention = sum(
                abs(l.irrf_valor) if l.irrf_valor < 0 else 0.0 for l in lines)
            rec.inss_retention = sum(
                abs(l.inss_valor) if l.inss_valor < 0 else 0.0 for l in lines)

            rec.total_bruto = sum(l.valor_bruto for l in lines)
            rec.total_desconto = sum(l.valor_desconto for l in lines)
            rec.total_tributos_federais = sum(l.tributos_estimados_federais
                                              for l in lines)
            rec.total_tributos_estaduais = sum(l.tributos_estimados_estaduais
                                               for l in lines)
            rec.total_tributos_municipais = sum(l.tributos_estimados_municipais
                                                for l in lines)
            rec.total_tributos_estimados = sum(l.tributos_estimados
                                               for l in lines)
            # TOTAL
            rec.amount_total = rec.total_bruto - \
                rec.total_desconto + rec.total_tax
            sign = rec.type in ['in_refund', 'out_refund'] and -1 or 1
            rec.amount_total_company_signed = rec.amount_total * sign
            rec.amount_total_signed = rec.amount_total * sign

        return res

    @api.depends('move_id.line_ids')
    def _compute_receivables(self):
        self.receivable_move_line_ids = self.move_id.line_ids.filtered(
            lambda m: m.account_id.user_type_id.type == 'receivable').sorted(
                key=lambda m: m.date_maturity)

    @api.depends('move_id.line_ids')
    def _compute_payables(self):
        self.payable_move_line_ids = self.move_id.line_ids.filtered(
            lambda m: m.account_id.user_type_id.type == 'payable')

    total_tax = fields.Float(string='Impostos ( + )',
                             readonly=True,
                             compute='_compute_amount',
                             digits=('Account'),
                             store=True)

    receivable_move_line_ids = fields.Many2many('account.move.line',
                                                string='Receivable Move Lines',
                                                compute='_compute_receivables')

    payable_move_line_ids = fields.Many2many('account.move.line',
                                             string='Payable Move Lines',
                                             compute='_compute_payables')

    product_serie_id = fields.Many2one(
        'br_account.document.serie',
<<<<<<< HEAD
        string='Série produtos',
=======
        string=u'Série produtos',
>>>>>>> 2614df42964d4858c2816b3e0adb82b10261ed30
        domain="[('fiscal_document_id', '=', product_document_id),\
        ('company_id','=',company_id)]",
        readonly=True,
        states={'draft': [('readonly', False)]})
    product_document_id = fields.Many2one(
        'br_account.fiscal.document',
        string='Documento produtos',
        readonly=True,
        states={'draft': [('readonly', False)]})
    service_serie_id = fields.Many2one(
        'br_account.document.serie',
<<<<<<< HEAD
        string='Série serviços',
=======
        string=u'Série serviços',
>>>>>>> 2614df42964d4858c2816b3e0adb82b10261ed30
        domain="[('fiscal_document_id', '=', service_document_id),\
        ('company_id','=',company_id)]",
        readonly=True,
        states={'draft': [('readonly', False)]})
    service_document_id = fields.Many2one(
        'br_account.fiscal.document',
        string='Documento serviços',
        readonly=True,
        states={'draft': [('readonly', False)]})
    fiscal_document_related_ids = fields.One2many(
        'br_account.document.related',
        'move_id',
        _("Documento Fiscal Relacionado"),
        readonly=True,
        states={'draft': [('readonly', False)]})
    fiscal_observation_ids = fields.Many2many(
        'br_account.fiscal.observation',
<<<<<<< HEAD
        string="Observações Fiscais",
        readonly=True,
        states={'draft': [('readonly', False)]})
    fiscal_comment = fields.Text('Observação Fiscal',
=======
        string=u"Observações Fiscais",
        readonly=True,
        states={'draft': [('readonly', False)]})
    fiscal_comment = fields.Text(u'Observação Fiscal',
>>>>>>> 2614df42964d4858c2816b3e0adb82b10261ed30
                                 readonly=True,
                                 states={'draft': [('readonly', False)]})

    total_bruto = fields.Float(string='Total Bruto ( = )',
                               store=True,
                               digits=('Account'),
                               compute='_compute_amount')
    total_desconto = fields.Float(string='Desconto ( - )',
                                  store=True,
                                  digits=('Account'),
                                  compute='_compute_amount')

    icms_base = fields.Float(string='Base ICMS',
                             store=True,
                             compute='_compute_amount',
                             digits=('Account'))
    icms_value = fields.Float(string='Valor ICMS',
                              digits=('Account'),
                              compute='_compute_amount',
                              store=True)
    icms_st_base = fields.Float(string='Base ICMS ST',
                                store=True,
                                compute='_compute_amount',
                                digits=('Account'))
    icms_st_value = fields.Float(string='Valor ICMS ST',
                                 store=True,
                                 compute='_compute_amount',
                                 digits=('Account'))
    valor_icms_fcp_uf_dest = fields.Float(
        string="Total ICMS FCP",
        store=True,
        compute='_compute_amount',
<<<<<<< HEAD
        help='Total total do ICMS relativo Fundo de Combate à Pobreza (FCP) \
=======
        help=u'Total total do ICMS relativo Fundo de Combate à Pobreza (FCP) \
>>>>>>> 2614df42964d4858c2816b3e0adb82b10261ed30
        da UF de destino')
    valor_icms_uf_dest = fields.Float(
        string="ICMS Destino",
        store=True,
        compute='_compute_amount',
        help='Valor total do ICMS Interestadual para a UF de destino')
    valor_icms_uf_remet = fields.Float(
        string="ICMS Remetente",
        store=True,
        compute='_compute_amount',
        help='Valor total do ICMS Interestadual para a UF do Remetente')
    issqn_base = fields.Float(string='Base ISSQN',
                              store=True,
                              digits=('Account'),
                              compute='_compute_amount')
    issqn_value = fields.Float(string='Valor ISSQN',
                               store=True,
                               digits=('Account'),
                               compute='_compute_amount')
    issqn_retention = fields.Float(string='ISSQN Retido',
                                   store=True,
                                   digits=('Account'),
                                   compute='_compute_amount')
    ipi_base = fields.Float(string='Base IPI',
                            store=True,
                            digits=('Account'),
                            compute='_compute_amount')
    ipi_base_other = fields.Float(string="Base IPI Outras",
                                  store=True,
                                  digits=('Account'),
                                  compute='_compute_amount')
    ipi_value = fields.Float(string='Valor IPI',
                             store=True,
                             digits=('Account'),
                             compute='_compute_amount')
    pis_base = fields.Float(string='Base PIS',
                            store=True,
                            digits=('Account'),
                            compute='_compute_amount')
    pis_value = fields.Float(string='Valor PIS',
                             store=True,
                             digits=('Account'),
                             compute='_compute_amount')
    pis_retention = fields.Float(string='PIS Retido',
                                 store=True,
                                 digits=('Account'),
                                 compute='_compute_amount')
    cofins_base = fields.Float(string='Base COFINS',
                               store=True,
                               digits=('Account'),
                               compute='_compute_amount')
    cofins_value = fields.Float(string='Valor COFINS',
                                store=True,
                                digits=('Account'),
                                compute='_compute_amount',
                                readonly=True)
    cofins_retention = fields.Float(string='COFINS Retido',
                                    store=True,
                                    digits=('Account'),
                                    compute='_compute_amount',
                                    readonly=True)
    ii_base = fields.Float(string='Base II',
                           store=True,
                           digits=('Account'),
                           compute='_compute_amount')
    ii_value = fields.Float(string='Valor II',
                            store=True,
                            digits=('Account'),
                            compute='_compute_amount')
    csll_base = fields.Float(string='Base CSLL',
                             store=True,
                             digits=('Account'),
                             compute='_compute_amount')
    csll_value = fields.Float(string='Valor CSLL',
                              store=True,
                              digits=('Account'),
                              compute='_compute_amount')
    csll_retention = fields.Float(string='CSLL Retido',
                                  store=True,
                                  digits=('Account'),
                                  compute='_compute_amount')
    irrf_base = fields.Float(string='Base IRRF',
                             store=True,
                             digits=('Account'),
                             compute='_compute_amount')
    irrf_value = fields.Float(string='Valor IRRF',
                              store=True,
                              digits=('Account'),
                              compute='_compute_amount')
    irrf_retention = fields.Float(string='IRRF Retido',
                                  store=True,
                                  digits=('Account'),
                                  compute='_compute_amount')
    inss_base = fields.Float(string='Base INSS',
                             store=True,
                             digits=('Account'),
                             compute='_compute_amount')
    inss_value = fields.Float(string='Valor INSS',
                              store=True,
                              digits=('Account'),
                              compute='_compute_amount')
    inss_retention = fields.Float(string='INSS Retido',
                                  store=True,
                                  digits=('Account'),
                                  compute='_compute_amount')
    total_tributos_federais = fields.Float(string='Total de Tributos Federais',
                                           store=True,
                                           digits=('Account'),
                                           compute='_compute_amount')
    total_tributos_estaduais = fields.Float(
        string='Total de Tributos Estaduais',
        store=True,
        digits=('Account'),
        compute='_compute_amount')
    total_tributos_municipais = fields.Float(
        string='Total de Tributos Municipais',
        store=True,
        digits=('Account'),
        compute='_compute_amount')
    total_tributos_estimados = fields.Float(string='Total de Tributos',
                                            store=True,
                                            digits=('Account'),
                                            compute='_compute_amount')

    @api.onchange('fiscal_position_id')
    def _onchange_br_account_fiscal_position_id(self):
        if self.fiscal_position_id and self.fiscal_position_id.account_id:
            self.account_id = self.fiscal_position_id.account_id.id

        if self.fiscal_position_id and self.fiscal_position_id.journal_id:
            self.journal_id = self.fiscal_position_id.journal_id

        self.product_serie_id = self.fiscal_position_id.product_serie_id.id
        self.product_document_id = \
            self.fiscal_position_id.product_document_id.id

        self.service_serie_id = self.fiscal_position_id.service_serie_id.id
        self.service_document_id = \
            self.fiscal_position_id.service_document_id.id

        ob_ids = [x.id for x in self.fiscal_position_id.fiscal_observation_ids]
        self.fiscal_observation_ids = [(6, False, ob_ids)]

    def action_invoice_cancel_paid(self):
        if self.filtered(lambda inv: inv.state not in
                         ['proforma2', 'draft', 'open', 'paid']):
            raise UserError(
                _("Invoice must be in draft, Pro-forma or open \
<<<<<<< HEAD
                  state in order to be cancelled."))
=======
                              state in order to be cancelled."))
>>>>>>> 2614df42964d4858c2816b3e0adb82b10261ed30

        return self.action_cancel()

    @api.model
    def invoice_line_move_line_get(self):
        res = super(AccountInvoice, self).invoice_line_move_line_get()

        contador = 0

        for line in self.invoice_line_ids:
            if line.quantity == 0:
                continue
            res[contador]['price'] = line.valor_liquido

            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            ctx = line._prepare_tax_context()
            tax_ids = line.invoice_line_tax_ids.with_context(**ctx)

            taxes_dict = tax_ids.compute_all(price,
                                             self.currency_id,
                                             line.quantity,
                                             product=line.product_id,
                                             partner=self.partner_id)

            for tax in line.invoice_line_tax_ids:
                tax_dict = next(x for x in taxes_dict['taxes']
                                if x['id'] == tax.id)

                if tax.price_include and (not tax.account_id
                                          or not tax.deduced_account_id):

                    if tax_dict['amount'] > 0.0:  # Negativo é retido
                        res[contador]['price'] -= round(tax_dict['amount'], 2)

            contador += 1

        return res

    def finalize_invoice_move_lines(self, move_lines):
        res = super(AccountInvoice, self).\
            finalize_invoice_move_lines(move_lines)
        count = 1

        for invoice_line in res:
            line = invoice_line[2]
            line['ref'] = self.origin

            if line['name'] == '/' or (line['name'] == self.name
                                       and self.name):
                line['name'] = "%02d" % count
                count += 1

        return res

    def get_taxes_values(self):
        tax_grouped = {}

        for line in self.invoice_line_ids:
            other_taxes = line.invoice_line_tax_ids.filtered(
                lambda x: not x.domain)
            line.invoice_line_tax_ids = other_taxes | line.tax_icms_id | \
                line.tax_ipi_id | line.tax_pis_id | line.tax_cofins_id | \
                line.tax_issqn_id | line.tax_ii_id | line.tax_icms_st_id | \
                line.tax_csll_id | line.tax_irrf_id | \
                line.tax_inss_id

            ctx = line._prepare_tax_context()
            tax_ids = line.invoice_line_tax_ids.with_context(**ctx)

            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_ids.compute_all(price_unit, self.currency_id,
                                        line.quantity, line.product_id,
                                        self.partner_id)['taxes']

            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(
                    tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += round(val['amount'], 2)
                    tax_grouped[key]['base'] += val['base']

        return tax_grouped

    @api.model
    def tax_line_move_line_get(self):
        res = super(AccountInvoice, self).tax_line_move_line_get()

        done_taxes = []

        for tax_line in sorted(self.line_ids, key=lambda x: -x.sequence):
            if tax_line.amount and tax_line.tax_id.deduced_account_id:
                tax = tax_line.tax_id
                done_taxes.append(tax.id)
                res.append({
                    'invoice_tax_line_id':
                    tax_line.id,
                    'tax_line_id':
                    tax_line.tax_id.id,
                    'type':
                    'tax',
                    'name':
                    tax_line.name,
                    'price_unit':
                    tax_line.amount * -1,
                    'quantity':
                    1,
                    'price':
                    tax_line.amount * -1,
                    'account_id':
                    tax_line.tax_id.deduced_account_id.id,
                    'account_analytic_id':
                    tax_line.account_analytic_id.id,
                    'invoice_id':
                    self.id,
                    'tax_ids': [(6, 0, done_taxes)]

                    if tax_line.tax_id.include_base_amount else []
                })

        return res

    @api.model
    def _prepare_refund(self,
                        invoice,
                        date_invoice=None,
                        date=None,
                        description=None,
                        journal_id=None):
        res = super(AccountInvoice,
                    self)._prepare_refund(invoice,
                                          date_invoice=date_invoice,
                                          date=date,
                                          description=description,
                                          journal_id=journal_id)
        docs_related = self._prepare_related_documents(invoice)
        res['fiscal_document_related_ids'] = docs_related
        res['product_document_id'] = invoice.product_document_id.id
        res['product_serie_id'] = invoice.product_serie_id.id
        res['service_document_id'] = invoice.service_document_id.id
        res['service_serie_id'] = invoice.service_serie_id.id

        return res

    def _prepare_related_documents(self, invoice):
        doc_related = self.env['br_account.document.related']
        related_vals = []

        for doc in invoice.invoice_eletronic_ids:
            vals = {
                'invoice_related_id':
                invoice.id,
                'document_type':
                doc_related.translate_document_type(
                    invoice.product_document_id.code),
                'access_key':
                doc.chave_nfe,
                'numero':
                doc.numero
            }
            related = (0, False, vals)
            related_vals.append(related)

        return related_vals
<<<<<<< HEAD
>>>>>>> 79d6053a... First steps and save to cloud
=======
>>>>>>> 2614df42964d4858c2816b3e0adb82b10261ed30

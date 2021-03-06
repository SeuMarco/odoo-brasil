# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
import base64
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestImportStatement(TransactionCase):

    caminho = os.path.dirname(__file__)

    def setUp(self):
        super(TestImportStatement, self).setUp()
        self.journal = self.env['account.journal'].create({
            'name': 'Bank',
            'code': 'BNK',
            'type': 'bank',
            'bank_acc_number': '123',
            'currency_id': self.env.ref('base.BRL').id,
        })

        self.import_ofx = self.env['account.bank.statement.import'].create({
            'force_format': True,
            'file_format': 'ofx',
            'force_journal_account': True,
            'journal_id': self.journal.id,
            'data_file': base64.b64encode(b'000'),
        })

    def test_invalid_files(self):
        with self.assertRaises(UserError):
            self.import_ofx.import_file()

    def test_import_ofx_default(self):
        ofx = os.path.join(self.caminho, 'extratos/extrato.ofx')
        self.import_ofx.data_file = base64.b64encode(open(ofx, 'rb').read())
        self.import_ofx.import_file()

        stmt = self.env['account.bank.statement'].search(
            [('journal_id', '=', self.journal.id)])

        lines = stmt.line_ids.sorted(lambda x: x.ref, reverse=True)
        self.assertTrue(stmt)
        self.assertEqual(len(lines), 28)
        self.assertEqual(lines[0].amount, -150.0)
        self.assertEqual(lines[0].name, ': SAQUE 24H 13563697')
        self.assertEqual(lines[0].ref, '20160926001')
        self.assertEqual(stmt.balance_start, -894.45)
        self.assertEqual(round(stmt.balance_end_real, 2), 10.0)
        self.assertEqual(stmt.balance_end, 10.0)

    def test_import_ofx_bb(self):
        ofx = os.path.join(self.caminho, 'extratos/extrato-bb.ofx')
        self.import_ofx.data_file = base64.b64encode(open(ofx, 'rb').read())
        self.import_ofx.import_file()

        stmt = self.env['account.bank.statement'].search(
            [('journal_id', '=', self.journal.id)])

        lines = stmt.line_ids.sorted(lambda x: x.ref, reverse=True)
        self.assertTrue(stmt)
        self.assertEqual(len(lines), 26)
        self.assertEqual(lines[0].amount, -20.0)
        self.assertEqual(lines[0].name,
                          ': Telefone Pre-Pago - TIM - Sao Paulo')
        self.assertEqual(lines[0].ref, '20160908120000')
        self.assertEqual(stmt.balance_start, 7.09)
        self.assertEqual(round(stmt.balance_end_real, 2), 172.61)
        self.assertEqual(stmt.balance_end, 172.61)

    def test_import_ofx_itau(self):
        ofx = os.path.join(self.caminho, 'extratos/extrato-itau.ofx')
        self.import_ofx.data_file = base64.b64encode(open(ofx, 'rb').read())
        self.import_ofx.import_file()

        stmt = self.env['account.bank.statement'].search(
            [('journal_id', '=', self.journal.id)])

        lines = stmt.line_ids.sorted(lambda x: x.ref, reverse=True)
        self.assertTrue(stmt)
        self.assertEqual(len(lines), 10)
        self.assertEqual(lines[0].amount, -240.33)
        self.assertEqual(lines[0].name, ': SISPAG FORNECEDORES')
        self.assertEqual(lines[0].ref, '20160810002')
        self.assertEqual(stmt.balance_start, 4701.58)
        self.assertEqual(round(stmt.balance_end_real, 2), -2690.0)
        self.assertEqual(stmt.balance_end, -2690.0)

    def test_import_ofx_without_force(self):
        ofx = os.path.join(self.caminho, 'extratos/extrato.ofx')
        self.import_ofx.data_file = base64.b64encode(open(ofx, 'rb').read())
        self.import_ofx.force_format = False
        self.import_ofx.import_file()

        ofx = os.path.join(self.caminho, 'extratos/extrato-bb.ofx')
        self.import_ofx.data_file = base64.b64encode(open(ofx, 'rb').read())
        self.import_ofx.force_format = False
        self.import_ofx.import_file()

        ofx = os.path.join(self.caminho, 'extratos/extrato-itau.ofx')
        self.import_ofx.data_file = base64.b64encode(open(ofx, 'rb').read())
        self.import_ofx.force_format = False
        self.import_ofx.import_file()

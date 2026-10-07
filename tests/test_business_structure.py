import unittest
from brain.confluence import StorageText, SourceUnavailable


class BusinessStructureTests(unittest.TestCase):
    def test_table_keeps_scope_value_relationships(self):
        parser=StorageText()
        parser.feed('<h2>Eligibility</h2><table><tr><th>Region</th><th>Limit</th></tr>'
                    '<tr><td>EU</td><td>10</td></tr><tr><td>US</td><td>20</td></tr></table>')
        rows=[line.strip() for line in ''.join(parser.parts).splitlines() if line.strip()]
        self.assertEqual(rows,['Eligibility','Region\tLimit','EU\t10','US\t20'])
        self.assertNotIn('EU20',''.join(parser.parts))

    def test_untrusted_macro_still_rejected(self):
        parser=StorageText()
        with self.assertRaises(SourceUnavailable):
            parser.feed('<ac:structured-macro>hidden</ac:structured-macro>')

    def test_paragraph_wrapped_cells_survive_reader_normalization(self):
        parser=StorageText()
        parser.feed('<table><tr><td><p>EU</p></td><td><p>10</p></td></tr>'
                    '<tr><td><p>US</p></td><td><p>20</p></td></tr></table>')
        rows=[line.strip() for line in ''.join(parser.parts).splitlines() if line.strip()]
        self.assertEqual([[cell.strip() for cell in row.split('\t')] for row in rows],[['EU','10'],['US','20']])

    def test_empty_edge_cells_do_not_move_scope_or_values(self):
        parser=StorageText()
        parser.feed('<table><tr><th>Region</th><th>Limit</th><th>Comment</th></tr>'
                    '<tr><td></td><td><p>10</p></td><td></td></tr></table>')
        rows=[line.strip(' \r') for line in ''.join(parser.parts).splitlines() if line.strip() or '\t' in line]
        self.assertEqual([cell.strip() for cell in rows[1].split('\t')],['','10',''])


if __name__=='__main__': unittest.main()

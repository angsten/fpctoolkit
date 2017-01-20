import os
import os
import os
from unittest2 import TestCase

from fpctoolkit.io.vasp.incar import Incar
from fpctoolkit.util.path import Path

class Test(TestCase):

	class_title = 'Incar'
	data_dir_path = Path.clean(os.path.dirname(__file__), 'data_'+class_title)

	def setUp(self):
		self.data_path = Path.clean(self.__class__.data_dir_path)

	def test_init(self):
		file_path = Path.clean(self.data_path, "empty_incar")

		incar = Incar(file_path)
		self.assertEqual(incar.dict, {})
		self.assertEqual(incar.lines, [])

		incar[0] = "This is a comment"
		self.assertEqual(incar.dict, {})
		self.assertEqual(incar.lines, ["This is a comment"])

		incar['algo'] = 'Fast'
		self.assertEqual(incar.dict.items(), [('ALGO', 'Fast')])
		self.assertEqual(incar.lines, ['This is a comment', 'ALGO = Fast'])

		incar['ALGO'] = 'Fast'
		self.assertEqual(incar.dict.items(), [('ALGO', 'Fast')])
		self.assertEqual(incar.lines, ['This is a comment', 'ALGO = Fast'])

		incar['      ALgo  '] = 'Medium'
		self.assertEqual(incar.dict.items(), [('ALGO', 'Medium')])
		self.assertEqual(incar.lines, ['This is a comment', 'ALGO = Medium'])

		incar['NSW'] = 191
		incar += "Here is another comment"
		incar['nsw'] = '181'

		self.assertEqual(incar.dict.items(), [('ALGO', 'Medium'), ('NSW', '181')])
		self.assertEqual(incar.lines, ['This is a comment', 'ALGO = Medium', 'NSW = 181', 'Here is another comment'])

		incar[0] = "Comment revised"
		incar[1] = "   Algo =   Fast"

		self.assertEqual(incar.dict.items(), [('ALGO', 'Fast'), ('NSW', '181')])
		self.assertEqual(str(incar), 'Comment revised\nALGO = Fast\nNSW = 181\nHere is another comment\n')

		incar[2] += " #here is a comment"
		incar += "#and another"
		incar += "one more comment."

		self.assertEqual(incar.dict.items(), [('ALGO', 'Fast'), ('NSW', '181')])
		self.assertEqual(incar.lines, ['Comment revised', 'ALGO = Fast', 'NSW = 181 #here is a comment', 'Here is another comment', '#and another', 'one more comment.'])
		self.assertEqual(str(incar), 'Comment revised\nALGO = Fast\nNSW = 181 #here is a comment\nHere is another comment\n#and another\none more comment.\n')

		incar['isif'] = 3

		del incar['  ALgO']
		del incar['ALGo ']
		incar['algo'] = 'Slow'
		del incar['ALGO']
		incar['prec'] = 'accurate'
		incar['ediff'] = 0.000001

		self.assertEqual(incar.dict.items(), [('NSW', '181'), ('ISIF', '3'), ('PREC', 'accurate'), ('EDIFF', '1e-06')])
		self.assertEqual(incar.lines, ['Comment revised', 'NSW = 181 #here is a comment', 'Here is another comment', '#and another', 'one more comment.', 'ISIF = 3', 'PREC = accurate', 'EDIFF = 1e-06'])
		self.assertEqual(str(incar), 'Comment revised\nNSW = 181 #here is a comment\nHere is another comment\n#and another\none more comment.\nISIF = 3\nPREC = accurate\nEDIFF = 1e-06\n')
		self.assertEqual(float(incar['ediff']), 0.000001)
		self.assertEqual(incar['prec'], 'accurate')

		file_out_path = Path.clean(self.data_path, "test_made_incar")
		incar.write_to_path(file_out_path)

		incar = Incar(file_out_path)
		self.assertEqual(incar['prec'], 'accurate')
		self.assertEqual(str(incar), 'Comment revised\nNSW = 181 #here is a comment\nHere is another comment\n#and another\none more comment.\nISIF = 3\nPREC = accurate\nEDIFF = 1e-06\n')

		incar[0] = '    Comment revised   ' #should kill this whitespace
		self.assertEqual(str(incar), 'Comment revised\nNSW = 181 #here is a comment\nHere is another comment\n#and another\none more comment.\nISIF = 3\nPREC = accurate\nEDIFF = 1e-06\n')

		with self.assertRaises(Exception):
			incar['proper ty'] = 'value'

		with self.assertRaises(Exception):
			incar += 'PREC = repeat'
		
	def test_loaded(self):
		file_path = Path.clean(self.data_path, "incar_1")
		incar = Incar(file_path)

		self.assertEqual(incar.dict.items(), [('ALGO', 'Fast'), ('EDIFF', '0.00075'), ('ENCUT', '520'), ('IBRION', '2'), ('ICHARG', '1'), ('ISIF', '3'), ('ISMEAR', '-5'), ('ISPIN', '2'), ('LORBIT', '11'), ('LREAL', 'Auto'), ('LWAVE', 'False'), ('MAGMOM', '15*0.6'), ('NELM', '100'), ('NSW', '99'), ('PREC', 'Accurate'), ('SIGMA', '0.05')])
		self.assertEqual(incar.lines, ['Comment here #messy messy', 'ALGO = Fast #stuff here', 'whats up', 'EDIFF = 0.00075', 'ENCUT = 520', '\tIBRION = 2', 'ICHARG = 1', 'ISIF = 3', 'ISMEAR = -5', '  ISPIN = 2', 'LORBIT = 11 #comment with = sign', 'LREAL = Auto', 'LWAVE = False', 'MAGMOM = 15*0.6', 'NELM = 100                   ', 'NSW = 99', '    PREC = Accurate', '  #lonely sigma with = sign!', 'SIGMA = 0.05'])

		incar['nelm'] = 60
		del incar['ibrion']
		incar[0] = 'new comment'
		incar += 'made_up = accurate'
		incar[5] = 'icharg = 2'

		self.assertEqual(incar.dict.items(), [('ALGO', 'Fast'), ('EDIFF', '0.00075'), ('ENCUT', '520'), ('ICHARG', '2'), ('ISIF', '3'), ('ISMEAR', '-5'), ('ISPIN', '2'), ('LORBIT', '11'), ('LREAL', 'Auto'), ('LWAVE', 'False'), ('MAGMOM', '15*0.6'), ('NELM', '60'), ('NSW', '99'), ('PREC', 'Accurate'), ('SIGMA', '0.05'), ('MADE_UP', 'accurate')])
		self.assertEqual(incar.lines, ['new comment', 'ALGO = Fast #stuff here', 'whats up', 'EDIFF = 0.00075', 'ENCUT = 520', 'icharg = 2', 'ISiF = 3', 'IsmeAR = -5', '  ISPIN = 2', 'LORBIT = 11 #comment', 'LREAL = Auto', 'LWAVE = False', 'magmom = 15*0.6', 'NELM = 60', 'NSW = 99', '    PREC = Accurate', '  #lonely sigma', 'SIGMA = 0.05', 'made_up = accurate'])
		self.assertFalse(' algoo' in incar)
		self.assertTrue('encut' in incar)
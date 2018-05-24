import os
import unittest
from Daty.SmartJson import SmartJson

dir_data = os.path.join(os.path.dirname(os.path.realpath(__file__)),'data-samples')

class Test_SmartJson(unittest.TestCase):

    def setUp(self):
        self.project = SmartJson(os.path.join(dir_data,'project_1.json'))

    def test_setitem(self):
        key = self.project['results'].keys()[0]
        self.project['results'][key] = None
        self.assertEqual(self.project['results'][key], None)

    def test_rename(self):
        self.project.rename(['results'],'solution')
        self.assertEqual('results' not in self.project.keys(), True)
        self.assertEqual('solution' in self.project.keys(), True)

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(Test_SmartJson)
	unittest.TextTestRunner(verbosity=2).run(suite)
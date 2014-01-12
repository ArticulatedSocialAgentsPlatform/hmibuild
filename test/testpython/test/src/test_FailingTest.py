'''
Created on Nov 5, 2012

@author: hvanwelbergen
'''
import unittest

class FailingTest(unittest.TestCase):
    def setUp(self):
        pass        
    def tearDown(self):
        pass
    def testFail(self):
        self.assertTrue(True)
		
if __name__ == "__main__":
    unittest.main()
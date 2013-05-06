'''
Utilizacion del PyUnit
'''
import os
import unittest
import random
import tempfile
from com.py.sap.adm.mod import Usuario
#import app
#from app.database import db
from com.py.sap.loginC import app
from com.py.sap.util.database import init_db, engine
import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

#class TestCase(unittest.TestCase):
#    
#    def setUp(self):
#        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
#        app.app.config['TESTING'] = True
#        self.app = app.app.test_client()
#        #init_db.create_all()
#
#    def tearDown(self):
#        os.close(self.db_fd)
#        os.unlink(app.app.config['DATABASE'])
#        
#    def loginC(self, uid, pwd):
#        return self.app.post('/loginC', data=dict(
#            loginData = '{"username":"%s","passwd":"%s"}' % (uid,pwd) 
#        ), follow_redirects=True)
#
#    def test_loginC(self):
#        import json
#        assert json.loads(self.loginC('lila', 'lila').data)['success'] == True
#        assert json.loads(self.loginC('lila', 'no').data)['success'] == False
# 
#unittest.main()
class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.seq = range(10)

    def test_shuffle(self):
        # make sure the shuffled sequence does not lose any elements
        random.shuffle(self.seq)
        self.seq.sort()
        self.assertEqual(self.seq, range(10))

        # should raise an exception for an immutable sequence
        self.assertRaises(TypeError, random.shuffle, (1,2,3))

    def test_choice(self):
        element = random.choice(self.seq)
        self.assertTrue(element in self.seq)

    def test_sample(self):
        with self.assertRaises(ValueError):
            random.sample(self.seq, 20)
        for element in random.sample(self.seq, 5):
            self.assertTrue(element in self.seq)
            
    def loginC(self, uid, pwd):
        return self.app.post('/loginC', data=dict(
            loginData = '{"username":"%s","passwd":"%s"}' % (uid,pwd) 
        ), follow_redirects=True)

    def test_loginC(self):
        import json
        assert json.loads(self.loginC('admin', 'admin').data)['success'] == True
        assert json.loads(self.loginC('lila', 'no').data)['success'] == False

if __name__ == '__main__':
    """Este es el docstring de la funcion."""  
    unittest.main()

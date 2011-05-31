from Crypto.Hash import MD5
from Crypto.Cipher import AES
try: import simplejson as json
except ImportError: import json
import logging

debug = False
class fakelog(object):
    def info(self,arg): pass

if not debug:
    logging = fakelog()

class Cipher(object):
    """docstring for Cipher"""
    def __init__(self):
        super(Cipher, self).__init__()
    
    def hsh(self, key):
        """docstring for hsh"""
        self.hash = MD5.new()
        self.hash.update(key)
        return self.hash.hexdigest()
    
    def cryptInfo(self, key, info):
        info = json.dumps(info)
        # Pad to 16char blocks
        info = info[:-1] + " " * (16 - (len(info) % 16)) + "}"
        cipher = AES.new(key,AES.MODE_CBC)
        cryptinfo = cipher.encrypt(info)
        cryptinfo = cryptinfo.encode('hex')
        return cryptinfo
    
    def decryptInfo(self, key, cryptinfo):
        #logging.info('got as key: %s' % key)
        #logging.info('got as crypto: %s' % cryptinfo)
        cryptinfo = cryptinfo.decode('hex')
        cipher = AES.new(key, AES.MODE_CBC)
        try:
            #logging.info('Trying to decrypt')
            info = cipher.decrypt(cryptinfo)
            #logging.info('Parsing...')
            #logging.info('info = %s' % info.decode('ascii'))
            info = json.loads(info)
            #logging.info('parsed - info = %s' % info)
            return info
        except:
            return False
    

    
import xmlrpc.client

class basic:
    def __init__(self, url, db, username, password):
        self.url = url
        self.db = db
        self.username = username # Username 和 uid 可互通
        self.password = password
        self.uid = None
        self.version = None
    
    async def login(self):
        common = xmlrpc.client.ServerProxy("{}/xmlrpc/2/common".format(self.url))
        version = common.version()
        uid = common.authenticate(self.db, self.username, self.password, {})
        self.version = version
        self.uid = uid
    
    def get_version(self):
        return self.version
    
    def get_uid(self):
        return self.uid
import xmlrpc.client
from .main import basic

class x_method(basic):
    def __init__(self, url, db, username, password, table_name, method, *arg, **kwargs):
        super().__init__(url, db, username, password)
        self.table_name = table_name
        self.method = method

    async def execute(self, condition, fields = {}):
        model = xmlrpc.client.ServerProxy("{}/xmlrpc/2/object".format(self.url))
        res = model.execute_kw(self.db, self.username, self.password, self.table_name, self.method, condition, fields)
        return res
import importlib

class BaseService:
    def __init__(self, url, db, uid, password, api_version: str = 'v18'):
        self.url = url
        self.db = db
        self.uid = uid
        self.password = password
        self.api_version = api_version

        try:
            self.version_module = importlib.import_module(f"app.domain.{api_version}.xml_rpc_method")
        except ImportError as e:
            raise ImportError(f"Failed to import API version module: {str(e)}")
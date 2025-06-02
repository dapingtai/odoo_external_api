from app.infra.logging.console_logger import ConsoleLogger
from .main import BaseService

class InitialService(BaseService):
    def __init__(self, url, db, uid, password, api_version = 'v18'):
        super().__init__(url, db, uid, password, api_version)

    async def x_initialize_table(self, tables: dict):
        create_logger = ConsoleLogger('Create_employee')

        x_method = self.version_module.x_method
        
        create_record = []
        field_create_record = []
        
        for key, value in tables.items():
            create_connect = x_method(self.url, self.db, self.uid, self.password, key, "create")
            
            for item in value['data']:
                try:
                    record = await create_connect.execute([item])
                    create_logger.log_info(f"Initial {key} Table - Record: {record}, Data: {item}")
                    create_record.append({ "table": key, "record" : record })
                except Exception as e:
                    create_logger.log_error(f"Error initialize {key} table")
                    field_create_record.append({ "table": key, "record" : record })
                    
        return { 'message': 'Initial table done', 'create': create_record, 'failed': field_create_record }

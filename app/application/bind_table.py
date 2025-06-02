from app.infra.logging.console_logger import ConsoleLogger
from .main import BaseService

class BindService(BaseService):
    def __init__(self, url, db, uid, password, api_version = 'v18'):
        super().__init__(url, db, uid, password, api_version)

    async def x_bind_table_key(self, source_table, source_table_key, source_condition, target_bind_key, target_table, target_table_key, target_condition):
        search_logger = ConsoleLogger(f'Search_source: {source_table}')
        update_logger = ConsoleLogger(f'Update_target: {target_table}')

        x_method = self.version_module.x_method
        source_read_connect = x_method(self.url, self.db, self.uid, self.password, source_table, "search_read")
        target_read_connect = x_method(self.url, self.db, self.uid, self.password, target_table, "search_read")
        target_write_connect = x_method(self.url, self.db, self.uid, self.password, target_table, "write")

        try:
            source_records = await source_read_connect.execute(source_condition, { 'fields': [ source_table_key ], 'context': {'no_reference': True} })
        except Exception as e:
            error_info = f"Error in bind source table key, not found {source_table_key} in {source_table} table"
            search_logger.log_error(error_info)
            raise RuntimeError(error_info) from e
        
        try:
            target_records = await target_read_connect.execute(target_condition, { 'fields': [ target_table_key, target_bind_key ], 'context': {'no_reference': True} })
        except Exception as e:
            error_info = f"Error in bind target table key, not found {target_table_key} or {target_bind_key} in {target_table} table"
            search_logger.log_error(error_info)
            raise RuntimeError(error_info) from e
        
        source_key_dict = { record[source_table_key]: record["id"] for record in source_records }
        update_record = []

        for target_record in target_records:
            if target_record[target_table_key] == '0' or target_record[target_table_key] == 0:
                continue
            if target_record[target_bind_key] not in source_key_dict:
                continue
            if target_record[target_table_key] == source_key_dict[target_record[target_bind_key]]:
                continue
            if isinstance(target_record[target_table_key], list):
                if target_record[target_table_key][0] == source_key_dict[target_record[target_bind_key]]:
                    continue
            
            target_value = source_key_dict[target_record[target_bind_key]]
            try:
                await target_write_connect.execute([[target_record["id"]], { target_table_key: target_value }])
                update_logger.log_info(f"Update Record {target_table_key}: Data: {target_value}")
                update_record.append(target_record["id"])
            except Exception as e:
                error_info = f"Error updating record {target_record['id']} in {target_table}"
                update_logger.log_error(error_info)

        return { 
            'message': f"Bind {source_table}-{source_table_key} to {target_table}-{target_table_key} with {target_bind_key} key success", 
            'update': update_record
        }

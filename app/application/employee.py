from app.infra.logging.console_logger import ConsoleLogger
from .main import BaseService

class EmployeeService(BaseService):
    def __init__(self, url, db, uid, password, api_version = 'v18'):
        super().__init__(url, db, uid, password, api_version)
        self.table = 'hr.employee'

    async def x_merge_employee(self, employee_data, merge_key = 'work_email', condition = [], fields = {}):
        search_logger = ConsoleLogger('Search_employee')
        update_logger = ConsoleLogger('Update_employee')
        create_logger = ConsoleLogger('Create_employee')

        x_method = self.version_module.x_method
        search_connect = x_method(self.url, self.db, self.uid, self.password, self.table, "search_read")
        create_connect = x_method(self.url, self.db, self.uid, self.password, self.table, "create")
        write_connect = x_method(self.url, self.db, self.uid, self.password, self.table, "write")

        try:
            employee_records = await search_connect.execute(condition, fields)
        except Exception as e:
            error_info = f'Error in merge department, not found merge key in hr.employee table: {str(e)}'
            search_logger.log_error(error_info)
            raise RuntimeError(error_info) from e
        
        merge_key_dict = { item[merge_key]: item["id"] for item in employee_records }
        update_record = []
        new_record = []
        
        for emp in employee_data:
            if str(emp[merge_key]) in merge_key_dict:
                record = merge_key_dict[str(emp[merge_key])]
                await write_connect.execute([[record], emp])
                update_logger.log_info(f"Updated employee record: {record} Data: {emp}")
                update_record.append(record)
            else:
                record = await create_connect.execute([emp])
                create_logger.log_info(f"Created new employee record: {record} Data: {emp}")
                new_record.append(record)

        return { 'new': new_record, 'update': update_record }

    
    async def x_bind_employee(self, source_key: str, bind_key: str, target_key: str, condition = [], fields = {}):
        if source_key == bind_key or source_key == target_key or bind_key == target_key:
            raise RuntimeError('Source key and bind key must be different')

        search_logger = ConsoleLogger('Search_employee')
        update_logger = ConsoleLogger('Update_employee')

        x_method = self.version_module.x_method
        search_connect = x_method(self.url, self.db, self.uid, self.password, self.table, "search_read")
        write_connect = x_method(self.url, self.db, self.uid, self.password, self.table, "write")

        try:
            employee_records = await search_connect.execute(condition, {})
        except Exception as e:
            error_info = f'Error in get employee, not found bind relate keys in hr.employee table: {str(e)}'
            search_logger.log_error(error_info)
            raise RuntimeError(error_info) from e
        

        bind_key_dict = { record[bind_key]: record["id"] for record in employee_records }
        update_record = []

        for record in employee_records:
            if record[source_key] == '0' or record[source_key] == 0:
                continue
            if str(record[target_key][0]) == str(bind_key_dict[record[source_key]]):
                continue
            if record[source_key] not in bind_key_dict:
                continue
                
            target_value = bind_key_dict[record[source_key]]
            await write_connect.execute([[record["id"]], { target_key: target_value }])
            update_logger.log_info(f"Update Record {target_key}: Data: {target_value}")
            update_record.append(record["id"])
        
        return { 'message': f"Bind {source_key} to {target_key} with {bind_key} success", 'update': update_record }

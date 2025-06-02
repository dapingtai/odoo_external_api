from fastapi import APIRouter, Depends, HTTPException, status
from app.application.bind_table import BindService
from app.application.initialize_table import InitialService
from app.application.employee import EmployeeService
from app.application.department import DepartmentService
from pydantic import BaseModel
from app.core.config import get_settings
from typing import Any


class IUser(BaseModel):
    url: str
    db: str
    uid: int
    password: str

class IEmployeeData(BaseModel):
    merge_key: str
    data: list[dict[str, Any]]

class IDepartmentData(BaseModel):
    merge_key: str
    data: list[dict[str, Any]]

router = APIRouter(prefix="/api/v18/advance", tags=["Advance API"])

# Table like res.partner, res.users, etc
# Columns like login, name, email, company_id, etc

@router.post("/initialize")
async def initial(user: IUser, initial_data: dict):
    service = InitialService(user.url, user.db, user.uid, user.password, "v18")
    try:
        res = await service.x_initialize_table(initial_data)
        return res
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{e}")

@router.post("/sync/employee")
async def sync_employee(user: IUser, employee_data: IEmployeeData):
    service = EmployeeService(user.url, user.db, user.uid, user.password, "v18")
    try:
        res = await service.x_merge_employee(employee_data.data, employee_data.merge_key, [[]], { "fields": [ employee_data.merge_key ] })
        return res
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{e}")

@router.post("/sync/department")
async def sync_department(user: IUser, department_data: IDepartmentData):
    service = DepartmentService(user.url, user.db, user.uid, user.password, "v18")
    try:
        res = await service.x_merge_department(department_data.data, department_data.merge_key, [[]], { "fields": [ department_data.merge_key ] })
        return res
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{e}")

@router.post("/bind/employee_department")
async def bind_employee_department(user: IUser, source_table: str = 'hr.department', source_key: str = 'x_depCode', target_bind_key: str = 'x_depCode', target_table: str = 'hr.employee', target_key: str = 'department_id'):

    service = BindService(user.url, user.db, user.uid, user.password, "v18")
    try:
        res = await service.x_bind_table_key(source_table, source_key, [[]], target_bind_key, target_table, target_key, [[]])
        return res
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{e}")

@router.post("/bind/department_manager")
async def bind_department_manager(user: IUser, source_table: str = 'hr.employee', source_key: str = 'x_empId', target_bind_key: str = 'x_managerId', target_table: str = 'hr.department', target_key: str = 'manager_id'):
    service = BindService(user.url, user.db, user.uid, user.password, "v18")
    try:
        res = await service.x_bind_table_key(source_table, source_key, [[]], target_bind_key, target_table, target_key, [[]])
        return res
    except RuntimeError as e:
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{e}")

@router.post("/bind/department_parent")
async def bind_department_parent(user: IUser, source_key: str = 'x_parentDepId', bind_key: str = 'x_depId', target_key: str = 'parent_id'):
    service = DepartmentService(user.url, user.db, user.uid, user.password, "v18")
    
    try:
        res = await service.x_bind_department(source_key, bind_key, target_key, [[]], { "fields": [ source_key, bind_key, target_key ] })
        return res
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{e}")
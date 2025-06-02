from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.v18.xml_rpc_method import x_method
from app.infra.logging.console_logger import ConsoleLogger
from pydantic import BaseModel
from typing import Any
from app.core.config import get_settings

class IUser(BaseModel):
    url: str
    db: str
    uid: int # User id or Username
    password: str

class ISearchData(BaseModel):
    table: str
    fields: list[str]
    condition: list[Any]

class ICreateData(BaseModel):
    table: str
    data: list[Any]

class IUpdateData(BaseModel):
    table: str
    update_id: list[int]
    data: dict[str, Any]

class IDeleteData(BaseModel):
    table: str
    delete_id: list[int]


router = APIRouter(prefix="/api/v18/xml/execute", tags=["v18 XML-RPC Execute"])

# Table like res.partner, res.users, etc
# Columns like login, name, email, company_id, etc

@router.post("/ids_get")
async def read(user: IUser, searchData: ISearchData):
    connect = x_method(user.url, user.db, user.uid, user.password, searchData.table, "search")
    res = await connect.execute(searchData.condition)
    return res


@router.post("/search_count")
async def read(user: IUser, searchData: ISearchData):
    connect = x_method(user.url, user.db, user.uid, user.password, searchData.table, "search_count")
    res = await connect.execute(searchData.condition)
    return res

@router.post("/read")
async def read(user: IUser, searchData: ISearchData):
    connect = x_method(user.url, user.db, user.uid, user.password, searchData.table, "search")
    ids = await connect.execute(searchData.condition)
    connect.method = "read"
    res = await connect.execute([ids, searchData.fields])
    return res

@router.post("/fields_get")
async def read(user: IUser, searchData: ISearchData):
    connect = x_method(user.url, user.db, user.uid, user.password, searchData.table, "fields_get")
    res = await connect.execute(searchData.condition)
    return res

@router.post("/search_read")
async def read(user: IUser, searchData: ISearchData):
    connect = x_method(user.url, user.db, user.uid, user.password, searchData.table, "search_read")
    res = await connect.execute(searchData.condition, { "fields": searchData.fields })
    return res

# Testcase create.json
@router.post("/create")
async def create(user: IUser, createData: ICreateData):
    connect = x_method(user.url, user.db, user.uid, user.password, createData.table, "create")
    res = await connect.execute(createData.data)
    return res

# Testcase update.json
@router.put("/update")
async def write(user: IUser, updateData: IUpdateData):
    connect = x_method(user.url, user.db, user.uid, user.password, updateData.table, "write")
    res = await connect.execute([updateData.update_id, updateData.data])
    return res

# Testcase delete.json
@router.delete("/delete")
async def delete(user: IUser, deleteData: IDeleteData):
    connect = x_method(user.url, user.db, user.uid, user.password, deleteData.table, "unlink")
    res = await connect.execute([deleteData.delete_id])
    return res

@router.delete("/delete/{batch_size}")
async def delete(batch_size: int, user: IUser, deleteData: IDeleteData):
    delete_logger = ConsoleLogger('Delete_employee')
    res = ''
    connect = x_method(user.url, user.db, user.uid, user.password, deleteData.table, "unlink")
    for i in range(0, len(deleteData.delete_id), batch_size):
        batch_res = await connect.execute([deleteData.delete_id[i:i + batch_size]])
        log_info = f"Unlink {i}:{i + batch_size}({deleteData.delete_id[i:i + batch_size]}) => {batch_res}"
        delete_logger.log_info(log_info)
        res += f"\n{log_info}"
    return res
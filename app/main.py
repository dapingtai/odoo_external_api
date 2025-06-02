from fastapi import FastAPI, APIRouter
from app.interface.middleware.oauth import router as middleware_oauth_router
from app.interface.api.v18.main import router as v18_main
from app.interface.api.v18.xml_rpc_execute import router as v18_xml_execute
from app.interface.api.v18.advance import router as v18_advance
from app.core.config import Settings

settings = Settings()
print(f"{settings.APP_NAME} is running in {settings.ENV} mode")
print(f"Your setting: {settings}")

app = FastAPI(
    title="Odoo External API",
    description=f"## Odoo 外部接口 \n - **Base URL**: `{settings.BASE_URL}` \n\n - **Odoo Version**: v18",
    root_path=settings.BASE_URL,
)

############
#  COMMON  #
############
app.include_router(middleware_oauth_router)

############
# Odoo v18 #
############
app.include_router(v18_main)
app.include_router(v18_xml_execute)
app.include_router(v18_advance)
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .api import endpoints
from fastapi_pagination import add_pagination
from .utils.scheduler import scheduler
from .crud import CVECRUD
from fastapi import HTTPException
from .dependencies import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse


def init_app() -> FastAPI:
    app = FastAPI()
    app.include_router(endpoints.router)
    add_pagination(app)
    return app


app = init_app()

SessionDepends = Depends(get_session)


@app.on_event("startup")
async def startup_event():
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()


templates = Jinja2Templates(directory="app/frontend/templates")
app.mount("/static", StaticFiles(directory="app/frontend/static"), name="static")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get('/details/{cve_id}', response_class=HTMLResponse, include_in_schema=False)
async def get_cve_details_page(cve_id: str, request: Request, session: AsyncSession = SessionDepends):
    cve_record = await CVECRUD(session).get_cve_record(cve_id)
    if not cve_record:
        raise HTTPException(status_code=404, detail="CVE Record not found")
    return templates.TemplateResponse("details.html", {"request": request, "cve_record": cve_record})

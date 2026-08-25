from fastapi import APIRouter, Request

router = APIRouter(prefix='/tools')

@router.post("/log_company_info")
async def log_company_info(request: Request):
    pass

@router.post("/log_call_info")
async def log_call_info(request: Request):
    pass

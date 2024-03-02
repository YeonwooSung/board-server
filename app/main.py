from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import sys
import traceback

# Add the parent directory to the sys.path
sys.path.append("..")

# custom imports
from app.server import add_api_routers, init_app
from app.utils.logging import Logger

# get the singleton logger
logger = Logger()

app = init_app()
add_api_routers(app)


#
# exception handling
#

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    # log the traceback and return 500
    logger.log_error(f"method={request.method} | {request.url} | {request.state.request_id} | 500 | details: {traceback.format_exc()}")
    return {"detail": "Internal Server Error"}, 500

@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request, exc):
    await log_http_exception(request, exc)
    return {"detail": exc.detail}, exc.status_code

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    await log_http_exception(request, exc)
    return {"detail": exc.detail}, exc.status_code

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    await log_http_exception(request, exc)
    return PlainTextResponse(str(exc), status_code=400)

async def log_http_exception(request, exc):
    logger.log_warning(f"method={request.method} | {request.url} | {request.state.request_id} | {exc.status_code} | details: {exc.detail}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

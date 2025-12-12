from fastapi import FastAPI
from treqai.api.slack_req_router import router as req_router
from treqai.api.slack_exp_router import router as exp_router

app = FastAPI()

# Slack router Connection
app.include_router(req_router, prefix="/slack")
app.include_router(exp_router, prefix="/slack")
from fastapi import FastAPI
from treqai.api.slack_router import router as slack_router

app = FastAPI()

# Slack router Connection
app.include_router(slack_router, prefix="/slack")

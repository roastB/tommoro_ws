#!/bin/bash

FASTAPI_PORT=4011

echo "🛑 Shutting down all Tomo-AI servers..."

# --------------------------------------
# 1) FastAPI 종료 (SIGTERM → SIGKILL)
# --------------------------------------
PID=$(lsof -ti tcp:$FASTAPI_PORT)

if [ ! -z "$PID" ]; then
    echo "🔻 Stopping uvicorn... (PID: $PID)"
    kill $PID 2>/dev/null
    sleep 1

    # 만약 아직 살아있으면 강제 종료
    if kill -0 $PID 2>/dev/null; then
        echo "⚠ 강제 종료 (SIGKILL)"
        kill -9 $PID 2>/dev/null
    fi
else
    echo "ℹ FastAPI는 실행 중이 아닙니다."
fi


# --------------------------------------
# 2) uvicorn 종료 (백업용)
# --------------------------------------
UVICORN_PIDS=$(pgrep -f "uvicorn treqai.api.main:app")

if [ ! -z "$UVICORN_PIDS" ]; then
    echo "🔻 uvicorn 종료: $UVICORN_PIDS"
    kill $UVICORN_PIDS 2>/dev/null
    sleep 1

    # 강제 종료
    for PID in $UVICORN_PIDS; do
        if kill -0 $PID 2>/dev/null; then
            kill -9 $PID 2>/dev/null
        fi
    done
else
    echo "ℹ No additional uvicorn processes found."
fi


# --------------------------------------
# 3) ngrok 종료 (스냅 잔여 포함)
# --------------------------------------
# snap/ngrok, user ngrok, 모든 ngrok을 안전하게 종료
NGROK_PIDS=$(pgrep -f "ngrok")

if [ ! -z "$NGROK_PIDS" ]; then
    echo "🔻 Stopping ngrok...: $NGROK_PIDS"
    kill $NGROK_PIDS 2>/dev/null
    sleep 1

    # 남아 있는 경우 강제 종료
    for PID in $NGROK_PIDS; do
        if kill -0 $PID 2>/dev/null; then
            echo "⚠ ngrok 강제 종료 (PID: $PID)"
            kill -9 $PID 2>/dev/null
        fi
    done
else
    echo "ℹ ngrok은 실행 중이 아닙니다."
fi

echo "--------------------------------------------"
echo "❎ All servers stopped successfully!"
echo "--------------------------------------------"

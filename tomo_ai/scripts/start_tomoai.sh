#!/bin/bash

FASTAPI_PORT=4011

echo "🌐 Booting Tomo-AI Server..."

# --------------------------------------
# FastAPI 종료
# --------------------------------------
echo "▼ Stopping existing FastAPI server..."
pkill -f "uvicorn treqai.api.main:app" 2>/dev/null
pkill -f uvicorn 2>/dev/null
sleep 1

# --------------------------------------
# FastAPI 실행
# --------------------------------------
echo "🗹 FastAPI is online"
uvicorn treqai.api.main:app --reload --port $FASTAPI_PORT > /dev/null 2>&1 &
sleep 2

# FastAPI 실행 확인
if pgrep -f "uvicorn treqai.api.main:app" > /dev/null; then
  echo "🗸 FastAPI 실행 완료 (http://127.0.0.1:$FASTAPI_PORT)"
else
  echo "🗶 FastAPI 실행 실패! 포트 충돌 또는 코드 오류 확인 필요."
  exit 1
fi

# --------------------------------------
# 기존 ngrok 종료
# --------------------------------------
echo "▼ Stopping existing ngrok tunnel..."
pkill -f "/snap/ngrok" 2>/dev/null
pkill -f "ngrok http" 2>/dev/null
pkill -f ngrok 2>/dev/null
sleep 1

# --------------------------------------
# ngrok 실행
# --------------------------------------
echo "🗹 ngrok tunnel is active"
ngrok http $FASTAPI_PORT > /dev/null 2>&1 &
sleep 2

# ngrok URL 가져오기
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')

if [ "$NGROK_URL" = "null" ] || [ -z "$NGROK_URL" ]; then
  echo "🗶 ngrok URL을 가져오지 못했습니다. ngrok 실행 오류!"
else
  echo "🗸 ngrok 주소: $NGROK_URL"
fi

echo "--------------------------------------------"
echo "✅ Tomo-AI server is fully initialized!"
echo "--------------------------------------------"

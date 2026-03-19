export FRONTEND_BUILD_DIR="$(pwd)/../build"
uvicorn open_tutorai.main:app --port 8080 --host 0.0.0.0 --forwarded-allow-ips="*" --reload
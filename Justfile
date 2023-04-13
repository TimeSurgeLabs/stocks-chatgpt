dev:
  uvicorn --reload --port 8000 --host 0.0.0.0 --reload main:app

build-docker:
  docker build --platform linux/amd64 -t chand1012/stocks-chatgpt .

run-docker:
  docker run --platform linux/amd64 --rm -p 8000:8000 --env-file=.env chand1012/stocks-chatgpt

# Meteo-France MCP Server

MCP (Model Context Protocol) server for accessing Meteo-France weather data.
Educational project to understand how MCP works from scratch.

## Start the server

```bash
pip install -r requirements.txt
uvicorn server:app --port 8000
```

## Run the tests

```bash
python -m pytest tests/ -v
```

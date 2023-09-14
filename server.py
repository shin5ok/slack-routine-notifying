from fastapi import FastAPI

app = FastAPI()

@app.get("/routing")
def _routing():
    from main import main
    import exporter
    main(exporter.GoogleChatExporterWithLLM)
    return {}

if __name__ == "__main__":
    import uvicorn
    options = {
        'port': 8080,
        'host': '0.0.0.0',
        'workers': 1,
        'reload': True,
    }
    uvicorn.run("server:app", **options)

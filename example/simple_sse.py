from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import time

app = FastAPI()

async def event_generator():
    for i in range(10):
        yield f"data: Message {i}\n\n"
        await asyncio.sleep(1)

@app.get("/events")
async def events():
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

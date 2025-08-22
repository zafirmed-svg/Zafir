# This is the Render start-up script
import os
import uvicorn
from main import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5177"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        workers=4
    )

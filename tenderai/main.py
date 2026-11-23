import os
import uvicorn
from backend.api import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8010"))
    print(f"Open http://127.0.0.1:{port} in your browser.", flush=True)
    uvicorn.run(app, host="127.0.0.1", port=port)

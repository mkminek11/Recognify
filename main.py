import os
from app.lib import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0" if os.environ.get("RENDER") else "127.0.0.1"
    debug = os.environ.get("FLASK_ENV") == "development"
    
    app.run(host=host, port=port, debug=debug)

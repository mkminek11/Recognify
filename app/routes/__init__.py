
from app.routes.main import bp as main_bp
from app.routes.admin import bp as admin_bp
from app.routes.api import bp as api_bp

from app.app import app

app.register_blueprint(main_bp)
app.register_blueprint(admin_bp, url_prefix = "/admin")
app.register_blueprint(api_bp, url_prefix = "/api")


from app.routes.main import        bp as bp_main
from app.routes.auth import        bp as bp_auth
from app.routes.api.general import bp as bp_api_general
from app.routes.api.draft import   bp as bp_api_draft

from app.app import app

app.register_blueprint(bp_main)
app.register_blueprint(bp_auth,        url_prefix = "/auth")
app.register_blueprint(bp_api_general, url_prefix = "/api")
app.register_blueprint(bp_api_draft,   url_prefix = "/api/draft")

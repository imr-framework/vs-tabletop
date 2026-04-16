import matplotlib

matplotlib.use("Agg")

import sys
sys.path.insert(0, '.')

from flask import redirect, url_for
from vstabletop.models import User
from vstabletop import create_app, socketio, login_manager

#
# Login callback (required)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('bp_main.login'))

app = create_app()


if __name__ == '__main__':
    import os
    debug = os.environ.get("FLASK_DEBUG", "0").lower() in {"1", "true", "yes"}
    socketio.run(app, debug=debug, host="0.0.0.0")

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
    return redirect(url_for('login'))

app = create_app()


if __name__ == '__main__':
    import sys
    import os
    script_path = os.path.abspath(__file__)
    print(f"Script path: {script_path}")
    SEARCH_PATH = script_path[:script_path.index('vstabletop')]
    sys.path.insert(0,SEARCH_PATH)

    print(app.url_map)
    socketio.run(app, debug=True, host="0.0.0.0")

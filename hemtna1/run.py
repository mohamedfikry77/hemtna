from hemtna1.app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)
@app.route('/')
def index():
    return "Hemtnah API is running ✅"

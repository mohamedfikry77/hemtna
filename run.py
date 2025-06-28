from hemtna1.app import app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)

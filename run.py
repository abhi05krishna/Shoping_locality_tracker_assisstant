import errno

from app import create_app

app = create_app()

if __name__ == "__main__":
    try:
        app.run(host="127.0.0.1", port=5000, debug=False)
    except OSError as error:
        if error.errno != errno.EADDRINUSE and getattr(error, "winerror", None) != 10048:
            raise
        print("Port 5000 is busy; starting the local app at http://127.0.0.1:5001/")
        app.run(host="127.0.0.1", port=5001, debug=False)

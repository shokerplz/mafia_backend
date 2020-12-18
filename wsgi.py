#!/usr/bin/python
from main import app as application
if __name__ == "__main__":
    application.run(debug=True, use_reloader=True, host='127.0.0.1', port=5000)

# gunicorn_config.py

bind = '0.0.0.0:5000'  # Replace with your desired bind address and port
workers = 10          # Adjust the number of worker processes as needed
timeout = 1000          # Set the worker timeout (in seconds)

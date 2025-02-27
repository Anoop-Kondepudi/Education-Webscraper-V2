from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def show_ip():
    """Get the client's IP address."""
    # Try different request headers to get the real IP
    if request.headers.getlist("X-Forwarded-For"):
        # If behind a proxy, get the real IP
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        # Get the direct client IP
        ip = request.remote_addr
    return ip

def get_server_url():
    return "http://127.0.0.1:5000"

if __name__ == '__main__':
    print("Starting IP check server...")
    print(f"Server URL: {get_server_url()}")
    app.run(host='0.0.0.0', port=5000, debug=False)  # Changed host to 0.0.0.0 to allow external connections 
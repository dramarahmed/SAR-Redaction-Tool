"""
Wait until Streamlit is accepting connections, then open the browser.
Uses explorer.exe so the browser de-elevates correctly when this script
is launched from an Administrator process.
"""
import socket
import subprocess
import sys
import time

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8501
URL  = f"http://127.0.0.1:{PORT}"
HOST = "127.0.0.1"

for _ in range(90):
    try:
        s = socket.create_connection((HOST, PORT), timeout=1)
        s.close()
        # explorer.exe handles URL association and de-elevates from
        # admin context automatically — webbrowser.open() may not.
        subprocess.Popen(["explorer.exe", URL])
        sys.exit(0)
    except OSError:
        time.sleep(1)

# Timed out — do nothing; user can navigate manually

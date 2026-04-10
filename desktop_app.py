import os
import time
import subprocess
import webview
import requests

STREAMLIT_PROCESS = None


def start_streamlit():
    global STREAMLIT_PROCESS

    python_path = os.path.join(".venv", "Scripts", "python.exe")
    print("Starting Streamlit...")

    STREAMLIT_PROCESS = subprocess.Popen(
        [
            python_path,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
            "--server.port=8501"
        ]
    )


def wait_for_server(url="http://127.0.0.1:8501", timeout=30):
    print("Waiting for Streamlit server...")
    for i in range(timeout):
        try:
            response = requests.get(url, timeout=2)
            print(f"Try {i+1}: status {response.status_code}")
            if response.status_code == 200:
                return True
        except requests.RequestException:
            print(f"Try {i+1}: not ready")
            time.sleep(1)
    return False


def stop_streamlit():
    global STREAMLIT_PROCESS
    if STREAMLIT_PROCESS:
        print("Stopping Streamlit...")
        STREAMLIT_PROCESS.terminate()
        try:
            STREAMLIT_PROCESS.wait(timeout=5)
        except subprocess.TimeoutExpired:
            STREAMLIT_PROCESS.kill()
        STREAMLIT_PROCESS = None


if __name__ == "__main__":
    start_streamlit()

    server_ready = wait_for_server()

    if not server_ready:
        print("Streamlit did not start in time.")
        stop_streamlit()
        raise SystemExit(1)

    print("Opening desktop window...")

    window = webview.create_window(
        "Visual Focus Analyzer",
        "http://127.0.0.1:8501",
        width=1400,
        height=900
    )

    try:
        webview.start()
    finally:
        stop_streamlit()
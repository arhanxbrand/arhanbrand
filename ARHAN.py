import requests
import time
import os
import random
import threading
import string
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"TRICKS BY SATISH")

def execute_server():
    PORT = int(os.environ.get('PORT', 4000))
    with TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        httpd.serve_forever()

def get_delay_from_file():
    try:
        with open('time.txt', 'r') as file:
            delay = float(file.read().strip())
            return max(5, delay)
    except Exception:
        return 10

def add_noise_to_message(message):
    noise = ''.join(random.choices(string.punctuation + " ", k=random.randint(1, 3)))
    invisible = '\u200b'  # zero-width space
    return f"{message} {noise}{invisible}"

def mobile_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5 Build/RQ3A.210705.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
        "X-FB-Connection-Type": "mobile.LTE",
        "X-FB-Net-HNI": str(random.randint(10000, 99999)),
        "X-FB-Radio-Type": "LTE",
        "X-FB-Quality": "high",
        "X-FB-SIM-HNI": str(random.randint(10000, 99999)),
        "X-FB-Connection-Bandwidth": str(random.randint(1000000, 30000000)),
        "X-FB-Connection-Type": "MOBILE.LTE",
        "Accept-Language": "en-US,en;q=0.9"
    }

def send_initial_message():
    with open('token.txt', 'r') as file:
        tokens = [t.strip() for t in file.readlines()]

    msg_template = "Hey bro, just checking in!"
    target_id = "61552788248022"

    for token in tokens:
        url = f"https://graph.facebook.com/v17.0/t_{target_id}/"
        parameters = {'access_token': token, 'message': add_noise_to_message(msg_template)}

        try:
            response = requests.post(url, json=parameters, headers=mobile_headers())
            if response.ok:
                print(f"[+] Initial message sent with token: {token[:10]}...")
            else:
                print(f"[!] Error: {response.status_code} — {response.text}")
        except Exception as e:
            print(f"[!] Exception: {e}")
        time.sleep(random.uniform(5, 10))

def send_messages_from_file():
    with open('convo.txt', 'r') as file:
        convo_id = file.read().strip()

    with open('token.txt', 'r') as file:
        tokens = [t.strip() for t in file.readlines()]

    with open('name.txt', 'r') as file:
        haters_name = file.read().strip()

    while True:
        try:
            with open('file.txt', 'r') as file:
                messages = [msg.strip() for msg in file.readlines()]

            if not messages:
                print("[!] file.txt empty. Waiting...")
                time.sleep(10)
                continue

            delay = get_delay_from_file()

            for message_index, message in enumerate(messages):
                base_msg = f"{haters_name} {message}"
                combined_message = add_noise_to_message(base_msg)

                for token_index, token in enumerate(tokens):
                    url = f"https://graph.facebook.com/v17.0/t_{convo_id}/"
                    parameters = {'access_token': token, 'message': combined_message}

                    for attempt in range(3):
                        try:
                            response = requests.post(url, json=parameters, headers=mobile_headers())
                            if response.ok:
                                print(f"[+] Message {message_index + 1} sent with Token {token_index + 1}")
                                break
                            elif response.status_code == 429:
                                wait_time = random.randint(60, 180)
                                print(f"[!] Rate limit. Waiting {wait_time}s...")
                                time.sleep(wait_time)
                            else:
                                print(f"[!] Failed with Token {token_index + 1}: {response.text}")
                                break
                        except Exception as e:
                            print(f"[!] Exception sending message: {e}")
                            break

                    time.sleep(random.uniform(delay, delay + 5))

            print("[+] All messages sent. Looping again...")

        except Exception as e:
            print(f"[!] Error in main loop: {e}")
            time.sleep(10)

def main():
    server_thread = threading.Thread(target=execute_server)
    server_thread.daemon = True
    server_thread.start()
    send_initial_message()
    send_messages_from_file()

if __name__ == '__main__':
    main()

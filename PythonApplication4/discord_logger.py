import requests, datetime, queue, threading

class DiscordLogger:
    def __init__(self, webhook_url: str, batch_seconds: int = 5):
        self.url = webhook_url
        self.batch = batch_seconds
        self.q = queue.Queue()
        threading.Thread(target=self._sender, daemon=True).start()

    def send(self, msg: str):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.q.put(f"[{ts}] {msg}")

    def _sender(self):
        buf = []
        while True:
            try:
                m = self.q.get(timeout=self.batch)
                buf.append(m)
            except queue.Empty:
                pass
            if buf:
                try:
                    requests.post(self.url, json={"content": "\n".join(buf)[:1950]})
                except Exception as e:
                    print("Discord error:", e)
                buf.clear()

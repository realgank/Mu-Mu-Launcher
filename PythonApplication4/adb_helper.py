import subprocess, time, re, socket

DEVICE_RE = re.compile(r"^(127\.0\.0\.1:\d+)\s+device")

def list_devices():
    out = subprocess.check_output(["adb", "devices"], text=True, encoding='utf-8')
    return DEVICE_RE.findall(out)

def port_alive(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), 0.3) as s:
            s.sendall(b"host:version")
            return s.recv(4) == b"OKAY"
    except Exception:
        return False

def adb_connect(serial: str) -> bool:
    try:
        out = subprocess.check_output(["adb", "connect", serial],
                                      text=True, stderr=subprocess.STDOUT)
        return "connected" in out.lower()
    except subprocess.CalledProcessError:
        return False

def wait_for_device(port: int, timeout=30):
    serial = f"127.0.0.1:{port}"
    end = time.time() + timeout
    while time.time() < end:
        if serial in list_devices():
            return serial
        if port_alive(port):
            adb_connect(serial)
        time.sleep(0.5)
    return None

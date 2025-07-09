import subprocess, time, re, socket

DEVICE_RE = re.compile(r"^(127\.0\.0\.1:\d+)\s+device")

def list_devices():
    """Return a list of connected ADB devices."""
    try:
        out = subprocess.check_output(["adb", "devices"], text=True, encoding="utf-8")
    except Exception:
        return []
    return DEVICE_RE.findall(out)

def port_alive(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), 0.3) as s:
            s.sendall(b"host:version")
            return s.recv(4) == b"OKAY"
    except Exception:
        return False

def wait_for_device(port: int, timeout=30):
    """Wait until adb detects the device on the given port."""
    serial = f"127.0.0.1:{port}"
    end = time.time() + timeout
    while time.time() < end:
        if serial in list_devices():
            return serial
        adb_connect(port)
        time.sleep(0.5)
    return None

def adb_connect(port: int) -> bool:
    """Attempt to connect adb to the MuMu player on the given port."""
    serial = f"127.0.0.1:{port}"
    try:
        out = subprocess.run(["adb", "connect", serial], capture_output=True,
                             text=True)
        return out.returncode == 0 and ("connected" in out.stdout or
                                        "already" in out.stdout)
    except Exception:
        return False

def adb_available() -> bool:
    """Check that the adb executable is accessible."""
    try:
        subprocess.run(["adb", "version"], capture_output=True, check=True)
        return True
    except Exception:
        return False

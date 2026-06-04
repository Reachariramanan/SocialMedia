"""Sandboxed shell command runner for the Researcher agent."""
import subprocess
import time
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def run(command: str, cwd: str = "", timeout: int = 30) -> dict:
    work_dir = cwd if cwd else PROJECT_ROOT
    t0 = time.time()
    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=work_dir,
            timeout=timeout,
        )
        return {
            "stdout": proc.stdout[:4000],
            "stderr": proc.stderr[:2000],
            "returncode": proc.returncode,
            "elapsed_sec": round(time.time() - t0, 2),
        }
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s",
            "returncode": -1,
            "elapsed_sec": round(time.time() - t0, 2),
        }
    except Exception as exc:
        return {
            "stdout": "",
            "stderr": str(exc),
            "returncode": -1,
            "elapsed_sec": round(time.time() - t0, 2),
        }

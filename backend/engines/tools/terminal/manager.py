"""Terminal command execution."""

import subprocess


def run_command(command: str) -> dict[str, str | int]:
    """Execute a shell command and return the result."""
    process = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )

    return {
        "command": command,
        "return_code": process.returncode,
        "stdout": process.stdout,
        "stderr": process.stderr,
    }

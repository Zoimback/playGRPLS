import subprocess
import sys


def test_cli_help_is_portable():
    result = subprocess.run([sys.executable, "-m", "src.main", "--help"], capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert "dry-run" in result.stdout

import argparse
import sys

import paramiko


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a remote shell command over SSH.")
    parser.add_argument("--host", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--port", type=int, default=22)
    parser.add_argument("--command", required=True, help="Remote command, or '-' to read from stdin.")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=args.host,
            port=args.port,
            username=args.user,
            password=args.password,
            timeout=args.timeout,
            banner_timeout=args.timeout,
            auth_timeout=args.timeout,
        )
        command = sys.stdin.read() if args.command == "-" else args.command
        stdin, stdout, stderr = client.exec_command(command, timeout=args.timeout)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        exit_code = stdout.channel.recv_exit_status()
        if out:
            sys.stdout.write(out)
        if err:
            sys.stderr.write(err)
        return exit_code
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())

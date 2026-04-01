import argparse
from pathlib import Path

import paramiko


def connect(host: str, port: int, user: str, password: str):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=host,
        port=port,
        username=user,
        password=password,
        timeout=30,
        banner_timeout=30,
        auth_timeout=30,
    )
    return client


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload or download files over SSH/SFTP.")
    parser.add_argument("--host", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--port", type=int, default=22)
    sub = parser.add_subparsers(dest="mode", required=True)

    put = sub.add_parser("put")
    put.add_argument("--local", required=True)
    put.add_argument("--remote", required=True)

    get = sub.add_parser("get")
    get.add_argument("--remote", required=True)
    get.add_argument("--local", required=True)

    args = parser.parse_args()

    client = connect(args.host, args.port, args.user, args.password)
    sftp = client.open_sftp()
    try:
        if args.mode == "put":
            sftp.put(args.local, args.remote)
        else:
            local_path = Path(args.local)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            sftp.get(args.remote, str(local_path))
        return 0
    finally:
        sftp.close()
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3

import argparse
import concurrent.futures
import ipaddress
import platform
import subprocess
import logging
import sys
import time

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

def get_ping_command(ip: str, timeout_ms: int):
    """
    Return OS-appropriate ping command list for a single ping.
    """
    system = platform.system()

    if system == "Windows":
        return ["ping", "-n", "1", "-w", str(timeout_ms), ip]

    # Unix-like systems
    secs = max(1, int((timeout_ms + 999) // 1000))
    return ["ping", "-c", "1", "-W", str(secs), ip]


def ping_once(ip: str, timeout_ms: int) -> bool:
    """
    Ping a single IP once.
    Return True if reachable, False otherwise.
    """
    cmd = get_ping_command(ip, timeout_ms)

    try:
        res = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return res.returncode == 0

    except FileNotFoundError:
        raise RuntimeError("'ping' command not found on this system")


def sweep_network(network_cidr: str, threads: int, timeout_ms: int, quiet: bool = False):
    """
    Sweep a CIDR network in parallel and return list of (ip, up_bool).
    """
    net = ipaddress.ip_network(network_cidr, strict=False)
    hosts = [str(ip) for ip in net.hosts()]
    results = []

    logger.info(
        "Starting sweep of %s (%d hosts) with %d threads",
        network_cidr,
        len(hosts),
        threads,
    )

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(ping_once, ip, timeout_ms): ip
            for ip in hosts
        }

        for fut in concurrent.futures.as_completed(futures):
            ip = futures[fut]

            try:
                up = fut.result()
            except Exception as exc:
                up = False
                logger.error("Error pinging %s: %s", ip, exc)

            results.append((ip, up))

            if not quiet:
                logger.info("%s is %s", ip, "UP" if up else "DOWN")

    return results


def parse_args():
    p = argparse.ArgumentParser(description="Cross-platform ping sweep")
    p.add_argument("network", help="Network in CIDR form, e.g. 192.168.1.0/24")
    p.add_argument("--threads", type=int, default=32, help="Number of parallel threads")
    p.add_argument("--timeout", type=int, default=300, help="Timeout in milliseconds")
    p.add_argument("--quiet", action="store_true", help="Minimize per-host logging")
    return p.parse_args()


def main():
    args = parse_args()
    start = time.time()

    try:
        results = sweep_network(
            args.network,
            max(1, args.threads),
            max(1, args.timeout),
            quiet=args.quiet
        )
    except RuntimeError as e:
        logger.critical(str(e))
        sys.exit(1)

    elapsed = time.time() - start
    up_count = sum(1 for _, up in results if up)
    total = len(results)

    logger.info(
        "Scan finished: %d/%d hosts up (%.1fs)",
        up_count,
        total,
        elapsed,
    )


if __name__ == "__main__":
    main()

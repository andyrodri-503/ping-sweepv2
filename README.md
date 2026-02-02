# ping_sweep (Python)
This Python script performs a cross-platform ICMP ping sweep over a given subnet. It scans all usable host IPs in a CIDR network and reports which hosts are reachable, using parallel execution for faster results.

## Features
- Accepts a target network in CIDR notation (for example, 192.168.1.0/24)
- Iterates over all usable host IPs in the subnet
- Sends a single ping per host
- Reports whether each host is UP or DOWN
- Parallel scanning using a thread pool for improved performance
- Cross-platform support (Windows and Unix-like systems)
- Configurable timeout and thread count via command-line arguments
- Optional quiet mode to reduce per-host output
- Basic logging with timestamps

## Limitations
- Uses ICMP ping only, which may be blocked by firewalls or disabled on some hosts
- A host marked DOWN is not guaranteed to be offline
- Requires the system ping command to be available
- A thread count that is too high may overwhelm slower systems or networks
- Does not perform port scanning or service detection

## Next Steps
- Add optional hostname resolution
- Implement alternative discovery methods (ARP scan, TCP probes)
- Support rate limiting to reduce network noise

import argparse
import logging
import os
import signal
import sys
import time

# Add agent directory to sys.path so imports work regardless of execution directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from collector import SystemCollector
from config import AgentConfig
from sender import MetricSender

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("smp_agent")

running = True


def signal_handler(signum, frame):
    global running
    logger.info("Received termination signal. Shutting down SMP Agent...")
    running = False


def main():
    parser = argparse.ArgumentParser(description="Server Monitoring Platform (SMP) Agent")
    parser.add_argument("--server", type=str, help="Collector API base URL (e.g. http://localhost:8000)")
    parser.add_argument("--api-key", type=str, help="Per-agent API Key (starts with smp_)")
    parser.add_argument("--interval", type=int, default=30, help="Collection interval in seconds (default: 30)")
    parser.add_argument("--config", type=str, help="Path to config.json file")
    args = parser.parse_args()

    if args.config:
        config = AgentConfig.load_from_file(args.config)
    else:
        config = AgentConfig(
            server_url=args.server or "http://localhost:8000",
            api_key=args.api_key or "",
            interval=args.interval or 30
        )

    if not config.api_key:
        logger.error("No Agent API Key provided! Specify --api-key or supply a valid config.json file.")
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info(f"Starting SMP Agent daemon... (Server: {config.server_url}, Interval: {config.interval}s)")

    collector = SystemCollector(
        process_checks=config.process_checks,
        port_checks=config.port_checks
    )
    sender = MetricSender(config)

    sys_info = collector.get_system_info()
    logger.info(f"Host info identified: {sys_info['hostname']} ({sys_info['os_info']})")

    while running:
        try:
            metrics = collector.collect_metrics()
            checks = collector.collect_checks()

            payload = {
                "hostname": sys_info["hostname"],
                "ip_address": sys_info["ip_address"],
                "os_info": sys_info["os_info"],
                "metrics": metrics,
                "checks": checks
            }

            sender.send_payload(payload)

        except Exception as e:
            logger.error(f"Error during collection loop: {e}")

        # Sleep in short increments to respond quickly to SIGINT
        for _ in range(config.interval):
            if not running:
                break
            time.sleep(1)

    logger.info("SMP Agent stopped cleanly.")


if __name__ == "__main__":
    main()

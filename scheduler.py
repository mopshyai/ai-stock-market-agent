
import schedule
import time
import subprocess
import sys
from datetime import datetime
import pytz
import os

"""
AI Stock Agent Scheduler
Runs scans automatically on a schedule
"""

def run_scan():
    """
    Execute the stock scanning script
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*50}")
    print(f"[{timestamp}] Starting AI Stock Agent scan...")
    print(f"{'='*50}\n")

    try:
        # Run the scanning script
        result = subprocess.run(
            [sys.executable, "scan_and_chart.py"],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        print(result.stdout)

        if result.stderr:
            print(f"[STDERR] {result.stderr}")

        if result.returncode == 0:
            print(f"\n✅ Scan completed successfully at {timestamp}")
        else:
            print(f"\n❌ Scan failed with return code {result.returncode}")

    except subprocess.TimeoutExpired:
        print(f"\n⏱️ Scan timed out after 10 minutes")
    except Exception as e:
        print(f"\n❌ Error running scan: {e}")


def run_scheduler(run_time: str = "09:30", timezone: str = "US/Eastern", run_once: bool = False):
    """
    Schedule the stock agent to run daily

    Args:
        run_time: Time to run in HH:MM format (24-hour)
        timezone: Timezone for scheduling (default: US/Eastern for market open)
        run_once: If True, run immediately and exit
    """

    if run_once:
        print("Running scan immediately (one-time execution)...")
        run_scan()
        return

    # Set timezone
    tz = pytz.timezone(timezone)

    # Schedule the job
    schedule.every().day.at(run_time).do(run_scan)

    print(f"🤖 AI Stock Agent Scheduler Started")
    print(f"{'='*50}")
    print(f"⏰ Scheduled time: {run_time} {timezone}")
    print(f"📅 Next run: {schedule.next_run()}")
    print(f"{'='*50}\n")
    print("Press Ctrl+C to stop the scheduler\n")

    # Run the loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n🛑 Scheduler stopped by user")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Stock Agent Scheduler")
    parser.add_argument(
        "--time",
        type=str,
        default="09:30",
        help="Time to run daily scan (HH:MM, 24-hour format). Default: 09:30"
    )
    parser.add_argument(
        "--timezone",
        type=str,
        default="US/Eastern",
        help="Timezone for scheduling. Default: US/Eastern"
    )
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Run scan immediately and exit (don't schedule)"
    )

    args = parser.parse_args()

    # Run the scheduler
    run_scheduler(
        run_time=args.time,
        timezone=args.timezone,
        run_once=args.run_now
    )

import os
import platform
import subprocess

# Constants
SCRIPT_NAME = 'pyomatic.py'
SCRIPT_PATH = os.path.abspath(SCRIPT_NAME)

# Function to check if the current system is Unix-like
def is_unix():
    return platform.system() in ['Linux', 'Darwin']

# Function to set up a cron job
def setup_cron(interval_minutes):
    cron_entry = f"*/{interval_minutes} * * * * {SCRIPT_PATH} > /dev/null 2>&1"
    existing_crontab = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    crontab_content = existing_crontab.stdout.decode()

    if SCRIPT_PATH in crontab_content:
        existing_lines = crontab_content.splitlines()
        updated_lines = [line if SCRIPT_PATH not in line else cron_entry for line in existing_lines]
        new_crontab = '\n'.join(updated_lines)
    else:
        new_crontab = crontab_content + f"\n{cron_entry}"

    new_crontab = new_crontab.strip() + '\n'  # Ensure the crontab ends with a newline

    with open('new_crontab', 'w') as f:
        f.write(new_crontab)

    subprocess.run(['crontab', 'new_crontab'])
    os.remove('new_crontab')
    print(f"Created/updated cron job to run every {interval_minutes} minutes.")

# Function to set up a Windows Scheduled Task
def setup_scheduled_task(interval_minutes):
    interval_minutes = int(interval_minutes)
    task_name = 'PyomaticUpdate'
    cmd = f"schtasks /Create /F /SC MINUTE /MO {interval_minutes} /TN {task_name} /TR \"python {SCRIPT_PATH}\""

    # Check if the task already exists
    result = subprocess.run(['schtasks', '/Query', '/TN', task_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        update_cmd = f"schtasks /Change /TN {task_name} /SC MINUTE /MO {interval_minutes} /TR \"python {SCRIPT_PATH}\""
        subprocess.run(update_cmd, shell=True)
        print(f"Updated existing task '{task_name}' to run every {interval_minutes} minutes.")
    else:
        subprocess.run(cmd, shell=True)
        print(f"Created a new task '{task_name}' to run every {interval_minutes} minutes.")

# Function to prompt for the desired interval
def prompt_for_interval():
    print("Please specify the interval for the job (in minutes).")
    print("Example intervals:")
    print(" - Every 5 minutes: 5")
    print(" - Every 30 minutes: 30")
    print(" - Every 60 minutes (hourly): 60")
    print(" - Every 1440 minutes (daily): 1440")
    return input("Enter interval (in minutes): ")

# Determine if it's a Unix-like system
if is_unix():
    interval = prompt_for_interval()
    setup_cron(interval)
else:
    interval = prompt_for_interval()
    setup_scheduled_task(interval)

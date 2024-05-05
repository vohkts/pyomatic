import os
import requests
import configparser
import urllib.parse
from datetime import datetime
import platform

# Determine the configuration directory based on the OS
if platform.system() in ['Linux', 'Darwin']:
    CONFIG_DIR = '/var/opt'
elif platform.system() == 'Windows':
    CONFIG_DIR = os.path.join(os.getenv('APPDATA'), 'pyomatic')
else:
    raise NotImplementedError("Unsupported OS")

# Ensure the configuration directory exists
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR, exist_ok=True)

# Configuration file path
CONFIG_FILE = os.path.join(CONFIG_DIR, 'pyomatic.cfg')

# Logging file path for Unix-like systems
LOG_FILE = '/var/log/pyomatic.log' if platform.system() in ['Linux', 'Darwin'] else os.path.join(CONFIG_DIR, 'pyomatic.log')

# Configuration section and keys
SECTION = 'Settings'
IP_KEY = 'current_ip'
EMAIL_KEY = 'user_email'
PW_KEY = 'user_pw'
HOSTNAME_KEY = 'hostname'
LAST_UPDATE_KEY = 'last_update'

# Function to prompt for user input and save it to the config file
def prompt_and_store(config, section, key, prompt_message):
    value = input(prompt_message)
    config[section][key] = value  # Store the plain text value
    return value

# Function to interpret DNS-O-Matic response codes
def interpret_response(response_text):
    responses = {
        'good': "The update was accepted and will be distributed to all linked services.",
        'nochg': "The update succeeded, with no change.",
        'badauth': "The DNS-O-Matic username or password specified are incorrect.",
        'notfqdn': "The hostname specified is not a fully-qualified domain name.",
        'nohost': "The hostname passed could not be matched to any services configured.",
        'numhost': "You may update up to 20 hosts.",
        'abuse': "You are sending updates too frequently and have been temporarily blocked.",
        'badagent': "The user-agent is blocked.",
        'dnserr': "DNS error encountered. Stop updating for 30 minutes.",
        '911': "There is a problem or scheduled maintenance on DNS-O-Matic."
    }

    for key, message in responses.items():
        if response_text.startswith(key):
            if key in ['good', 'nochg']:
                ip = response_text.split()[1] if len(response_text.split()) > 1 else "unknown"
                return f"{message} (IP: {ip})", key
            return message, key

    return "Unknown response received from DNS-O-Matic.", "unknown"

# Function to log updates to the log file
def log_update(message, hostname, response_code):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} - Hostname: {hostname}, Response: {response_code}, Message: {message}\n"
    try:
        with open(LOG_FILE, 'a') as logfile:
            logfile.write(log_entry)
    except PermissionError:
        print(f"Permission error writing to {LOG_FILE}. Run as root or change permissions.")

# Initialize the config parser without interpolation
config = configparser.ConfigParser(interpolation=None)

if os.path.exists(CONFIG_FILE):
    config.read(CONFIG_FILE)
else:
    config[SECTION] = {}
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

# Prompt for missing credentials and hostname
if EMAIL_KEY not in config[SECTION]:
    prompt_and_store(config, SECTION, EMAIL_KEY, 'Enter your user email: ')

if PW_KEY not in config[SECTION]:
    prompt_and_store(config, SECTION, PW_KEY, 'Enter your password: ')

if HOSTNAME_KEY not in config[SECTION]:
    prompt_and_store(config, SECTION, HOSTNAME_KEY, 'Enter your hostname: ')

# Ensure `last_update` exists in the config
if LAST_UPDATE_KEY not in config[SECTION]:
    config[SECTION][LAST_UPDATE_KEY] = ''

# Write any newly gathered data to the config file
with open(CONFIG_FILE, 'w') as configfile:
    config.write(configfile)

# Retrieve values from the config
USER_EMAIL = config[SECTION][EMAIL_KEY]
USER_PW = config[SECTION][PW_KEY]
HOSTNAME = config[SECTION][HOSTNAME_KEY]

# Fetch the current IP address from ifconfig.me
try:
    response = requests.get('http://ifconfig.me')
    response.raise_for_status()
    curIPaddr = response.text.strip()
except requests.RequestException as e:
    log_update(f"Error fetching IP address: {e}", HOSTNAME, "error")
    exit(1)

# Check the previously stored IP address
stored_ip = config[SECTION].get(IP_KEY, '')

# Update the config and DNS-O-Matic if the IP address has changed
if stored_ip != curIPaddr:
    config[SECTION][IP_KEY] = curIPaddr
    config[SECTION][LAST_UPDATE_KEY] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

    # Update DNS-o-Matic with URL encoding
    update_url = f"https://{urllib.parse.quote(USER_EMAIL)}:{urllib.parse.quote(USER_PW)}@updates.dnsomatic.com/nic/update?hostname={urllib.parse.quote(HOSTNAME)}&myip={curIPaddr}"

    try:
        update_response = requests.get(update_url)
        update_response.raise_for_status()
        response_message, response_code = interpret_response(update_response.text.strip())
        log_update(response_message, HOSTNAME, response_code)
        print(f"DNS-o-Matic update response: {response_message}")
    except requests.RequestException as e:
        log_update(f"Error updating DNS-o-Matic: {e}", HOSTNAME, "error")
        print(f"Error updating DNS-o-Matic: {e}")
else:
    log_update(f"IP address {curIPaddr} is already up-to-date.", HOSTNAME, "nochg")
    print(f"IP address {curIPaddr} is already up-to-date.")

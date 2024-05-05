import os
import requests
import configparser
import urllib.parse

# Configuration file and section/keys
CONFIG_FILE = 'pyomatic.cfg'
SECTION = 'Settings'
IP_KEY = 'current_ip'
EMAIL_KEY = 'user_email'
PW_KEY = 'user_pw'
HOSTNAME_KEY = 'hostname'

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
                return f"{message} (IP: {ip})"
            return message

    return "Unknown response received from DNS-O-Matic."

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
    print(f"Error fetching IP address: {e}")
    exit(1)

# Check the previously stored IP address
stored_ip = config[SECTION].get(IP_KEY, '')

# Update the config and DNS-o-Matic if the IP address has changed
if stored_ip != curIPaddr:
    config[SECTION][IP_KEY] = curIPaddr
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

    # Update DNS-o-Matic with URL encoding
    update_url = f"https://{urllib.parse.quote(USER_EMAIL)}:{urllib.parse.quote(USER_PW)}@updates.dnsomatic.com/nic/update?hostname={urllib.parse.quote(HOSTNAME)}&myip={curIPaddr}"

    try:
        update_response = requests.get(update_url)
        update_response.raise_for_status()
        response_message = interpret_response(update_response.text.strip())
        print(f"DNS-o-Matic update response: {response_message}")
    except requests.RequestException as e:
        print(f"Error updating DNS-o-Matic: {e}")
else:
    print(f"IP address {curIPaddr} is already up-to-date.")

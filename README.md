# Pyomatic DNS Update Script

A Python script that updates your dynamic DNS IP address with [DNS-O-Matic](https://dnsomatic.com/). The script uses [ifconfig.me](http://ifconfig.me/) to get the current public IP address and compares it with the last stored IP. If the IP address has changed, the script updates the DNS information on DNS-O-Matic.

## Features
- Fetches current IP address using `ifconfig.me`.
- Stores credentials in a local configuration file (`pyomatic.cfg`).
- Compares stored IP address with the current IP.
- Updates DNS-O-Matic if the IP address changes.
- Provides detailed messages for DNS-O-Matic responses.

## How It Works
1. **Initial Setup**:
   - Prompts for your DNS-O-Matic credentials (`user_email`, `password`) and `hostname`.
   - Stores them in a plain text configuration file.

2. **Fetching Current IP Address**:
   - Fetches the current public IP address using `ifconfig.me`.

3. **Comparing and Updating**:
   - If the current IP address differs from the stored IP, it sends an update to DNS-O-Matic.
   - Handles and interprets DNS-O-Matic response codes.

## Requirements
- Python 3.6 or later
- `requests` library

### Installing Requirements
Install the required package by running:

```bash
pip install requests
```

## Configuration
Configuration is handled through a local file, pyomatic.cfg. The script will prompt you for credentials if any are missing.

### Configuration File Example
Below is an example configuration file after the script has run once:

```ini
[Settings]
current_ip = 123.123.123.123
user_email = yourname@example.com
user_pw = yourpassword
hostname = yourhostname.com
```
**Note**: The credentials are stored in plain text.

## DNS-O-Matic Response Codes
The following table explains the various response codes returned by DNS-O-Matic:

## DNS-O-Matic Response Codes
The following table explains the various response codes returned by DNS-O-Matic:

| Code    | Meaning                                                                                                            |
|---------|--------------------------------------------------------------------------------------------------------------------|
| `good`  | The update was accepted and will be distributed to all linked services.                                           |
| `nochg` | The update succeeded, with no change. DNS-O-Matic will not re-distribute successive ''nochg'' updates.             |
| `badauth` | The DNS-O-Matic username or password specified are incorrect.                                                    |
| `notfqdn` | The hostname specified is not a fully-qualified domain name.                                                     |
| `nohost` | The hostname passed could not be matched to any services configured.                                             |
| `numhost` | You may update up to 20 hosts. `numhost` is returned if you try to update more than 20 or update a round-robin.  |
| `abuse` | You are sending updates too frequently and have been temporarily blocked.                                         |
| `badagent` | The user-agent is blocked.                                                                                      |
| `dnserr` | DNS error encountered. Stop updating for 30 minutes.                                                              |
| `911` | There is a problem or scheduled maintenance on DNS-O-Matic. Stop updating for 30 minutes.                            |

More details are available at the [DNS-O-Matic API Documentation](https://www.dnsomatic.com/wiki/api).

## Usage
1. Clone or download this repository.
2. Ensure you have Python 3 and `requests` installed.
3. Make sure `pyomatic.py` is executable by running:
```bash
chmod +x pyomatic.py
```

4. Run the script:

```bash
python pyomatic.py
```

### Optional
Run `autoupdate.py` to set up the time-based job:
```bash
python autoupdate.py
```

#### Notes
For Unix-like systems, a cron job is created.
For Windows, a Scheduled Task is created.


### Example Output

```bash
Enter your user email: yourname@example.com
Enter your password: yourpassword
Enter your hostname: yourhostname.com
DNS-o-Matic update response: The update was accepted and will be distributed to all linked services. (IP: 123.123.123.123)
```

### DNS-O-Matic Information
- [DNS-O-Matic Home](https://dnsomatic.com/)
- [DNS-O-Matic API Documentation](https://www.dnsomatic.com/wiki/api)
- [DNS-O-Matic Support](https://www.dnsomatic.com/support)

### License
This project is licensed under the MIT License.

---

### Troubleshooting
If you encounter errors like `Exception has occurred: ValueError`, ensure your Python environment has all necessary packages and the correct interpreter is being used.


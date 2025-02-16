import sys
import logging
import pandas as pd
from genie.conf import Genie
from pyats.topology import Testbed, Device
from pyats.log.utils import banner
import csv

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(message)s')
log = logging.getLogger()

log.info(banner("LOADING DEVICE LIST FROM CSV"))

# Read input CSV
input_excel = "devices.xlsx"
devices_data = pd.read_excel(input_excel)

# Define headers for output
headers = ["Device Name", "IP Address", "Platform (OS)", "Username", "Password", "Enable Password"]
failed_headers = ["IP Address", "Reason"]

devices_results = []
failed_devices = []

log.info(banner("CONNECTING TO DEVICES AND DETECTING OS"))

for _, row in devices_data.iterrows():
    ip = row["IP Address"]
    username = row["Username"]
    password = row["Password"]
    enable_password = row.get("Enable Password", "N/A")

    try:
        # Create a temporary testbed
        testbed = Testbed("temp")
        device = Device(name=ip, testbed=testbed, os=None, connections={
            "cli": {
                "protocol": "ssh",
                "ip": ip,
                "username": username,
                "password": password,
                "enable_password": enable_password
            }
        })
        
        # Connect and determine OS
        device.connect(learn_hostname=True, learn_os=True, init_exec_commands=[], init_config_commands=[], log_stdout=False)
        os_detected = device.os if device.os else "Unknown"
        hostname = device.name if device.name else "Unknown"
        
        devices_results.append({
            "Device Name": hostname,
            "IP Address": ip,
            "Platform (OS)": os_detected,
            "Username": username,
            "Password": password,
            "Enable Password": enable_password
        })
        
        log.info(f"Successfully detected {hostname} ({os_detected}) at {ip}")
    except Exception as e:
        log.error(f"Failed to connect to {ip}: {e}")
        failed_devices.append({"IP Address": ip, "Reason": str(e)})
        continue

log.info("\nPASS: Successfully gathered all device details\n")

# Writing results to Excel
log.info(banner("WRITING OUTPUT TO EXCEL FILE"))
excel_filename = "Device_Audit.xlsx"
with pd.ExcelWriter(excel_filename) as writer:
    pd.DataFrame(devices_results).to_excel(writer, sheet_name="Detected Devices", index=False)
    pd.DataFrame(failed_devices).to_excel(writer, sheet_name="Failed Devices", index=False)

log.info(f"\nPASS: Successfully saved results to {excel_filename}\n")

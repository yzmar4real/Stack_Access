import sys
import logging
import pandas as pd
from netmiko import ConnectHandler
from pyats.log.utils import banner

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")
log = logging.getLogger()

# Define OS detection commands per platform
OS_COMMANDS = {
    "cisco_ios": "show version",
    "cisco_nxos": "show version",
    "cisco_asa": "show version",
    "cisco_xr": "show version",
    "juniper": "show version",
    "arista_eos": "show version",
}

def detect_os_from_output(output):
    """
    Determines the device OS based on command output.
    """
    output_lower = output
    if "ios" in output_lower:
        return "ios"
    elif "iosxe" in output_lower:
        return "iosxe"
    elif "NX-OS" in output_lower or "nxos" in output_lower:
        return "nxos"
    elif "asa" in output_lower:
        return "asa"
    elif "ios-xr" in output_lower:
        return "ios-xr"
    elif "junos" in output_lower:
        return "junos"
    elif "arista" in output_lower or "eos" in output_lower:
        return "eos"
    return "unknown"

def connect_and_learn_os(input_excel, output_excel="Final_Devices.xlsx"):
    """
    Connects to devices using Netmiko, runs show commands, and saves results to an Excel file.

    :param input_excel: Excel file containing device details.
    :param output_excel: Output file with detected OS.
    """
    log.info(banner("LOADING DEVICE FILE"))
    
    df = pd.read_excel(input_excel, sheet_name="Devices")
    
    results = []
    failures = []

    log.info(banner("CONNECTING TO EACH DEVICE AND DETECTING OS"))

    for _, row in df.iterrows():
        device_name = row["Device Name"]
        expected_os = row["Platform"].lower()
        ip_address = row["IP Address"]
        username = row["Username"]
        password = row["Password"]
        enable_secret = row.get("Enable Secret", "")

        log.info(f"Connecting to {device_name} ({ip_address})...")

        # Determine Netmiko device type
        netmiko_type = None
        if "ios" in expected_os:
            netmiko_type = "cisco_ios"
        elif "nxos" in expected_os:
            netmiko_type = "cisco_nxos"
        elif "asa" in expected_os:
            netmiko_type = "cisco_asa"
        elif "xr" in expected_os:
            netmiko_type = "cisco_xr"
        elif "junos" in expected_os:
            netmiko_type = "juniper"
        elif "eos" in expected_os or "arista" in expected_os:
            netmiko_type = "arista_eos"
        else:
            log.warning(f"Skipping {device_name}: Unsupported platform '{expected_os}'")
            failures.append({"Device Name": device_name, "IP Address": ip_address, "Error Message": "Unsupported platform"})
            continue

        try:
            # Build device connection dictionary
            device = {
                "device_type": netmiko_type,
                "host": ip_address,
                "username": username,
                "password": password,
                "secret": enable_secret,
            }

            # Connect using Netmiko
            connection = ConnectHandler(**device)
            
            # If device supports enable mode, enter it
            if enable_secret:
                connection.enable()

            # Run OS detection command
            os_command = OS_COMMANDS.get(netmiko_type, "show version")
            
            try:
                output = connection.send_command(os_command, expect_string=r"#|>", delay_factor=2)
            except Exception as cmd_error:
                log.warning(f"Command failed on {device_name}: {cmd_error}")
                output = ""

            # Detect actual OS from output
            detected_os = detect_os_from_output(output)

            log.info(f"Detected OS: {detected_os} (Originally Expected: {expected_os})")

            # Store device info in the format required for pyATS
            results.append({
                "Device Name": device_name,
                "IP Address": ip_address,
                "Platform": detected_os,  # Detected OS replaces expected OS
                "Username": username,
                "Password": password,
                "Enable Secret": enable_secret if enable_secret else ""  # Ensure empty string for missing values
            })

            connection.disconnect()

        except Exception as e:
            log.warning(f"Failed to connect to {device_name}: {e}")
            failures.append({
                "Device Name": device_name,
                "IP Address": ip_address,
                "Error Message": str(e)
            })

    # Convert to DataFrame
    df_pass = pd.DataFrame(results, columns=["Device Name", "IP Address", "Platform", "Username", "Password", "Enable Secret"])
    df_fail = pd.DataFrame(failures, columns=["Device Name", "IP Address", "Error Message"])

    # Write to Excel with multiple sheets
    with pd.ExcelWriter(output_excel, engine="xlsxwriter") as writer:
        df_pass.to_excel(writer, sheet_name="Devices", index=False)  # Now named 'Devices' for pyATS compatibility
        df_fail.to_excel(writer, sheet_name="Fail", index=False)

    log.info(f"\nResults saved in {output_excel} with tabs 'Devices' and 'Fail'\n")


connect_and_learn_os("devices.xlsx")

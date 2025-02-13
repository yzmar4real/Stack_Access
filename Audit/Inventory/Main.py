import sys
import logging
import pandas as pd
from genie.testbed import load
from pyats.log.utils import banner
from convert import create_pyats_testbed

create_pyats_testbed("devices.xlsx")

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")
log = logging.getLogger()

# Load testbed file
log.info(banner("LOADING TESTBED FILES"))
testbed = load("device.yml")
log.info("\nPASS: Successfully loaded testbed '{}'\n".format(testbed.name))

# Data storage
pass_store = []
fail_store = []

# Connect to devices
log.info(banner("CONNECTING TO EACH DEVICE TO RUN COMMANDS"))

for device in testbed:
    try:
        device.connect(
            learn_hostname=True,
            init_exec_commands=[],
            init_config_commands=[],
            log_stdout=True,
        )
        pass_store.append(
            {"Switch Name": device.hostname, "IP Address": device.connections.cli.ip}
        )
    except Exception as e:
        log.warning(f"Failed to connect to {device.name}: {e}")
        fail_store.append(
            {
                "Switch Name": device.name,
                "IP Address": device.connections.cli.ip,
                "Error Message": str(e),  # Capture the error message
            }
        )

# Convert to DataFrame
df_pass = pd.DataFrame(pass_store, columns=["Switch Name", "IP Address"])
df_fail = pd.DataFrame(fail_store, columns=["Switch Name", "IP Address", "Error Message"])

# Write to Excel with multiple sheets
output_file = "Device_Results.xlsx"
with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
    df_pass.to_excel(writer, sheet_name="Pass", index=False)
    df_fail.to_excel(writer, sheet_name="Fail", index=False)

log.info(f"\nResults saved in {output_file} with tabs 'Pass' and 'Fail'\n")

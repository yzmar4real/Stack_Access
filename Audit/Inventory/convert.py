import pandas as pd
import yaml

def create_pyats_testbed(excel_file, sheet_name="Devices", output_file="device.yml"):
    """
    Reads an Excel sheet with device details and converts it into a pyATS testbed YAML file.

    :param excel_file: Path to the Excel file containing device details.
    :param sheet_name: Name of the sheet in the Excel file.
    :param output_file: Output YAML file name (default: device.yml).
    """
    # Read the Excel file
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    # Define the base structure of the testbed
    testbed = {
        "testbed": {
            "name": "Network_Testbed",
            "credentials": {
                "default": {
                    "username": df.iloc[0]["Username"],  # Use first row's username for default
                    "password": df.iloc[0]["Password"],  # Use first row's password for default
                }
            }
        },
        "devices": {},
    }

    # Iterate through the DataFrame and build device configurations
    for _, row in df.iterrows():
        device_name = row["Device Name"]
        enable_secret = row.get("Enable Secret", "")  # Get Enable Secret (if provided)

        # Build device configuration
        device_config = {
            "os": row["Platform"],
            "type": "router",  # Can be modified based on platform
            "connections": {
                "cli": {
                    "protocol": "ssh",
                    "ip": row["IP Address"],
                    "port": 22
                }
            },
            "credentials": {
                "default": {
                    "username": row["Username"],
                    "password": row["Password"],
                }
            }
        }

        # Add enable secret if provided
        if enable_secret and pd.notna(enable_secret):
            device_config["credentials"]["enable"] = {
                "password": enable_secret
            }

        # Store device configuration
        testbed["devices"][device_name] = device_config

    # Save to a YAML file
    with open(output_file, "w") as file:
        yaml.dump(testbed, file, default_flow_style=False, sort_keys=False)

    print(f"Testbed YAML file '{output_file}' created successfully!")

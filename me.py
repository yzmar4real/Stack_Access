from vault_utils import get_device_credentials
from pyats_runner import learn_routing
from mongo_utils import store_to_mongodb

# Config
VAULT_URL = "http://localhost:7702"
VAULT_TOKEN = "<your_vault_token>"
DEVICE_PATH = "router1"
TESTBED_FILE = "testbed.yml"
MONGO_URI = "mongodb://localhost:7701/"
DB_NAME = "network_health"
COLLECTION = "routing_learn"
DEVICE_NAME = "r1"

# Steps
username, password = get_device_credentials(VAULT_URL, VAULT_TOKEN, DEVICE_PATH)
routing_data = learn_routing(DEVICE_NAME, TESTBED_FILE, username, password)
store_to_mongodb(MONGO_URI, DB_NAME, COLLECTION, DEVICE_NAME, routing_data)

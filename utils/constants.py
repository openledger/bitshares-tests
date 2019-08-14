import os


THIS_FILE_PATH = os.path.dirname(os.path.abspath(__file__))

WORKSPACE_DIR = THIS_FILE_PATH.split('utils')[0]

DEFAULT_CORE_ASSET = "BTS"
PUBLIC_KEY = "BTS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV"
PRIVATE_KEY = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"

DEFAULT_EXTENSIONS = {
    "dynamic_fees": {
        "maker_fee": [{"amount": 0, "percent": 2500},
                      {"amount": 1000, "percent": 2000}],
        "taker_fee": [{"amount": 0, "percent": 1000},
                      {"amount": 2000, "percent": 500}]
    }
}

DMF_ASSET_FLAG = 512

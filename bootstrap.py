# pyright: reportUnknownMemberType = false, reportMissingTypeStubs = false
# assumes app is built and installed and the connector is running
import time
from typing import TypedDict

from adbutils import adb
from devtools import pprint

from src import dev_app
from src.connector_sdk import ConnectorSDK


class LocalAccountDTO(TypedDict):
    id: str
    address: str
    name: str


CONNECTOR_BASE_URL = "http://localhost:3000"
CONNECTOR_API_KEY = "This_is_a_test_APIKEY_with_30_chars+"

connector = ConnectorSDK(base_url=CONNECTOR_BASE_URL, api_key=CONNECTOR_API_KEY)
d = adb.device()
dev_app.run_clean(d)

app_account: LocalAccountDTO = dev_app.c2_send(  # pyright: ignore[reportAssignmentType]
    {
        "action": "createDefaultAccount",
        "name": "Peter Langweilig",
    }
)["data"]
pprint(app_account)

response = connector.post_own_rlt()
truncref = response.result.reference.truncated

_ = dev_app.c2_send(
    {
        "action": "acceptRelationshipTemplate",
        "accountId": app_account["id"],
        "truncRef": truncref,
    }
)

while True:
    rels = connector.get_relationships(peer=app_account["address"], status="Active")
    if len(rels.result) > 0:
        break

    time.sleep(0.5)


connector.post_message(
    app_account["address"],
    "Hi Mum",
    "Look, no hands!",
)

_ = dev_app.c2_send(
    {
        "action": "navigate",
        "path": f"/account/{app_account['id']}",
    }
)


# # print(connector.get_health())

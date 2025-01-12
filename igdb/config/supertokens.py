import os

from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import jwt

def supertokens_init():
    server_url = os.environ.get("SERVER_URI", "http://localhost:5000")
    core_uri = os.environ.get("SUPERTOKENS_CORE_URI", "http://localhost:3567")

    init(
        app_info=InputAppInfo(
            app_name="GameNode",
            api_domain=server_url,
            website_domain="...", # not used
            api_base_path="/v1/auth"
        ),
        supertokens_config=SupertokensConfig(
            connection_uri=core_uri, # location of the core
        ),
        framework='fastapi',
        recipe_list=[
            jwt.init(),
        ],
    )
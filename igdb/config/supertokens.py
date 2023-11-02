from supertokens_python import init, InputAppInfo, SupertokensConfig
from supertokens_python.recipe import jwt
import os

init(
    app_info=InputAppInfo(
        app_name="GameNode",
        api_domain=os.environ.get("DOMAIN_API", "http://localhost:5000"),
        website_domain=os.environ.get("DOMAIN_WEBSITE", "http://localhost:3000"),
    ),
    supertokens_config=SupertokensConfig(
        connection_uri=os.environ.get(
            "SUPERTOKENS_CORE_URI", "http://localhost:3567"
        ),  # location of the core
        api_key=None,  # provide the core's API key if configured
    ),
    framework="fastapi",
    recipe_list=[
        jwt.init(),
    ],
)

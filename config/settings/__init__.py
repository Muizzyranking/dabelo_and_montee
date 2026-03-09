from .env import env

ENVIRONMENT = env.str("ENVIRONMENT", default="dev")

if ENVIRONMENT == "prod":
    from .prod import *  # noqa
else:
    from .dev import *  # noqa

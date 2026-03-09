from .env import env

# ENVIRONMENT = env.str("ENVIRONMENT", default="dev")
ENVIRONMENT = "dev"

if ENVIRONMENT == "prod":
    from .prod import *  # noqa
else:
    from .dev import *  # noqa

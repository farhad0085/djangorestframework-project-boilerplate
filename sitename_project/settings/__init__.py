from .base import *

if ENVIRONMENT == "production":
    from .production import *
else:
    from .development import *
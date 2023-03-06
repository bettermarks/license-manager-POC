from decouple import config, Choices
from licensing.logging import LogLevel


log_level: str = config("LOG_LEVEL", default=LogLevel.DEBUG)
log_format: str = config(
    "LOG_FORMAT", default="console", cast=Choices(["console", "json"])
)

# DB settings
database_user: str = config("DATABASE_USER")
database_password: str = config("DATABASE_PASSWORD")
database_host: str = config("DATABASE_HOST")
database_port: str = config("DATABASE_PORT")
database_name: str = config("DATABASE_NAME")

segment: str = config("SEGMENT")

apm_secret_token: str = config("APM_SECRET_TOKEN", default=None)
apm_url: str = config("APM_URL", default=None)
apm_enabled: str = config("APM_ENABLED", default=False, cast=bool)
apm_transaction_sample_rate: float = config(
    "APM_TRANSACTION_SAMPLE_RATE", default=0.1, cast=float
)

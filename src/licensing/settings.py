from decouple import config, Choices
from licensing.logging import LogLevel


log_level: str = config("LOG_LEVEL", default=LogLevel.DEBUG)
log_format: str = config(
    "LOG_FORMAT", default="console", cast=Choices(["console", "json"])
)

# DB settings
db_user: str = config("DB_USER")
db_password: str = config("DB_PASSWORD")
db_host: str = config("DB_HOST")
db_port: str = config("DB_PORT")
db_name: str = config("DB_NAME")

segment: str = config("SEGMENT")

apm_secret_token: str = config("APM_SECRET_TOKEN", default=None)
apm_url: str = config("APM_URL", default=None)
apm_enabled: str = config("APM_ENABLED", default=False, cast=bool)
apm_transaction_sample_rate: float = config(
    "APM_TRANSACTION_SAMPLE_RATE", default=0.1, cast=float
)

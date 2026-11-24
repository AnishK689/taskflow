from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import our app's config and all models so Alembic can see them.
# Without importing models here, autogenerate won't detect new tables.
from app.core.config import settings
from app.db.session import Base
import app.models.user  # noqa: F401 — registers User with Base.metadata
import app.models.task  # noqa: F401 — registers Task with Base.metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Point Alembic at our models' metadata so it can diff against the DB.
target_metadata = Base.metadata

# Override the sqlalchemy.url in alembic.ini with our settings value.
# This way we only define the DB URL in one place (.env).
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """
    Offline mode: generate SQL scripts without connecting to the DB.
    Useful for reviewing migrations before applying them.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Online mode: connect to DB and apply migrations directly.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

# type: ignore
"""added cpe product configuration

Revision ID: cf1dccc9d1ed
Revises: ea7e8e8ba91d
Create Date: 2023-08-23 15:16:13.079799

"""
import warnings

import sqlalchemy as sa
from alembic import op
from litestar.contrib.sqlalchemy.types import GUID, ORA_JSONB, DateTimeUTC

__all__ = ["downgrade", "upgrade", "schema_upgrades", "schema_downgrades", "data_upgrades", "data_downgrades"]

sa.GUID = GUID
sa.DateTimeUTC = DateTimeUTC
sa.ORA_JSONB = ORA_JSONB

# revision identifiers, used by Alembic.
revision = "cf1dccc9d1ed"
down_revision = "ea7e8e8ba91d"
branch_labels = None
depends_on = None


def upgrade():
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        with op.get_context().autocommit_block():
            schema_upgrades()
            data_upgrades()


def downgrade():
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        with op.get_context().autocommit_block():
            data_downgrades()
            schema_downgrades()


def schema_upgrades():
    """Schema upgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "product_configuration",
        sa.Column("description", sa.String(length=200), nullable=False),
        sa.Column("configuration_id", sa.Integer(), nullable=False),
        sa.Column("cpe_model", sa.String(length=50), nullable=False),
        sa.Column("vendor_id", sa.GUID(length=16), nullable=False),
        sa.Column("id", sa.GUID(length=16), nullable=False),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTimeUTC(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTimeUTC(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["vendor_id"],
            ["vendor.id"],
            name=op.f("fk_product_configuration_vendor_id_vendor"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_product_configuration")),
        sa.UniqueConstraint("configuration_id", name=op.f("uq_product_configuration_configuration_id")),
    )
    # ### end Alembic commands ###


def schema_downgrades():
    """Schema downgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("product_configuration")
    # ### end Alembic commands ###


def data_upgrades():
    """Add any optional data upgrade migrations here!"""


def data_downgrades():
    """Add any optional data downgrade migrations here!"""

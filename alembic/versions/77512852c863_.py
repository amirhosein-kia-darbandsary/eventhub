"""empty message

Revision ID: 77512852c863
Revises: 86e1d29ec272
Create Date: 2026-08-16 19:11:08.078184

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '77512852c863'
down_revision: Union[str, Sequence[str], None] = '86e1d29ec272'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    webhook_event_status = sa.Enum(
        'received',
        'processed',
        'dead_letter',
        name='webhookeventstatus'
    )

    webhook_event_status.create(
        op.get_bind(),
        checkfirst=True
    )

    op.add_column(
        'webhook_events',
        sa.Column(
            'status',
            webhook_event_status,
            nullable=False
        )
    )

    op.drop_column(
        "webhook_events",
        "id"
    )

    op.add_column(
        "webhook_events",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            nullable=False
        )
    )

    op.alter_column(
        'webhook_events',
        'payload',
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        type_=sa.String(),
        existing_nullable=False
    )


def downgrade() -> None:
    op.drop_column(
        'webhook_events',
        'status'
    )

    sa.Enum(
        name='webhookeventstatus'
    ).drop(
        op.get_bind(),
        checkfirst=True
    )

    op.alter_column(
        'webhook_events',
        'payload',
        existing_type=sa.String(),
        type_=postgresql.JSON(astext_type=sa.Text()),
        existing_nullable=False
    )

    op.alter_column(
        'webhook_events',
        'id',
        existing_type=sa.Uuid(),
        type_=sa.INTEGER(),
        existing_nullable=False
    )

    # ### end Alembic commands ###

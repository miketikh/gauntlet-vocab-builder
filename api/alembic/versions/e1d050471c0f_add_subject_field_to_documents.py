"""add_subject_field_to_documents

Revision ID: e1d050471c0f
Revises: dff23adf0a56
Create Date: 2025-11-13 16:49:32.576507

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1d050471c0f'
down_revision: Union[str, Sequence[str], None] = 'dff23adf0a56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add subject column to documents table
    op.add_column('documents', sa.Column('subject', sa.String(length=100), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove subject column from documents table
    op.drop_column('documents', 'subject')

"""update_quotes_table

Revision ID: 24f31688801f
Revises: 9acfdf6c5274
Create Date: 2025-08-22 12:49:19.891805

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '24f31688801f'
down_revision: Union[str, None] = '9acfdf6c5274'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old columns
    op.drop_column('quotes', 'company_name')
    op.drop_column('quotes', 'contact_name')
    op.drop_column('quotes', 'email')
    op.drop_column('quotes', 'phone')
    op.drop_column('quotes', 'package_ids')
    
    # Add new columns
    op.add_column('quotes', sa.Column('patient_id', sa.String(100)))
    op.add_column('quotes', sa.Column('patient_age', sa.Integer))
    op.add_column('quotes', sa.Column('patient_phone', sa.String(20)))
    op.add_column('quotes', sa.Column('patient_email', sa.String(100)))
    op.add_column('quotes', sa.Column('procedure_name', sa.String(200)))
    op.add_column('quotes', sa.Column('procedure_code', sa.String(50)))
    op.add_column('quotes', sa.Column('procedure_description', sa.String(1000)))
    op.add_column('quotes', sa.Column('surgeon_name', sa.String(100)))
    op.add_column('quotes', sa.Column('surgeon_specialty', sa.String(100)))
    op.add_column('quotes', sa.Column('facility_fee', sa.Float))
    op.add_column('quotes', sa.Column('equipment_costs', sa.Float))
    op.add_column('quotes', sa.Column('anesthesia_fee', sa.Float))
    op.add_column('quotes', sa.Column('other_costs', sa.Float))
    op.add_column('quotes', sa.Column('surgery_duration_hours', sa.Integer))
    op.add_column('quotes', sa.Column('created_by', sa.String(100)))
    op.add_column('quotes', sa.Column('notes', sa.String(1000)))
    op.add_column('quotes', sa.Column('surgical_package', sa.TEXT))
    op.add_column('quotes', sa.Column('status', sa.String(50), server_default='borrador'))


def downgrade() -> None:
    # Drop new columns
    op.drop_column('quotes', 'status')
    op.drop_column('quotes', 'surgical_package')
    op.drop_column('quotes', 'notes')
    op.drop_column('quotes', 'created_by')
    op.drop_column('quotes', 'surgery_duration_hours')
    op.drop_column('quotes', 'other_costs')
    op.drop_column('quotes', 'anesthesia_fee')
    op.drop_column('quotes', 'equipment_costs')
    op.drop_column('quotes', 'facility_fee')
    op.drop_column('quotes', 'surgeon_specialty')
    op.drop_column('quotes', 'surgeon_name')
    op.drop_column('quotes', 'procedure_description')
    op.drop_column('quotes', 'procedure_code')
    op.drop_column('quotes', 'procedure_name')
    op.drop_column('quotes', 'patient_email')
    op.drop_column('quotes', 'patient_phone')
    op.drop_column('quotes', 'patient_age')
    op.drop_column('quotes', 'patient_id')
    
    # Restore old columns
    op.add_column('quotes', sa.Column('package_ids', sa.String(500)))
    op.add_column('quotes', sa.Column('phone', sa.String(20)))
    op.add_column('quotes', sa.Column('email', sa.String(100)))
    op.add_column('quotes', sa.Column('contact_name', sa.String(100)))
    op.add_column('quotes', sa.Column('company_name', sa.String(100)))

"""empty message

Revision ID: b6b471edc9ff
Revises: 6308243b2fa6
Create Date: 2020-06-27 13:49:41.022267

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6b471edc9ff'
down_revision = '6308243b2fa6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ArtistGenre', 'id')
    op.drop_column('VenueGenre', 'id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('VenueGenre', sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"VenueGenre_id_seq"\'::regclass)'), autoincrement=True, nullable=False))
    op.add_column('ArtistGenre', sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"ArtistGenre_id_seq"\'::regclass)'), autoincrement=True, nullable=False))
    # ### end Alembic commands ###
"""Lead finder: search runs and leads.

Revision ID: 0002
Revises: 0001
"""
import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def _ts() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "lead_search_runs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("client_id", sa.Integer, sa.ForeignKey("clients.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_by", sa.String(255), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("queries_total", sa.Integer, nullable=False),
        sa.Column("queries_done", sa.Integer, nullable=False),
        sa.Column("pages_total", sa.Integer, nullable=False),
        sa.Column("pages_done", sa.Integer, nullable=False),
        sa.Column("leads_found", sa.Integer, nullable=False),
        sa.Column("stage", sa.String(120), nullable=False),
        sa.Column("error", sa.Text, nullable=False),
        sa.Column("summary_json", sa.JSON),
        *_ts(),
    )
    op.create_index("ix_lead_search_runs_client_id", "lead_search_runs", ["client_id"])
    op.create_index("ix_lead_search_runs_status", "lead_search_runs", ["status"])

    op.create_table(
        "leads",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("client_id", sa.Integer, sa.ForeignKey("clients.id"), nullable=False),
        sa.Column("run_id", sa.Integer, sa.ForeignKey("lead_search_runs.id")),
        sa.Column("url", sa.String(1000), nullable=False),
        sa.Column("url_key", sa.String(600), nullable=False),
        sa.Column("source", sa.String(255), nullable=False),
        sa.Column("author", sa.String(120), nullable=False),
        sa.Column("author_key", sa.String(400), nullable=False),
        sa.Column("poster_type", sa.String(20), nullable=False),
        sa.Column("problem", sa.Text, nullable=False),
        sa.Column("quote", sa.Text, nullable=False),
        sa.Column("posted_at", sa.DateTime(timezone=True)),
        sa.Column("date_known", sa.Boolean, nullable=False),
        sa.Column("problem_match", sa.Integer, nullable=False),
        sa.Column("intent", sa.Integer, nullable=False),
        sa.Column("score", sa.Integer, nullable=False),
        sa.Column("priority", sa.String(20), nullable=False),
        sa.Column("breakdown_json", sa.JSON, nullable=False),
        sa.Column("why_fit", sa.Text, nullable=False),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("contact_json", sa.JSON, nullable=False),
        sa.Column("verified", sa.Boolean, nullable=False),
        sa.Column("supporting_urls_json", sa.JSON, nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("note", sa.Text, nullable=False),
        sa.Column("outreach_json", sa.JSON),
        *_ts(),
        sa.UniqueConstraint("client_id", "url_key", name="uq_lead_client_url"),
    )
    op.create_index("ix_leads_client_id", "leads", ["client_id"])
    op.create_index("ix_leads_author_key", "leads", ["author_key"])
    op.create_index("ix_leads_score", "leads", ["score"])
    op.create_index("ix_leads_status", "leads", ["status"])


def downgrade() -> None:
    op.drop_table("leads")
    op.drop_table("lead_search_runs")

"""Hierarchical RBAC and Announcement Channels - Table Schema Initializer and SQL DDL Migrations.
"""
from typing import List

class GroupsSchemaMigrations:
    @staticmethod
    def get_ddl_statements() -> List[str]:
        return [
            f"""CREATE TABLE IF NOT EXISTS groups_records (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(50) NOT NULL DEFAULT 'default',
                payload JSONB NOT NULL,
                version INT NOT NULL DEFAULT 1,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );""",
            f"""CREATE INDEX IF NOT EXISTS idx_groups_tenant ON groups_records(tenant_id);""",
            f"""CREATE INDEX IF NOT EXISTS idx_groups_active ON groups_records(is_active);""",
            f"""CREATE INDEX IF NOT EXISTS idx_groups_created ON groups_records(created_at DESC);"""
        ]

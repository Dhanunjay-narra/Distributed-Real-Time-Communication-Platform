"""Ephemeral Mesh and Activity Streams - Table Schema Initializer and SQL DDL Migrations.
"""
from typing import List

class PresenceSchemaMigrations:
    @staticmethod
    def get_ddl_statements() -> List[str]:
        return [
            f"""CREATE TABLE IF NOT EXISTS presence_records (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(50) NOT NULL DEFAULT 'default',
                payload JSONB NOT NULL,
                version INT NOT NULL DEFAULT 1,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );""",
            f"""CREATE INDEX IF NOT EXISTS idx_presence_tenant ON presence_records(tenant_id);""",
            f"""CREATE INDEX IF NOT EXISTS idx_presence_active ON presence_records(is_active);""",
            f"""CREATE INDEX IF NOT EXISTS idx_presence_created ON presence_records(created_at DESC);"""
        ]

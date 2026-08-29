"""Vector Clock Replication and Offline Recovery - Table Schema Initializer and SQL DDL Migrations.
"""
from typing import List

class SyncSchemaMigrations:
    @staticmethod
    def get_ddl_statements() -> List[str]:
        return [
            f"""CREATE TABLE IF NOT EXISTS sync_records (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(50) NOT NULL DEFAULT 'default',
                payload JSONB NOT NULL,
                version INT NOT NULL DEFAULT 1,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );""",
            f"""CREATE INDEX IF NOT EXISTS idx_sync_tenant ON sync_records(tenant_id);""",
            f"""CREATE INDEX IF NOT EXISTS idx_sync_active ON sync_records(is_active);""",
            f"""CREATE INDEX IF NOT EXISTS idx_sync_created ON sync_records(created_at DESC);"""
        ]

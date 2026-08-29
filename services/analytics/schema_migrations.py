"""Time-Series Aggregations and DAU Metrics - Table Schema Initializer and SQL DDL Migrations.
"""
from typing import List

class AnalyticsSchemaMigrations:
    @staticmethod
    def get_ddl_statements() -> List[str]:
        return [
            f"""CREATE TABLE IF NOT EXISTS analytics_records (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(50) NOT NULL DEFAULT 'default',
                payload JSONB NOT NULL,
                version INT NOT NULL DEFAULT 1,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );""",
            f"""CREATE INDEX IF NOT EXISTS idx_analytics_tenant ON analytics_records(tenant_id);""",
            f"""CREATE INDEX IF NOT EXISTS idx_analytics_active ON analytics_records(is_active);""",
            f"""CREATE INDEX IF NOT EXISTS idx_analytics_created ON analytics_records(created_at DESC);"""
        ]

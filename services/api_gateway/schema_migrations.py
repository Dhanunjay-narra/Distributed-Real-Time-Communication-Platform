"""Reverse Proxy and Correlation Ingress - Table Schema Initializer and SQL DDL Migrations.
"""
from typing import List

class ApiGatewaySchemaMigrations:
    @staticmethod
    def get_ddl_statements() -> List[str]:
        return [
            f"""CREATE TABLE IF NOT EXISTS api_gateway_records (
                id VARCHAR(36) PRIMARY KEY,
                tenant_id VARCHAR(50) NOT NULL DEFAULT 'default',
                payload JSONB NOT NULL,
                version INT NOT NULL DEFAULT 1,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );""",
            f"""CREATE INDEX IF NOT EXISTS idx_api_gateway_tenant ON api_gateway_records(tenant_id);""",
            f"""CREATE INDEX IF NOT EXISTS idx_api_gateway_active ON api_gateway_records(is_active);""",
            f"""CREATE INDEX IF NOT EXISTS idx_api_gateway_created ON api_gateway_records(created_at DESC);"""
        ]

import os
from typing import List, Optional, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class PlatformSettings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, extra="allow", env_file=".env", env_file_encoding="utf-8")

    # Service & Environment
    PROJECT_NAME: str = "Chatbot Distributed Real-Time Communication Platform"
    PROJECT_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=False, description="Debug mode flag")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    SERVICE_NAME: str = Field(default="chatbot-core", description="Current microservice name")
    NODE_ID: str = Field(default="node-01", description="Cluster node identifier")
    CLUSTER_REGION: str = Field(default="us-east-1", description="Deployment cloud region")
    AVAILABILITY_ZONE: str = Field(default="us-east-1a", description="Cloud availability zone")

    # API & Gateway Ports
    API_GATEWAY_PORT: int = 8000
    WEBSOCKET_GATEWAY_PORT: int = 8001
    AUTH_SERVICE_PORT: int = 8010
    USERS_SERVICE_PORT: int = 8020
    MESSAGING_SERVICE_PORT: int = 8030
    PRESENCE_SERVICE_PORT: int = 8040
    GROUPS_SERVICE_PORT: int = 8050
    SYNC_SERVICE_PORT: int = 8060
    MEDIA_SERVICE_PORT: int = 8070
    CALLS_SERVICE_PORT: int = 8080
    SEARCH_SERVICE_PORT: int = 8090
    NOTIFICATIONS_SERVICE_PORT: int = 8100
    MODERATION_SERVICE_PORT: int = 8110
    ADMIN_SERVICE_PORT: int = 8120
    COORDINATION_SERVICE_PORT: int = 8130

    # Security & Cryptography
    JWT_SECRET_KEY: str = Field(default="chatbot-distributed-super-secret-key-32bytes-min-len", description="HMAC Secret Key")
    JWT_ALGORITHM: str = "HS256"
    JWT_PUBLIC_KEY: Optional[str] = None
    JWT_PRIVATE_KEY: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    OTP_EXPIRE_SECONDS: int = 300
    OTP_MAX_ATTEMPTS: int = 5
    PASSWORD_HASH_ROUNDS: int = 12
    E2EE_MASTER_KEY: str = "c7891234567890abcdef1234567890abcdef1234567890abcdef1234567890ab"
    DOUBLE_RATCHET_MAX_SKIP_KEYS: int = 2000

    # CORS & Networking
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8000", "https://chatbot.internal"]
    TRUSTED_PROXIES: List[str] = ["127.0.0.1", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
    SSL_ENABLED: bool = False
    SSL_CERT_PATH: Optional[str] = None
    SSL_KEY_PATH: Optional[str] = None

    # Database & Replication
    DATABASE_URL: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/chatbot", description="Primary Read/Write Postgres")
    DATABASE_REPLICA_URL: Optional[str] = Field(default=None, description="Read replica Postgres connection string")
    DB_POOL_SIZE: int = 25
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_TIMEOUT: float = 30.0
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = False

    # Redis Cluster & Distributed Lock
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Primary Redis instance or cluster entry")
    REDIS_SENTINEL_HOSTS: List[str] = []
    REDIS_SENTINEL_MASTER: str = "mymaster"
    REDIS_CLUSTER_NODES: List[str] = []
    REDIS_POOL_SIZE: int = 50
    REDIS_SOCKET_TIMEOUT: float = 2.0
    REDIS_SOCKET_CONNECT_TIMEOUT: float = 2.0
    LOCK_DEFAULT_TIMEOUT_SECONDS: int = 15
    LOCK_ACQUIRE_TIMEOUT_SECONDS: float = 5.0

    # Kafka Event Backbone
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_CLIENT_ID: str = "chatbot-distributed-cluster"
    KAFKA_CONSUMER_GROUP_PREFIX: str = "chatbot-group"
    KAFKA_TOPIC_MESSAGES_SENT: str = "messages.sent"
    KAFKA_TOPIC_MESSAGES_DELIVERED: str = "messages.delivered"
    KAFKA_TOPIC_MESSAGES_READ: str = "messages.read"
    KAFKA_TOPIC_USER_PRESENCE: str = "user.presence"
    KAFKA_TOPIC_GROUPS: str = "groups.events"
    KAFKA_TOPIC_CALLS: str = "calls.signaling"
    KAFKA_TOPIC_NOTIFICATIONS: str = "notifications.requests"
    KAFKA_TOPIC_MEDIA: str = "media.events"
    KAFKA_TOPIC_SAGAS: str = "sagas.events"
    KAFKA_TOPIC_DLQ: str = "dead_letter_queue"
    KAFKA_MAX_POLL_INTERVAL_MS: int = 300000
    KAFKA_SESSION_TIMEOUT_MS: int = 45000
    KAFKA_AUTO_OFFSET_RESET: str = "latest"

    # Distributed Presence Mesh
    PRESENCE_HEARTBEAT_INTERVAL_SECONDS: int = 15
    PRESENCE_TTL_SECONDS: int = 45
    TYPING_TIMEOUT_SECONDS: float = 5.0
    PRESENCE_CLUSTER_SYNC_INTERVAL: float = 2.0

    # Storage & Media Pipeline
    STORAGE_BACKEND: str = "minio"  # 'minio', 's3', 'local'
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "chatbot-media"
    S3_REGION: str = "us-east-1"
    S3_USE_SSL: bool = False
    MEDIA_MAX_FILE_SIZE_BYTES: int = 104857600  # 100MB
    MEDIA_CHUNK_SIZE_BYTES: int = 5242880  # 5MB
    MEDIA_IMAGE_MAX_WIDTH: int = 3840
    MEDIA_IMAGE_MAX_HEIGHT: int = 2160
    MEDIA_THUMBNAIL_SIZE: int = 300

    # Search & OpenSearch Engine
    OPENSEARCH_HOSTS: List[str] = ["http://localhost:9200"]
    OPENSEARCH_USERNAME: str = "admin"
    OPENSEARCH_PASSWORD: str = "admin"
    OPENSEARCH_INDEX_MESSAGES: str = "chatbot_messages"
    OPENSEARCH_INDEX_USERS: str = "chatbot_users"
    OPENSEARCH_INDEX_GROUPS: str = "chatbot_groups"
    OPENSEARCH_INDEX_CONVERSATIONS: str = "chatbot_conversations"
    SEARCH_FUZZY_DISTANCE: int = 2

    # WebRTC & Calling Mesh
    STUN_SERVERS: List[str] = ["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302"]
    TURN_SERVERS: List[Dict[str, str]] = [
        {"url": "turn:turn.chatbot.internal:3478", "username": "turnuser", "credential": "turnpassword"}
    ]
    CALL_RINGING_TIMEOUT_SECONDS: int = 45
    CALL_MAX_PARTICIPANTS: int = 32

    # Push Notifications
    FCM_SERVER_KEY: Optional[str] = None
    FCM_PROJECT_ID: Optional[str] = None
    APNS_KEY_ID: Optional[str] = None
    APNS_TEAM_ID: Optional[str] = None
    APNS_BUNDLE_ID: str = "com.chatbot.app"
    PUSH_BATCH_SIZE: int = 500
    PUSH_RATE_LIMIT_PER_SEC: int = 1000

    # Rate Limiting & Bulkheads
    RATE_LIMIT_GLOBAL_PER_MINUTE: int = 120
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10
    RATE_LIMIT_MESSAGING_PER_MINUTE: int = 180
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT_SECONDS: float = 30.0
    CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS: int = 3
    BULKHEAD_MAX_CONCURRENT_CALLS: int = 100
    BULKHEAD_MAX_QUEUE_SIZE: int = 50

    # Raft Consensus Engine
    RAFT_NODE_ID: str = "raft-01"
    RAFT_PEER_NODES: List[str] = ["raft-02", "raft-03"]
    RAFT_ELECTION_TIMEOUT_MIN_MS: int = 150
    RAFT_ELECTION_TIMEOUT_MAX_MS: int = 300
    RAFT_HEARTBEAT_INTERVAL_MS: int = 50
    RAFT_SNAPSHOT_THRESHOLD_ENTRIES: int = 1000

    # Monitoring & Tracing
    PROMETHEUS_METRICS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9100
    OPENTELEMETRY_EXPORTER_ENDPOINT: str = "http://localhost:4317"
    TRACING_SAMPLE_RATE: float = 1.0

settings = PlatformSettings()

Settings = PlatformSettings

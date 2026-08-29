import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "chatbot-distributed-super-secret-key-32bytes-min-len"
os.environ["ENVIRONMENT"] = "test"

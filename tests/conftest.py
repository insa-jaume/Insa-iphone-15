"""Configuración de tests: usa SQLite en memoria por defecto."""
import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret")

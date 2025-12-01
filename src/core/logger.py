import sqlite3
import json
import datetime
import uuid
import os
from .config import Config

class AgentLogger:
    def __init__(self):
        # Ensure the path exists or is valid
        self.db_path = Config.DB_PATH
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                agent_name TEXT,
                prompt TEXT,
                output TEXT,
                metadata TEXT
            )
        ''')
        self.conn.commit()

    def log(self, agent_name: str, prompt: str, output: dict | str, metadata: dict = None):
        """
        Logs an agent interaction to the SQLite database.
        """
        entry_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        
        # Ensure output/metadata are strings for storage
        output_str = json.dumps(output) if isinstance(output, (dict, list)) else str(output)
        meta_str = json.dumps(metadata) if metadata else "{}"

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO interactions VALUES (?, ?, ?, ?, ?, ?)",
                (entry_id, timestamp, agent_name, prompt, output_str, meta_str)
            )
            self.conn.commit()
        except Exception as e:
            print(f"[Logger Error] Failed to write to DB: {e}")

# Global instance
logger = AgentLogger()

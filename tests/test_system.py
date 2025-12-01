import unittest
import os
import sqlite3
import sys
from unittest.mock import patch

# Ensure we can import from src
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.config import Config
from src.core.logger import AgentLogger
from src.tools.lexicon import lexicon
from src.core.reflection_loop import ReflectionLoop

class TestSystem(unittest.TestCase):

    def setUp(self):
        """Runs before every test to set up a clean environment."""
        # 1. Use a temporary database file
        self.test_db = "test_logs.db"
        # We manually overwrite the DB_PATH class attribute for the test
        Config.DB_PATH = self.test_db
        
        # 2. Patch the Environment to bypass API Key validation
        self.env_patcher = patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_test_key"})
        self.env_patcher.start()

    def tearDown(self):
        """Runs after every test to clean up."""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.env_patcher.stop()

    def test_logger_writes_to_db(self):
        """
        [Component Test] 
        Verifies that AgentLogger actually writes rows to SQLite.
        """
        logger = AgentLogger() # Re-init to use the test_db path
        
        # Log a dummy action
        logger.log("TestAgent", "Input Prompt", {"result": "Success"}, {"meta": "data"})
        
        # Manually check the DB
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT agent_name, output FROM interactions")
        row = cursor.fetchone()
        conn.close()
        
        self.assertEqual(row[0], "TestAgent")
        self.assertIn("Success", row[1])

    def test_lexicon_tool_graceful_failure(self):
        """
        [Tool Test]
        Verifies the dictionary tool doesn't crash if files are missing.
        """
        # Should return a "not found" string, NOT raise an exception
        result = lexicon.lookup_vietnamese("nonexistent_word_12345")
        self.assertIn("not found", result)

    @patch('src.agents.translator_agent.TranslatorAgent.run')
    @patch('src.agents.critic_agent.CriticAgent.run')
    def test_reflection_loop_retry_logic(self, mock_critic, mock_translator):
        """
        [Logic Test]
        Verifies that if the Critic gives a low score (5/10), the system RETRIES.
        """
        # SCENARIO:
        # Attempt 1: Translator gives bad draft -> Critic gives 5/10
        # Attempt 2: Translator gives good draft -> Critic gives 9/10
        
        # Setup Translator Responses (returns dictionary)
        mock_translator.return_value = {"translation": "Draft Text", "reasoning": "Testing"}
        
        # Setup Critic Responses (returns dictionary)
        mock_critic.side_effect = [
            {"score": 5, "critique": "Too informal", "suggestions": "Fix it"}, # Attempt 1
            {"score": 9, "critique": "Perfect", "suggestions": "None"}         # Attempt 2
        ]
        
        # Run the Loop
        loop = ReflectionLoop()
        result = loop.process_request("Hello", {})
        
        # ASSERTIONS
        # The loop should have run TWICE because the first score was low
        self.assertEqual(result['attempts'], 2) 
        self.assertEqual(result['final_score'], 9)
        
        # Verify the agents were actually called the correct number of times
        self.assertEqual(mock_translator.call_count, 2)
        self.assertEqual(mock_critic.call_count, 2)

if __name__ == '__main__':
    unittest.main()

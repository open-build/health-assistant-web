import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('manage', ROOT / 'scripts/manage.py')
manage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manage)


class ManagementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forge = manage.load_forge()

    def handler(self):
        return object.__new__(manage.create_handler(self.forge))

    def test_save_stays_in_public_directory(self):
        handler = self.handler()
        self.assertEqual(handler.clean_path('articles/example.html'), 'articles/example.html')
        for path in ('../README.md', '/tmp/outside.html'):
            with self.assertRaises(ValueError):
                handler.clean_path(path)

    def test_remote_inference_is_rejected(self):
        with patch.dict(os.environ, {'OLLAMA_ENDPOINT': 'https://example.com'}):
            with self.assertRaises(SystemExit):
                manage.create_handler(self.forge)

    def test_draft_uses_configured_local_model_and_facts(self):
        with patch.dict(os.environ, {'OLLAMA_ENDPOINT': 'http://127.0.0.1:11434', 'OLLAMA_MODEL': 'test-model'}):
            handler = self.handler()
        with patch.object(self.forge.ForgeWebHandler, '_call_ollama', return_value='<p>Draft</p>') as call:
            result = handler._call_ollama('https://ignored.example', 'ignored', 'Write HTML.', 'Visit preparation')
        self.assertEqual(result, '<p>Draft</p>')
        endpoint, model, system, prompt = call.call_args.args
        self.assertEqual(endpoint, 'http://127.0.0.1:11434')
        self.assertEqual(model, 'test-model')
        self.assertIn('No public App Store', system)
        self.assertEqual(prompt, 'Visit preparation')

    def test_paid_fallback_is_disabled(self):
        handler = self.handler()
        for method in (handler._call_openai, handler._call_gemini):
            with self.assertRaises(ValueError):
                method()

    def test_initialization_preserves_existing_site_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            database = self.forge.ForgeWebDB(str(Path(directory) / 'test.db'))
            original = self.forge.db
            self.forge.db = database
            try:
                database.set_site_config('site', {'name': 'Existing name'})
                manage.initialize(self.forge)
                manage.initialize(self.forge)
                self.assertEqual(database.get_site_config('site')['name'], 'Existing name')
                self.assertEqual(len(database.get_all_pages()), 2)
            finally:
                database.conn.close()
                self.forge.db = original


if __name__ == '__main__':
    unittest.main()

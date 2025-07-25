import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import types

# Provide minimal PyQt6 stubs so the services package can be imported without
# the real PyQt6 dependency.
qtcore = types.ModuleType("QtCore")
qtcore.QObject = object
qtcore.QTimer = object
qtcore.pyqtSignal = lambda *args, **kwargs: lambda *a, **k: None
pyqt6 = types.ModuleType("PyQt6")
pyqt6.QtCore = qtcore
pyqt6.QtWidgets = types.ModuleType("QtWidgets")
pyqt6.QtTest = types.ModuleType("QtTest")
sys.modules.setdefault("PyQt6", pyqt6)
sys.modules.setdefault("PyQt6.QtCore", qtcore)
sys.modules.setdefault("PyQt6.QtWidgets", pyqt6.QtWidgets)
sys.modules.setdefault("PyQt6.QtTest", pyqt6.QtTest)
requests_mod = types.ModuleType("requests")
class DummySession:
    def __init__(self):
        self.headers = {}
    def get(self, *a, **k):
        return MagicMock(status_code=200, json=lambda: {})
    post = get
    put = get
    delete = get
    def close(self):
        pass
requests_mod.Session = DummySession
requests_mod.exceptions = types.SimpleNamespace(Timeout=Exception, ConnectionError=Exception, RequestException=Exception)
sys.modules.setdefault("requests", requests_mod)
crypto = types.ModuleType("cryptography")
hazmat = types.ModuleType("hazmat")
primitives = types.ModuleType("primitives")
hashes = types.ModuleType("hashes")
pbkdf2 = types.ModuleType("pbkdf2")
pbkdf2.PBKDF2HMAC = object
primitives.hashes = hashes
primitives.kdf = types.ModuleType("kdf")
primitives.kdf.pbkdf2 = pbkdf2
hazmat.primitives = primitives
fernet_mod = types.ModuleType("fernet")
fernet_mod.Fernet = object
crypto.hazmat = hazmat
crypto.fernet = fernet_mod
sys.modules.setdefault("cryptography", crypto)
sys.modules.setdefault("cryptography.hazmat", hazmat)
sys.modules.setdefault("cryptography.hazmat.primitives", primitives)
sys.modules.setdefault("cryptography.hazmat.primitives.hashes", hashes)
sys.modules.setdefault("cryptography.hazmat.primitives.kdf", primitives.kdf)
sys.modules.setdefault("cryptography.hazmat.primitives.kdf.pbkdf2", pbkdf2)
sys.modules.setdefault("cryptography.fernet", fernet_mod)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util

# Load GoogleProvider without importing the full services package (which
# requires heavy dependencies like PyQt6 and cryptography).  We load the
# module directly from its file path and then extract ``GoogleProvider``.
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
module_path = os.path.join(current_dir, 'services', 'providers', 'google_provider.py')
spec = importlib.util.spec_from_file_location('services.providers.google_provider', module_path)
google_provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(google_provider)
GoogleProvider = google_provider.GoogleProvider
LLMParameters = importlib.import_module('models.llm_models').LLMParameters

class TestGoogleProviderSession(unittest.TestCase):
    def setUp(self):
        self.api_key = "AIzaTestKey1234567890"
        self.provider = GoogleProvider(self.api_key)

    def test_setup_session_sets_header(self):
        self.assertEqual(self.provider.session.headers.get("X-Goog-Api-Key"), self.api_key)

    def test_make_request_uses_header_and_no_key_param(self):
        def fake_post(url, json=None, timeout=30):
            # Header should already be attached to the session
            self.assertEqual(self.provider.session.headers.get("X-Goog-Api-Key"), self.api_key)
            self.assertNotIn("key=", url)
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {"ok": True}
            return resp

        with patch.object(self.provider.session, "post", side_effect=fake_post) as mock_post:
            success, data, _ = self.provider._make_request("POST", "test", {})
            self.assertTrue(success)
            self.assertEqual(data, {"ok": True})
            mock_post.assert_called_once()

    def test_generate_text_endpoint_does_not_add_key(self):
        dummy_response = {"candidates": [{"content": {"parts": [{"text": "hi"}]}}], "usageMetadata": {}}
        with patch.object(self.provider, "_make_request", return_value=(True, dummy_response, 0.1)) as mock_req:
            params = LLMParameters()
            self.provider.generate_text("hello", "gemini-pro", params)
            endpoint = mock_req.call_args[0][1]
            self.assertNotIn("key=", endpoint)

if __name__ == "__main__":
    unittest.main()

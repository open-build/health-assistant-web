#!/usr/bin/env python3
"""Launch the pinned ForgeWeb admin against this site's public directory."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
ADMIN = ROOT / 'ForgeWeb' / 'admin'


def load_forge():
    if not (ADMIN / 'file-api.py').is_file():
        raise SystemExit('ForgeWeb checkout missing. Run bash scripts/setup.sh first.')
    sys.path.insert(0, str(ADMIN))
    # The upstream server otherwise defaults to docs/. Use its supported override.
    os.environ['WEBSITE_ROOT'] = str(ROOT / 'website')
    spec = importlib.util.spec_from_file_location('forgeweb_api', ADMIN / 'file-api.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.db is None:
        raise SystemExit('ForgeWeb database could not be initialized.')
    return module


def initialize(module):
    config = json.loads((ROOT / 'forgeweb.json').read_text())
    database = module.db
    for key in ('site', 'branding'):
        if database.get_site_config(key) is None:
            database.set_site_config(key, config[key])
    if database.get_design_config() is None:
        database.set_design_config('custom', [], '', '')
    existing = {page['slug'] for page in database.get_all_pages()}
    for title, slug, filename in [('Health Assistant', 'home', 'index.html'),
                                  ('Privacy model', 'privacy', 'privacy.html')]:
        if slug not in existing:
            database.add_page(title, slug, filename, status='draft')
    print('Health Assistant pages registered. Existing content and settings preserved.')


def create_handler(module):
    brief = (ROOT / 'content' / 'editorial-brief.md').read_text()
    endpoint = os.getenv('OLLAMA_ENDPOINT', 'http://127.0.0.1:11434').rstrip('/')
    model = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
    # This workspace's writing workflow is intentionally local, with no paid fallback.
    if urlparse(endpoint).hostname not in ('localhost', '127.0.0.1', '::1'):
        raise SystemExit('OLLAMA_ENDPOINT must point to a loopback host for local drafting.')

    class HealthAssistantHandler(module.ForgeWebHandler):
        def _request_allowed(self):
            allowed_hosts = {f'127.0.0.1:{self.server.server_port}',
                             f'localhost:{self.server.server_port}'}
            if self.headers.get('Host') not in allowed_hosts:
                self.send_error(403, 'Use the localhost admin URL.')
                return False
            origin = self.headers.get('Origin')
            if origin and origin not in {f'http://{host}' for host in allowed_hosts}:
                self.send_error(403, 'Cross-origin admin requests are disabled.')
                return False
            decoded = unquote(urlparse(self.path).path)
            if '..' in decoded.split('/') or '\\' in decoded:
                self.send_error(400, 'Invalid path')
                return False
            return True

        def do_GET(self):
            if self._request_allowed():
                super().do_GET()

        def do_POST(self):
            if self._request_allowed():
                super().do_POST()

        def do_PUT(self):
            if self._request_allowed():
                super().do_PUT()

        def do_DELETE(self):
            if self._request_allowed():
                super().do_DELETE()

        def do_OPTIONS(self):
            if self._request_allowed():
                self.send_response(204)
                self.end_headers()

        def clean_path(self, path):
            target = (ROOT / 'website' / path).resolve()
            if not target.is_relative_to((ROOT / 'website').resolve()):
                raise ValueError('File must stay inside website/.')
            return str(target.relative_to(ROOT / 'website'))

        def _call_ollama(self, _endpoint, _model, system_msg, prompt):
            return super()._call_ollama(endpoint, model,
                system_msg + '\n\nUse this factual editorial brief:\n' + brief, prompt)

        def _call_openai(self, *args):
            raise ValueError('This site uses local Ollama drafting. Select Ollama in the editor.')

        def _call_gemini(self, *args):
            raise ValueError('This site uses local Ollama drafting. Select Ollama in the editor.')

    return HealthAssistantHandler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--initialize-only', action='store_true')
    parser.add_argument('--port', type=int, default=int(os.getenv('FORGEWEB_PORT', '8000')))
    args = parser.parse_args()
    module = load_forge()
    initialize(module)
    if args.initialize_only:
        return
    server = module.HTTPServer(('127.0.0.1', args.port), create_handler(module))
    print(f'Website: http://127.0.0.1:{args.port}/', flush=True)
    print(f'ForgeWeb admin: http://127.0.0.1:{args.port}/admin/', flush=True)
    print('Local AI model: ' + os.getenv('OLLAMA_MODEL', 'llama3.2:3b'), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()

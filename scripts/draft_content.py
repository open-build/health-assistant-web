#!/usr/bin/env python3
"""Request a fact-grounded HTML draft via the running local ForgeWeb API."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prompt', help='The content to draft, e.g. a visit-preparation article')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    payload = json.dumps({'provider': 'ollama', 'prompt': args.prompt,
                          'context': (ROOT / 'website' / 'index.html').read_text()[:3000]}).encode()
    request = Request(f'http://127.0.0.1:{args.port}/api/ai-generate', data=payload,
                      headers={'Content-Type': 'application/json'})
    try:
        with urlopen(request, timeout=75) as response:
            data = json.load(response)
        if not data.get('success') or not data.get('code', '').strip():
            raise ValueError('No generated draft was returned.')
    except (URLError, HTTPError, ValueError) as error:
        raise SystemExit(f'Draft failed: {error}. Start ForgeWeb and Ollama with an installed model. No content was published.')
    drafts = ROOT / 'content' / 'drafts'
    drafts.mkdir(exist_ok=True)
    filename = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.html'
    output = drafts / filename
    output.write_text(data['code'])
    print(f'Draft saved for review: {output}')
    print('Review factual claims and generated HTML before adding it to website/. Nothing was published.')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Check portable links, anchors, metadata, and public artifact boundaries."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1] / 'website'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.refs, self.ids, self.titles, self.h1s = [], set(), 0, 0
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f'Duplicate id: {attrs["id"]}'
            self.ids.add(attrs['id'])
        if tag == 'title':
            self.titles += 1
        if tag == 'h1':
            self.h1s += 1
        for key in ('href', 'src'):
            if key in attrs:
                self.refs.append(attrs[key])
        if tag == 'img':
            assert 'alt' in attrs, 'Image missing alternative text'
        if tag == 'script' and 'src' in attrs:
            assert not urlsplit(attrs['src']).scheme, 'Unexpected remote public script'


def main():
    pages = {p: Page(p) for p in ROOT.rglob('*.html') if '_preview' not in p.parts}
    for path, page in pages.items():
        assert page.titles == 1 and page.h1s == 1, f'{path}: expected one title and h1'
        for ref in page.refs:
            url = urlsplit(ref)
            if url.scheme or url.netloc:
                continue
            assert not url.path.startswith('/'), f'{path}: project Pages needs relative URLs: {ref}'
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if target.is_dir():
                target /= 'index.html'
            assert target.is_relative_to(ROOT.resolve()), f'Outside public root: {ref}'
            assert target.is_file(), f'{path}: missing {ref}'
            if url.fragment and target in pages:
                assert url.fragment in pages[target].ids, f'{path}: missing anchor {ref}'
    forbidden = {'.env', '.git', 'forgeweb.db', 'manage.py'}
    for path in ROOT.rglob('*'):
        assert path.name not in forbidden, f'Private file in public artifact: {path}'
    print(f'PASS: {len(pages)} pages; local assets, links, anchors, metadata, public boundaries.')


if __name__ == '__main__':
    main()

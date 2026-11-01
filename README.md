# Health Assistant marketing website

A responsive, dependency-free public site with a local ForgeWeb content admin and
Ollama drafting. The public site is `website/`; admin tools and model settings stay
on the author’s computer. The iOS app source in the parent directory is untouched.

## Preview the site

```sh
python3 -m http.server 4173 --bind 127.0.0.1 --directory website
```

Open http://127.0.0.1:4173/. No build step, external fonts, trackers, or API keys.

## Manage with ForgeWeb

```sh
bash scripts/setup.sh
.venv/bin/python scripts/manage.py
```

Open http://127.0.0.1:8000/admin/ for ForgeWeb, or http://127.0.0.1:8000/ for the site.
The launcher registers Home and Privacy as drafts without rewriting their HTML.
Use the page editor’s **Open** control to select `index.html` or `privacy.html`.
Preview edits and save deliberately. Avoid the upstream site-setup generator on
this custom site: it generates replacement pages.

The upstream checkout is pinned in `forgeweb.json` and ignored as recommended by
ForgeWeb’s folder-based architecture; it is an independent nested Git repository,
not a submodule. `setup.sh` reproduces it. The launcher uses upstream’s supported
`WEBSITE_ROOT` override because the current server otherwise defaults to `docs/`.
Site settings and page metadata are in ignored `ForgeWeb/admin/forgeweb.db`.

## Local AI content drafting

Ollama must be running and have a model installed. No model is bundled, and the
initial machine inspection found no installed models. Choose a model appropriate
for your machine and review its license. For example, after installing a suitable
model, run:

```sh
ollama serve
# In a separate terminal, use the EXACT model name shown by ollama list:
OLLAMA_MODEL=your-installed-model .venv/bin/python scripts/manage.py
```

If Ollama’s desktop app already runs the service, do not start a second server.
The default model name is `llama3.2:3b`; change it with `OLLAMA_MODEL`. The default
endpoint is `http://127.0.0.1:11434`; `OLLAMA_ENDPOINT` may select another loopback
port. The launcher does not read `.env.example` automatically.

In ForgeWeb’s page editor choose **Ollama (Local)**. The launcher uses its environment
model/endpoint settings, overriding browser-stored settings so the request remains
local. It adds `content/editorial-brief.md` to the upstream model prompt and disables
paid provider calls in this site workflow. This is separate from the iOS app’s BYOT
feature, which the marketing site explains.

You can also request a draft through the same ForgeWeb API:

```sh
.venv/bin/python scripts/draft_content.py 'Draft a short HTML article about preparing questions for a doctor visit. Use only supported Health Assistant features.'
```

Drafts go to ignored `content/drafts/`, outside the published directory. Review
facts and HTML before copying content into the editor. No automatic publishing.
If the model is unavailable, the CLI fails explicitly and saves no draft. Upstream’s
editor may show built-in template suggestions after a model error; those are not
proof that local inference succeeded.

## Validate and publish

```sh
python3 scripts/check_site.py
python3 -m unittest discover -s tests
```

The GitHub Actions workflow deploys **only `website/`** on pushes to `main`, or
manual dispatch. In the target repository select Settings → Pages → GitHub Actions.
It does not upload ForgeWeb, its database, model settings, or draft content.
Relative asset URLs work on a GitHub Pages project path.

The requested origin is `https://github.com/open-build/health-assistant-web.git`.
The repository is accessible and its existing `main` history and LICENSE are
preserved. This independent local repository is on
`codex/health-assistant-marketing`, based on `origin/main`. The publishing workflow runs when website changes reach `main`.

Public site: https://open-build.github.io/health-assistant-web/
App Store availability is not claimed.

## Product review

See `content/editorial-brief.md` for sources and copy guardrails. Key distinctions:

- Open-weight models are available via user-configured local providers; Apple’s
  on-device model is a different option, and the app bundles no open-weight model.
- BYOT uses the app’s HTTPS OpenAI-compatible configuration; support depends on
  the chosen service. There is no universal paid-provider guarantee.
- The phone visual is a clearly labeled illustration with fictional data.
- No verified App Store link, shared caregiver accounts, or cloud sync is advertised.
- `privacy.html` describes architecture; it is not a release-specific legal policy.

ForgeWeb’s own license remains in `ForgeWeb/LICENSE.md`. App branding is copied
from the supplied iOS app. No license is inferred or changed for the app itself.

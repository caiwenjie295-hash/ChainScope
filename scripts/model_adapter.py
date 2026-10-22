"""Load config/model_registry.json and resolve API credentials for chat adapters.

Boundary:
- Default active_profile is deepseek (deepseek-flash baseline). Switch via
  CHAINSCOPE_MODEL_PROFILE=deepseek-pro (or edit active_profile) — no scattered literals.
- Profiles: deepseek (flash), deepseek-pro (API id deepseek-v4-pro), assistant (empty slot).
- Credential files: prefer deepseek_APIKEY.txt (underscore); fall back to the
  legacy spaced name if present. Env wins over files. Never print keys.
- Unconfigured profile (missing base_url/model/key) is a hard error at call time,
  never a silent fallback to deepseek.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from probe import ROOT, CREDENTIALS

REGISTRY_PATH = ROOT / 'config' / 'model_registry.json'


def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding='utf-8'))


def active_profile_name(registry: dict | None = None) -> str:
    reg = registry or load_registry()
    return (os.getenv('CHAINSCOPE_MODEL_PROFILE') or reg.get('active_profile') or 'deepseek').strip()


def get_profile(name: str | None = None) -> dict:
    reg = load_registry()
    profile_name = name or active_profile_name(reg)
    profiles = reg.get('profiles') or {}
    if profile_name not in profiles:
        raise KeyError(f'unknown model profile: {profile_name}')
    profile = dict(profiles[profile_name])
    profile['_name'] = profile_name
    return profile


def resolve_api_key(profile: dict | None = None) -> str:
    """Env first, then api_key_files in order (underscore before spaced legacy)."""
    profile = profile or get_profile()
    env_name = profile.get('api_key_env') or 'DEEPSEEK_API_KEY'
    env_val = os.getenv(env_name)
    if env_val and env_val.strip():
        return env_val.strip()
    files = list(profile.get('api_key_files') or [])
    # Always try underscore then spaced deepseek names if profile did not list them.
    if env_name == 'DEEPSEEK_API_KEY':
        for legacy in ('deepseek_APIKEY.txt', 'deepseek APIKEY.txt'):
            if legacy not in files:
                files.append(legacy)
    tried = []
    for name in files:
        path = CREDENTIALS / name
        tried.append(str(path))
        if path.is_file():
            return path.read_text(encoding='utf-8-sig').strip()
    raise FileNotFoundError(
        f"API key not found for profile {profile.get('_name')}: "
        f"set {env_name} or place one of {files} under {CREDENTIALS}"
    )


def require_chat_endpoint(profile: dict | None = None) -> dict:
    """Return profile with base_url and model required for an online call."""
    profile = profile or get_profile()
    base = profile.get('base_url')
    model = profile.get('model')
    if not base or not model:
        raise RuntimeError(
            f"model profile {profile.get('_name')!r} is not configured "
            f"(base_url={base!r}, model={model!r}); set them in "
            f"config/model_registry.json before an online run"
        )
    return profile


def model_name(profile: dict | None = None) -> str:
    return require_chat_endpoint(profile)['model']

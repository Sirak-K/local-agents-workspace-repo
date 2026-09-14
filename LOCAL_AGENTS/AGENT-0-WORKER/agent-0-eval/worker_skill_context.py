"""Hash-bound local-candidate skill exposure, distinct from Codex skills."""
import hashlib
from pathlib import Path

from json_document_comparison import parse_json_document

SKILLS = Path(__file__).resolve().parents[1] / "agent-0-skills"


def _read(path, limit):
    if path.is_symlink() or path.parent.is_symlink() or path.resolve() != path.absolute():
        raise ValueError("skill link denied")
    with path.open("rb") as handle:
        body = handle.read(limit + 1)
    if len(body) > limit or body.startswith(b"\xef\xbb\xbf"):
        raise ValueError("skill byte or encoding budget")
    return body


def expose_skills(mode: str, identifier: str | None = None) -> dict:
    if mode not in ("none", "explicit", "discovery") or (mode == "explicit") != bool(identifier):
        raise ValueError("invalid skill exposure contract")
    if mode == "none":
        return {"mode": mode, "system_text": "", "skills": [], "catalog_sha256": None}
    body = _read(SKILLS / "skill_catalog.json", 8192)
    catalog = parse_json_document(body.decode("utf-8"))
    entries = catalog.get("skills", [])
    if (catalog.get("version") != 1 or not 2 <= len(entries) <= 3
            or not all(isinstance(item, dict) and isinstance(item.get("id"), str) for item in entries)
            or len({item["id"] for item in entries}) != len(entries)):
        raise ValueError("invalid skill catalog")
    selected = []
    for item in entries:
        if item.get("file") != item["id"] + "/SKILL.md" or not item["id"].replace("_", "").isalnum():
            raise ValueError("skill path does not match identity")
        content = _read(SKILLS / item["file"], 4096)
        if hashlib.sha256(content).hexdigest() != item.get("sha256"):
            raise ValueError("skill changed from the locked hash")
        if mode == "discovery" or item["id"] == identifier:
            selected.append(item | {"content": content.decode("utf-8")})
    if not selected:
        raise ValueError("requested skill is not in the catalog")
    if mode == "explicit":
        text = "\n\nExplicit WORKER skill source:\n" + selected[0]["content"]
    else:
        text = "\n\nAvailable WORKER skills. Use read_worker_skill to retrieve a relevant procedure if needed:\n"
        text += "\n".join(item["id"] + ": " + item["description"] for item in selected)
    return {"mode": mode, "system_text": text, "skills": selected,
            "catalog_sha256": hashlib.sha256(body).hexdigest()}

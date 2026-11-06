"""G3-3 GitHub-only remote digest custody. Never a scientific execution entry point.

A real seal is a non-force commit/push to an explicitly selected audit branch,
followed by ref and *pinned remote commit content* readback. Unit tests use an
in-memory fault injector, not an actual GitHub push. GitHub history is not an
independent timestamp authority and privileged users can rewrite its history.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
import subprocess

SHA40 = re.compile(r"[0-9a-f]{40}\Z")
SHA64 = re.compile(r"[0-9a-f]{64}\Z")
BRANCH = re.compile(r"audit/r2ma/[a-z0-9][a-z0-9-]{2,63}\Z")


class CustodyBlocked(RuntimeError):
    """Remote custody failure must prevent the protected next action."""


@dataclass(frozen=True, slots=True)
class RemoteReceipt:
    commit_sha: str
    remote_ref: str
    path: str
    content_sha256: str
    remote_url: str

    def __post_init__(self) -> None:
        if (type(self.commit_sha) is not str or not SHA40.fullmatch(self.commit_sha)
                or type(self.content_sha256) is not str
                or not SHA64.fullmatch(self.content_sha256)
                or type(self.path) is not str
                or not self.path.startswith("audit/r2ma/")
                or ".." in Path(self.path).parts
                or type(self.remote_ref) is not str
                or not self.remote_ref.startswith("refs/heads/audit/r2ma/")
                or type(self.remote_url) is not str
                or not self.remote_url):
            raise CustodyBlocked("RUN_BLOCK: malformed remote receipt")

    def as_dict(self) -> dict[str, str]:
        return {
            "commit_sha": self.commit_sha, "remote_ref": self.remote_ref,
            "path": self.path, "content_sha256": self.content_sha256,
            "remote_url": self.remote_url,
        }


class GitHubRemoteCustody:
    """GitHub repo working tree on an isolated audit branch; no force push.

    This object is evaluator/parent-only. Its use needs independent future
    authorization for a real run. It does not decide whether G4/G5/G6 may run.
    """

    def __init__(self, checkout: str | Path, *, branch: str,
                 repo_slug: str = "ryonakayama234/DekaSugi"):
        self.checkout = Path(checkout).resolve(strict=True)
        if (type(branch) is not str or not BRANCH.fullmatch(branch)
                or type(repo_slug) is not str
                or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo_slug)):
            raise CustodyBlocked("RUN_BLOCK: explicit GitHub audit branch required")
        self.ref = "refs/heads/" + branch
        self.slug = repo_slug
        if self._git("rev-parse", "--show-toplevel").strip() != str(self.checkout):
            raise CustodyBlocked("RUN_BLOCK: checkout root mismatch")
        if self._git("symbolic-ref", "HEAD").strip() != self.ref:
            raise CustodyBlocked("RUN_BLOCK: wrong checkout branch")
        url = self._git("remote", "get-url", "origin").strip()
        accepted = (
            "https://github.com/" + repo_slug + ".git",
            "https://github.com/" + repo_slug,
            "git@github.com:" + repo_slug + ".git",
            "ssh://git@github.com/" + repo_slug + ".git",
        )
        if url not in accepted:
            raise CustodyBlocked("RUN_BLOCK: origin must be exact GitHub repository")
        self.remote_url = "https://github.com/" + repo_slug

    def _git(self, *args: str) -> str:
        try:
            p = subprocess.run(
                ["git", "-C", str(self.checkout), *args],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=45, text=True,
            )
            return p.stdout
        except (subprocess.SubprocessError, OSError) as exc:
            raise CustodyBlocked("RUN_BLOCK: remote Git custody failed") from exc

    def _relative(self, source: Path) -> str:
        if source.is_symlink() or not source.is_file():
            raise CustodyBlocked("RUN_BLOCK: missing or symlinked custody artifact")
        try:
            rel = source.resolve(strict=True).relative_to(self.checkout).as_posix()
        except (ValueError, OSError) as exc:
            raise CustodyBlocked("RUN_BLOCK: artifact outside checkout") from exc
        if not rel.startswith("audit/r2ma/"):
            raise CustodyBlocked("RUN_BLOCK: only isolated audit paths may be published")
        return rel

    def _read_commit(self, commit_sha: str, rel: str) -> bytes:
        # git show in text mode is forbidden: exact UTF-8 bytes are pinned.
        try:
            return subprocess.run(
                ["git", "-C", str(self.checkout), "show", commit_sha + ":" + rel],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=45,
            ).stdout
        except (subprocess.SubprocessError, OSError) as exc:
            raise CustodyBlocked("RUN_BLOCK: remote pinned-object readback failed") from exc

    def commit_and_verify(self, source: Path, content_sha256: str) -> RemoteReceipt:
        rel = self._relative(source)
        data = source.read_bytes()
        if type(content_sha256) is not str or sha256(data).hexdigest() != content_sha256:
            raise CustodyBlocked("RUN_BLOCK: local artifact digest mismatch")
        # Refuse accidental inclusion of unrelated staged contents.
        if self._git("diff", "--cached", "--name-only").strip():
            raise CustodyBlocked("RUN_BLOCK: Git index must be clean before remote seal")
        self._git("add", "--", rel)
        self._git("commit", "-m", "R2-M-A custody seal: " + content_sha256, "--only", "--", rel)
        head = self._git("rev-parse", "HEAD").strip()
        if not SHA40.fullmatch(head) or self._read_commit(head, rel) != data:
            raise CustodyBlocked("RUN_BLOCK: locally committed bytes differ")
        self._git("push", "--porcelain", "origin", "HEAD:" + self.ref)
        remote = self._git("ls-remote", "--exit-code", "origin", self.ref).splitlines()
        if len(remote) != 1 or remote[0].split() != [head, self.ref]:
            raise CustodyBlocked("RUN_BLOCK: remote ref readback mismatch")
        receipt = RemoteReceipt(head, self.ref, rel, content_sha256, self.remote_url)
        self.verify_receipt(receipt, source)
        return receipt

    def verify_receipt(self, receipt: RemoteReceipt, source: Path) -> None:
        if type(receipt) is not RemoteReceipt or receipt.remote_ref != self.ref:
            raise CustodyBlocked("RUN_BLOCK: receipt branch mismatch")
        if receipt.remote_url != self.remote_url or receipt.path != self._relative(source):
            raise CustodyBlocked("RUN_BLOCK: receipt target mismatch")
        data = source.read_bytes()
        if sha256(data).hexdigest() != receipt.content_sha256:
            raise CustodyBlocked("RUN_BLOCK: custody artifact changed since sealing")
        # Fetch the pinned commit from GitHub, not only the local commit cache.
        self._git("fetch", "--no-tags", "origin", receipt.commit_sha)
        got = self._git("rev-parse", "FETCH_HEAD").strip()
        if got != receipt.commit_sha or self._read_commit(got, receipt.path) != data:
            raise CustodyBlocked("RUN_BLOCK: remote commit/bytes do not match")

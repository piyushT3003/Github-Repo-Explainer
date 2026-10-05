from pathlib import Path
import shutil
import tempfile
from urllib.parse import urlparse
from zipfile import ZipFile

import requests

try:
    import git
    GITPYTHON_AVAILABLE = True
    GITPYTHON_IMPORT_ERROR = None
except Exception as exc:
    GITPYTHON_AVAILABLE = False
    GITPYTHON_IMPORT_ERROR = str(exc)

MAX_FILE_SIZE = 150_000
MAX_TOTAL_CODE = 100_000
REQUEST_TIMEOUT = 120

SOURCE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".h",
    ".cpp", ".hpp", ".cs", ".go", ".rs", ".php", ".rb", ".swift",
    ".kt", ".kts", ".sql", ".html", ".css", ".scss", ".vue",
    ".dart", ".r", ".R", ".sh"
}

READABLE_EXTENSIONS = SOURCE_EXTENSIONS | {
    ".yaml", ".yml", ".json", ".xml", ".toml", ".ini", ".md", ".txt",
    ".cfg", ".conf"
}

IGNORED_DIRS = {
    ".git", ".github", ".idea", ".vscode", "node_modules",
    "__pycache__", ".venv", "venv", "env", "dist", "build",
    "target", "coverage", ".next", ".pytest_cache",
    ".mypy_cache", ".tox", "vendor"
}

IGNORED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf",
    ".zip", ".rar", ".7z", ".exe", ".dll", ".so", ".dylib",
    ".bin", ".mp3", ".mp4", ".mov", ".avi", ".woff", ".woff2",
    ".ttf", ".otf", ".lock", ".pyc"
}

IMPORTANT_EXTENSIONLESS_FILES = {
    "README", "Dockerfile", "Makefile", "Procfile"
}

IMPORTANT_NAMED_FILES = {
    "requirements.txt", "pyproject.toml", "package.json"
}


def parse_github_url(repo_url: str):
    parsed = urlparse(repo_url)
    hostname = (parsed.hostname or "").lower()

    if parsed.scheme not in {"http", "https"} or hostname not in {
        "github.com",
        "www.github.com",
    }:
        raise ValueError(
            "Please enter a valid public GitHub repository URL such as "
            "https://github.com/username/repository"
        )

    parts = [p for p in parsed.path.strip("/").split("/") if p]
    if len(parts) < 2:
        raise ValueError(
            "The URL must contain both an owner and repository name."
        )

    return parts[0], parts[1].removesuffix(".git")


def github_metadata(owner: str, repo: str) -> dict:
    url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        response = requests.get(
            url,
            headers={"Accept": "application/vnd.github+json"},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not reach GitHub: {exc}") from exc

    if response.status_code == 404:
        raise RuntimeError(
            "GitHub repository was not found. Make sure it is public "
            "and the URL is correct."
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub API returned HTTP {response.status_code}."
        )

    return response.json()


def _git_clone(
    repo_url: str,
    branch: str,
    destination: Path,
) -> Path | None:
    """
    Primary acquisition path required by the project:
    GitPython clone_from().
    """
    if not GITPYTHON_AVAILABLE:
        return None

    try:
        git.Repo.clone_from(
            repo_url,
            destination,
            branch=branch,
            depth=1,
        )
        return destination
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        return None


def _archive_download(
    owner: str,
    repo: str,
    branch: str,
    destination: Path,
) -> Path:
    """
    Safe fallback when GitPython cannot access a system Git executable.
    It keeps the application usable on machines without Git installed.
    """
    archive_url = (
        f"https://codeload.github.com/{owner}/{repo}/zip/refs/heads/{branch}"
    )

    try:
        response = requests.get(
            archive_url,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not download the GitHub repository: {exc}"
        ) from exc

    if response.status_code != 200:
        raise RuntimeError(
            f"Could not download repository archive "
            f"(HTTP {response.status_code})."
        )

    archive_path = destination / "repository.zip"
    archive_path.write_bytes(response.content)

    extract_dir = destination / "repository"

    try:
        with ZipFile(archive_path, "r") as archive:
            archive.extractall(extract_dir)
    except Exception as exc:
        raise RuntimeError(
            f"Could not extract the repository archive: {exc}"
        ) from exc

    folders = [p for p in extract_dir.iterdir() if p.is_dir()]
    if len(folders) == 1:
        return folders[0]

    return extract_dir


def acquire_repository(
    repo_url: str,
    owner: str,
    repo: str,
    branch: str,
    workspace: Path,
) -> tuple[Path, str]:
    """
    Returns (repository_path, method).
    GitPython is the primary method; public ZIP download is the fallback.
    """
    clone_target = workspace / "cloned_repository"
    clone_target.mkdir(parents=True, exist_ok=True)

    cloned = _git_clone(repo_url, branch, clone_target)
    if cloned is not None:
        return cloned, "GitPython clone"

    return (
        _archive_download(owner, repo, branch, workspace),
        "GitHub archive fallback",
    )


def _read_files(repo_dir: Path) -> dict:
    files = []
    total_chars = 0

    for path in sorted(repo_dir.rglob("*")):
        if not path.is_file():
            continue

        relative = path.relative_to(repo_dir)

        if any(part in IGNORED_DIRS for part in relative.parts):
            continue

        if path.suffix.lower() in IGNORED_EXTENSIONS:
            continue

        accepted = (
            path.suffix in READABLE_EXTENSIONS
            or path.name in IMPORTANT_EXTENSIONLESS_FILES
            or path.name in IMPORTANT_NAMED_FILES
        )

        if not accepted:
            continue

        try:
            if path.stat().st_size > MAX_FILE_SIZE:
                continue

            content = path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except (OSError, UnicodeError):
            continue

        remaining = MAX_TOTAL_CODE - total_chars
        if remaining <= 0:
            break

        content = content[:remaining]

        is_source = (
            path.suffix in SOURCE_EXTENSIONS
            or path.name in {"Dockerfile", "Makefile", "Procfile"}
        )

        files.append(
            {
                "path": str(relative).replace("\\", "/"),
                "content": content,
                "extension": path.suffix.lower(),
                "is_source": is_source,
                "lines": len(content.splitlines()),
            }
        )

        total_chars += len(content)

    return {
        "files": files,
        "files_analyzed": len(files),
        "source_files": sum(1 for item in files if item["is_source"]),
        "lines_of_code": sum(
            item["lines"] for item in files if item["is_source"]
        ),
    }


def analyze_repository(repo_url: str) -> dict:
    owner, repo = parse_github_url(repo_url)
    metadata = github_metadata(owner, repo)
    branch = metadata.get("default_branch") or "main"

    workspace = Path(
        tempfile.mkdtemp(prefix="github_code_explainer_")
    )

    try:
        repo_dir, acquisition_method = acquire_repository(
            repo_url,
            owner,
            repo,
            branch,
            workspace,
        )

        file_data = _read_files(repo_dir)

        readme = ""
        for item in file_data["files"]:
            if Path(item["path"]).name.lower() in {
                "readme",
                "readme.md",
                "readme.txt",
            }:
                readme = item["content"][:12000]
                break

        if not file_data["files"]:
            raise ValueError(
                "The repository contains no readable source-code, "
                "documentation, or configuration files."
            )

        return {
            "repository": repo,
            "owner": owner,
            "full_name": metadata.get(
                "full_name",
                f"{owner}/{repo}",
            ),
            "html_url": metadata.get(
                "html_url",
                repo_url,
            ),
            "default_branch": branch,
            "description": metadata.get(
                "description"
            ) or "No description provided.",
            "stars": metadata.get(
                "stargazers_count",
                0,
            ),
            "forks": metadata.get(
                "forks_count",
                0,
            ),
            "language": metadata.get(
                "language"
            ) or "N/A",
            "updated_at": metadata.get("updated_at"),
            "repo_type": (
                "Code"
                if file_data["source_files"] > 0
                else "Documentation"
            ),
            "acquisition_method": acquisition_method,
            "readme": readme,
            **file_data,
        }
    finally:
        shutil.rmtree(workspace, ignore_errors=True)

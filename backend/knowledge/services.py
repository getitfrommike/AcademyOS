from __future__ import annotations

import hashlib
import os
import uuid
from pathlib import Path
from typing import BinaryIO

from django.conf import settings
from django.db import transaction

from .models import KnowledgeSource, Workspace
from .validators import validate_upload


class KnowledgeUploadError(Exception):
    """Raised when a knowledge upload cannot be stored safely."""


def _safe_extension(filename: str) -> str:
    """
    Return a normalized file extension.

    The original filename is never used as the server-side filename.
    """

    return Path(filename).suffix.lower()


def _build_storage_names(original_filename: str) -> tuple[str, str]:
    """
    Generate a random server-side filename and relative storage key.

    Example:
        stored_filename:
            52ce11d0-8ee4-4b82-8515-f27579f1fef6.pdf

        storage_key:
            quarantine/52ce11d0-8ee4-4b82-8515-f27579f1fef6.pdf
    """

    extension = _safe_extension(original_filename)
    stored_filename = f"{uuid.uuid4()}{extension}"
    storage_key = Path("quarantine") / stored_filename

    return stored_filename, storage_key.as_posix()


def _resolve_quarantine_path(stored_filename: str) -> Path:
    """
    Build and verify the absolute quarantine destination.

    The containment check prevents a future programming mistake from
    writing files outside the quarantine directory.
    """

    quarantine_root = Path(settings.QUARANTINE_UPLOAD_ROOT).resolve()
    quarantine_root.mkdir(parents=True, exist_ok=True, mode=0o700)

    destination = (quarantine_root / stored_filename).resolve()

    try:
        destination.relative_to(quarantine_root)
    except ValueError as exc:
        raise KnowledgeUploadError(
            "The generated upload destination is invalid."
        ) from exc

    return destination


def _write_upload_and_hash(
    uploaded_file: BinaryIO,
    destination: Path,
) -> tuple[int, str]:
    """
    Stream the upload to disk while calculating its SHA-256 digest.

    The complete file is never loaded into memory.
    """

    digest = hashlib.sha256()
    bytes_written = 0

    try:
        with destination.open("xb") as output_file:
            for chunk in uploaded_file.chunks():
                if not chunk:
                    continue

                output_file.write(chunk)
                digest.update(chunk)
                bytes_written += len(chunk)

        os.chmod(destination, 0o600)

    except FileExistsError as exc:
        raise KnowledgeUploadError(
            "The generated upload filename already exists."
        ) from exc

    except OSError as exc:
        destination.unlink(missing_ok=True)
        raise KnowledgeUploadError(
            "The upload could not be written to quarantine storage."
        ) from exc

    return bytes_written, digest.hexdigest()


@transaction.atomic
def create_quarantined_source(
    *,
    workspace: Workspace,
    uploaded_file,
) -> KnowledgeSource:
    """
    Store an uploaded file in private quarantine storage and create its
    KnowledgeSource database record.

    Security properties:
    - The upload is validated before any filesystem write.
    - The client filename is never used as the stored filename.
    - The file is streamed instead of fully loaded into memory.
    - A SHA-256 digest is computed during the write.
    - The upload receives restrictive filesystem permissions.
    - Only a relative storage key is stored in the database.
    - Filesystem cleanup occurs if database creation fails.
    """

    validate_upload(
        uploaded_file=uploaded_file,
        workspace=workspace,
    )

    original_filename = Path(uploaded_file.name).name
    stored_filename, storage_key = _build_storage_names(original_filename)
    destination = _resolve_quarantine_path(stored_filename)

    try:
        bytes_written, sha256_digest = _write_upload_and_hash(
            uploaded_file,
            destination,
        )

        source = KnowledgeSource.objects.create(
            workspace=workspace,
            original_filename=original_filename,
            stored_filename=stored_filename,
            storage_key=storage_key,
            file_extension=_safe_extension(original_filename),
            declared_mime_type=(
                getattr(uploaded_file, "content_type", "") or ""
            ),
            detected_mime_type="",
            file_size_bytes=bytes_written,
            sha256=sha256_digest,
            status=KnowledgeSource.Status.QUARANTINED,
        )

    except Exception:
        destination.unlink(missing_ok=True)
        raise

    return source
from pathlib import Path

from django.conf import settings
from rest_framework.exceptions import ValidationError


def validate_file_size(uploaded_file):
    """
    Reject empty files and files larger than the configured maximum.
    """

    if uploaded_file.size <= 0:
        raise ValidationError(
            "Empty files are not permitted."
        )

    max_size = settings.KNOWLEDGE_UPLOAD_MAX_BYTES

    if uploaded_file.size > max_size:
        raise ValidationError(
            f"Maximum upload size is {max_size // (1024 * 1024)} MB."
        )


def validate_extension(uploaded_file):
    """
    Reject file extensions that are not explicitly allowed.
    """

    filename = Path(uploaded_file.name).name
    extension = Path(filename).suffix.lower()

    if not extension:
        raise ValidationError(
            "The uploaded file must have a valid file extension."
        )

    if extension not in settings.KNOWLEDGE_ALLOWED_EXTENSIONS:
        raise ValidationError(
            f'Files of type "{extension}" are not permitted.'
        )


def validate_workspace_limit(workspace):
    """
    Reject uploads when the workspace has reached its configured file limit.
    """

    source_count = workspace.knowledge_sources.count()
    max_files = settings.KNOWLEDGE_MAX_FILES_PER_WORKSPACE

    if source_count >= max_files:
        raise ValidationError(
            f"This workspace may contain no more than {max_files} files."
        )


def validate_upload(*, uploaded_file, workspace):
    """
    Run all upload validation checks.
    """

    validate_file_size(uploaded_file)
    validate_extension(uploaded_file)
    validate_workspace_limit(workspace)
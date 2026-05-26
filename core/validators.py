import re

from django.core.exceptions import ValidationError

GITHUB_RE = re.compile(r'^https?://(www\.)?github\.com/', re.IGNORECASE)


def validate_github_url(value: str) -> None:
    if value and not GITHUB_RE.match(value):
        raise ValidationError('Ссылка должна вести на GitHub (github.com).')

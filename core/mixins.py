from .validators import validate_github_url


class GithubUrlMixin:
    def clean_github_url(self):
        value = self.cleaned_data.get('github_url', '')
        validate_github_url(value)
        return value

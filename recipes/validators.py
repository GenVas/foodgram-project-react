from django.core import validators
import re


class slug_regex_validator(validators.RegexValidator):
    regex = r'^[-a-zA-Z0-9_]+$'
    message = (
        'Enter a valid slug name. This value may contain only English letters, '
        'numbers, and ^[-a-zA-Z0-9_]+$ characters.'
    )
    flags = re.ASCII


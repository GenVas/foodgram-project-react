import re

from django.core import validators


class SlugRegexValidator(validators.RegexValidator):
    '''Custom validator for slug fild of Tag Model'''
    regex = r'^[-a-zA-Z0-9_]+$'
    message = (
        '''Enter a valid slug name. This value may contain
        only English letters, numbers, and ^[-a-zA-Z0-9_]+$ characters.'''
    )
    flags = re.ASCII

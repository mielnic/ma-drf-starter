from django.core.exceptions import ValidationError
from django.conf import settings

mdomain = settings.REGISTRATION_DOMAIN

def validate_email_domain(email):
    if not mdomain in email:
        raise ValidationError(f'Only {mdomain} mails are accepted.')
    else:
        return email
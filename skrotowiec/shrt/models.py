import logging
import random
import string

from django.db import IntegrityError, models

MAX_SHORTENED_LENGTH = 256
MAX_PK_COMMIT_RETRIES = 3
ALLOWED_CHARACTERS = tuple(set(string.printable) - set(string.whitespace))

log = logging.getLogger(__name__)
random.seed()

def generate_short_pk(length:int) -> str:
    """Returns short random string

    Since example short URL in requirements is composed from characters that
    need to be escaped for URL, this function doesn't care about that also.
    """
    return ''.join(
        random.choice(ALLOWED_CHARACTERS)
        for _ in range(length)
    )

def generate_unique_pk(max_length:int=MAX_SHORTENED_LENGTH) -> str:
    """Returns a unique short random string

    The uniqueness is not guaranteed -- caller has to handle  UNIQUE violations.

    A possible improvement to this algorithm would be to use a cartesian product
    generator `itertools.product(ALLOWED_CHARACTERS)` and try to actively use
    whole set of possible short urls. This would probably need
    a separate service that keeps track of available short pks. Seems outside of
    scope for this assignment.
    """
    if max_length < 1:
        raise ValueError("max_length must be greater than 0")
    for i in range(1, max_length+1):
        pk: str = generate_short_pk(length=i)
        if not ShortenedURL.objects.filter(pk=pk).exists():
            log.debug("Generated pk. pk=%r, tries=%r", pk, i)
            return pk
    raise ShortenedURL.ModelError("Couldn't generate unique pk")


class ShortenedURL(models.Model):
    short = models.CharField(max_length=MAX_SHORTENED_LENGTH, primary_key=True)
    full = models.URLField(max_length=2048)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


    class Meta:
        pass


    class ModelError(Exception):
        """Generic exception for ShortenedURL model"""


    def save(self, *args, **kwargs) -> None:
        if self.pk:  # type: ignore
            return super().save(*args, **kwargs)
        for _ in range(MAX_PK_COMMIT_RETRIES):
            log.info("Saving shortened url. pk=%r, full=%r", self.pk, self.full)  # type: ignore
            try:
                self.pk: str | None = generate_unique_pk()
                return super().save(*args, **kwargs)
            except IntegrityError:
                # Assuming that only uniqueness of `short` field failed

                # Could handle error code for a specific DB.
                # e.pgcode == 23505 for PostgreSQL
                log.info(
                    "Saving shortened url failed. pk=%r, full=%r",
                    self.pk, self.full,
                    exc_info=True
                )
                continue
        # Attempt to unset pk
        self.pk = None
        raise

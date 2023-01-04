from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


class CustomAccessToken(AccessToken):
    def check_iat(self, claim="iat"):
        """
        Checks whether token's `iat` claim is present in the token payload or not.
        If not, token will be invalid.

        Raises a TokenError with a user-facing error message if so.
        """

        try:
            self.payload[claim]
        except KeyError:
            raise TokenError(_(f"Token has no '{claim}' claim"))

    def verify(self):
        super().verify()
        self.check_iat()


class CustomRefreshToken(RefreshToken):
    access_token_class = CustomAccessToken

    @classmethod
    def for_user(cls, user):
        """
        Returns an authorization token for the given user that will be provided
         after authenticating the user's credentials.
        """
        token = super().for_user(user)
        token["iat"] = timezone.now()
        return token

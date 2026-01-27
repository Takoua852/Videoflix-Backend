from django.contrib.auth.tokens import PasswordResetTokenGenerator

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Token generator for account activation emails.
    """
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_active}"

class PasswordResetTokenGeneratorCustom(PasswordResetTokenGenerator):
    """
    Token generator for password reset emails.
    """
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.password}{user.last_login}"
    
account_activation_token = AccountActivationTokenGenerator()
password_reset_token = PasswordResetTokenGeneratorCustom()
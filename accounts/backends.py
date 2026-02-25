from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    """
    Custom authentication backend for email-based login.
    Accepts both 'username' and 'email' parameters for compatibility.
    """
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        # Support both 'email' and 'username' parameters
        email_to_use = email or username
        
        if email_to_use is None or password is None:
            return None
        
        try:
            user = User.objects.get(email=email_to_use)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            User().set_password(password)
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
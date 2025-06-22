import random
import string
import base64
from users.models import UserActivation  # Using your project's model path

def create_secret_key(length, instance):
    """Generate a random secret key and store it in UserActivation."""
    letters = string.ascii_letters
    text = ''.join(random.choice(letters) for _ in range(length))  
    secret_key = base64.b64encode(text.encode()).decode()  

    user_activation, _ = UserActivation.objects.get_or_create(user=instance)
    user_activation.activation_token = secret_key
    user_activation.is_expired = False
    user_activation.activated = False
    user_activation.save()

    return secret_key  

def get_secret_key(instance):
    """Decode and retrieve the original text from the stored secret key."""
    if instance.activation_token:
        return base64.b64decode(instance.activation_token).decode()
    return None  

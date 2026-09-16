from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': ("Неверное имя пользователя или пароль."),
        'inactive': ("Этот аккаунт не активен."),
    }
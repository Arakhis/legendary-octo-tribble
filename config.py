from defer import babel
from flask import request

LANGUAGES = {
    'en': 'English',
    'ru': 'Русский',
    'tr': 'Turkce'
}

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())
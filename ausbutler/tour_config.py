from .config import load_config
from .db import get_session
from .model import Translation, Admin

session = get_session()

class Translations(object):

    translation_cache = { t.id: t.dane for t
                          in session.query(Translation).all() }
    translation_mapping = load_config('logoh')
    custom_translations = load_config('translations')

    @staticmethod
    def get_translation(key):
        if key in Translations.translation_mapping:
            return Translations.translation_cache[Translations.translation_mapping[key]]
        if key in Translations.custom_translations:
            return Translations.custom_translations[key][Translations.detect_language()]
        return '{{%s}}' % (key)

    @staticmethod
    def detect_language():
        return 'en' if Translations.get_translation('ROUND').lower().strip() == 'round' else 'pl'

Constants = session.query(Admin).one()

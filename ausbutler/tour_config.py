from .config import load_config
from .db import get_session
from .model import Parameters, Translation

session = get_session(load_config('db'))


class Translations(object):

    translation_cache = {
        t.id: t.dane for t
        in session.query(Translation).all()
    }
    translation_mapping = load_config('logoh')
    custom_translations = load_config('translations')
    warned_missing_keys = []

    @staticmethod
    def get_translation(key):
        missing_logoh_key = False
        if key in Translations.translation_mapping:
            if Translations.translation_mapping[key] not in Translations.translation_cache:
                missing_logoh_key = True
            else:
                return Translations.translation_cache[
                    Translations.translation_mapping[key]]
        if key in Translations.custom_translations:
            return Translations.custom_translations[key][
                Translations.detect_language()]
        elif missing_logoh_key:
            if key not in Translations.warned_missing_keys:
                print 'WARNING: translation key "%s" not found in logoh table!' % (key)
                Translations.warned_missing_keys.append(key)
        return '{{%s}}' % (key)

    @staticmethod
    def detect_language():
        if Translations.get_translation('ROUND').lower().strip() == 'round':
            return 'en'
        else:
            return 'pl'

Constants = session.query(Parameters).one()

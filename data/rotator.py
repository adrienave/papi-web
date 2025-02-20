from logging import Logger

from common.config_reader import ConfigReader
from common.logger import get_logger
from data.screen import AScreen
from dataclasses import dataclass

logger: Logger = get_logger()


ROTATOR_DEFAULT_DELAY: int = 15


@dataclass(frozen=True)
class Rotator:
    id: str
    delay: int
    screens: list[AScreen]


class RotatorBuilder:
    def __init__(
            self, config_reader: ConfigReader,
            screens: dict[str, AScreen],
            screens_by_family_id: dict[str, list[AScreen]]):
        self._config_reader: ConfigReader = config_reader
        self._event_screens_by_family_id: dict[str, list[AScreen]] = screens_by_family_id
        self._event_screens: dict[str, AScreen] = screens
        self.rotators: dict[str, Rotator] = {}
        for rotator_id in self._read_rotator_ids():
            if rotator := self._build_rotator(rotator_id):
                self.rotators[rotator_id] = rotator
        if not self.rotators:
            self._config_reader.add_debug('aucun écran rotatif défini')

    def _read_rotator_ids(self) -> list[str]:
        rotator_ids: list[str] = self._config_reader.get_subsection_keys_with_prefix('rotator')
        if not rotator_ids:
            self._config_reader.add_debug('aucun écran rotatif déclaré', 'rotator.*')
        return rotator_ids

    def _build_rotator(self, rotator_id: str) -> Rotator | None:
        section_key = f'rotator.{rotator_id}'
        rotator_section = self._config_reader[section_key]
        section_keys: list[str] = ['screens', 'families', 'delay', ]
        for key in rotator_section:
            if key not in section_keys:
                self._config_reader.add_warning('option inconnue', section_key, key)
        key = 'delay'
        default_delay: int | None = ROTATOR_DEFAULT_DELAY
        delay: int = default_delay
        if key not in rotator_section:
            self._config_reader.add_debug(
                f'option absente, par défaut [{default_delay}]',
                section_key,
                key
            )
        else:
            delay = self._config_reader.getint_safe(section_key, key, minimum=1)
            if delay is None:
                self._config_reader.add_warning(
                    f'un entier positif non nul est attendu, par défaut '
                    f'[{default_delay}]',
                    section_key,
                    key
                )
        if 'screens' not in rotator_section and 'families' not in rotator_section:
            if rotator_id in self._event_screens_by_family_id:
                self._config_reader.add_info(
                    f'les options [screens] et [families] ne sont pas définies, '
                    f'utilisation de la famille [{rotator_id}] par défaut',
                    section_key
                )
                rotator_section['families'] = rotator_id
            elif len(self._event_screens_by_family_id) == 1:
                self._config_reader.add_info(
                    f'les options [screens] et [families] ne sont pas définies, '
                    f'utilisation par défaut de l\'unique famille [{rotator_id}] par défaut',
                    section_key
                )
                rotator_section['families'] = list(self._event_screens_by_family_id.keys())[0]
            else:
                self._config_reader.add_info(
                    'au moins une option parmi [screens] et [families] doit être '
                    'définie, écran rotatif ignoré',
                    section_key
                )
                return None
        rotator_screens: list[AScreen] = []
        key = 'families'
        if key in rotator_section:
            for family_id in str(rotator_section.get(key)).replace(' ', '').split(','):
                if family_id:
                    if family_id not in self._event_screens_by_family_id:
                        self._config_reader.add_warning(
                            f"la famille [{family_id}] n'existe pas, ignorée",
                            section_key,
                            key
                        )
                    else:
                        rotator_screens += self._event_screens_by_family_id[family_id]
        key = 'screens'
        if key in rotator_section:
            for screen_id in str(rotator_section.get(key)).replace(' ', '').split(','):
                if screen_id:
                    if screen_id not in self._event_screens:
                        self._config_reader.add_warning(
                            f"l'écran [{screen_id}] n'existe pas, ignoré",
                            section_key,
                            key
                        )
                    elif self._event_screens[screen_id] not in rotator_screens:
                        rotator_screens.append(self._event_screens[screen_id])

        if 'screens' not in rotator_section and 'families' not in rotator_section:
            self._config_reader.add_warning(
                'au moins une des deux options [screens] ou [families] doit '
                'être utilisée, écran rotatif ignoré',
                section_key
            )
            return None
        if not rotator_screens:
            self._config_reader.add_warning('aucun écran, écran rotatif ignoré', section_key, key)
            return None
        return Rotator(rotator_id, delay, rotator_screens)

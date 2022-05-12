from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from convoapp.models import Dialog
    from filterapp.models import RepairsFilterStageChoice
    from tgbot.models import BotUser


class BindableProtocol(Protocol):
    @property
    def dialog(self) -> "Dialog":
        ...

    @property
    def user(self) -> "BotUser":
        ...

    @property
    def stage_id(self) -> "RepairsFilterStageChoice":
        ...

    @stage_id.setter
    def stage_id(self, value: "RepairsFilterStageChoice"):
        ...

    def save(self):
        ...

    def get_service_name(self) -> int:
        ...

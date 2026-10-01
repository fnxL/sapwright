from dataclasses import dataclass


@dataclass
class StatusBarMsg:
    """The status bar message"""

    id: str
    type: str
    text: str
    number: str
    has_longtext: int
    is_popup: bool | None


@dataclass
class SessionInfo:
    """Session information"""

    application_server: str = ""
    client: str = ""
    codepage: int | None = None
    flushes: int | None = None
    group: str = ""
    gui_codepage: int | None = None
    i18n_mode: bool | None = None
    interpretation_time: int | None = None
    is_low_speed_connection: bool | None = None
    language: str = ""
    message_server: str = ""
    program: str = ""
    response_time: int | None = None
    round_trips: int | None = None
    screen_number: int | None = None
    scripting_mode_force_notification: bool | None = None
    scripting_mode_read_only: bool | None = None
    scripting_mode_recording_disabled: bool | None = None
    system_name: str = ""
    session_number: int | None = None
    system_session_id: str = ""
    transaction: str = ""
    ui_guideline: int | None = None
    user: str = ""

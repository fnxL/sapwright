from pydantic import BaseModel


class StatusBarMsg(BaseModel):
    """The status bar message"""

    id: str
    type: str
    text: str
    number: str
    has_longtext: int
    is_popup: bool | None


class SessionInfo(BaseModel):
    """Session information"""

    application_server: str
    client: str
    codepage: int
    flushes: int
    group: str
    gui_codepage: int
    i18n_mode: bool
    interpretation_time: int
    is_low_speed_connection: bool
    language: str
    message_server: str
    program: str
    response_time: int
    round_trips: int
    screen_number: int
    scripting_mode_read_only: bool
    scripting_mode_recording_disabled: bool
    session_number: int
    system_name: str
    system_session_id: str
    transaction: str
    ui_guideline: str
    user: str

from enum import IntEnum, StrEnum


class GuiComponentType(StrEnum):
    """
    A String Enum containing all SAP GUI Scripting Objects.
    The enum member names and their values are the original object names
    as used by the SAP Scripting API.

    Source: https://help.sap.com/docs/sap_gui_for_windows/b47d018c3b9b45e897fa
    f66a6c0885a8/a2e9357389334dc89eecc1fb13999ee3.html
    """

    GuiApplication = "GuiApplication"
    GuiBarChart = "GuiBarChart"
    GuiBox = "GuiBox"
    GuiButton = "GuiButton"
    GuiCalendar = "GuiCalendar"
    GuiChart = "GuiChart"
    GuiCheckBox = "GuiCheckBox"
    GuiCollection = "GuiCollection"
    GuiColorSelector = "GuiColorSelector"
    GuiComboBox = "GuiComboBox"
    GuiComboBoxControl = "GuiComboBoxControl"
    GuiComboBoxEntry = "GuiComboBoxEntry"
    GuiConnection = "GuiConnection"
    GuiContainer = "GuiContainer"
    GuiCTextField = "GuiCTextField"
    GuiContainerShell = "GuiContainerShell"
    GuiFrameWindow = "GuiFrameWindow"
    GuiGridView = "GuiGridView"
    GuiLabel = "GuiLabel"
    GuiMainWindow = "GuiMainWindow"
    GuiMenu = "GuiMenu"
    GuiMenubar = "GuiMenubar"
    GuiMessageWindow = "GuiMessageWindow"
    GuiModalWindow = "GuiModalWindow"
    GuiPasswordField = "GuiPasswordField"
    GuiPicture = "GuiPicture"
    GuiRadioButton = "GuiRadioButton"
    GuiScrollbar = "GuiScrollbar"
    GuiSession = "GuiSession"
    GuiSessionInfo = "GuiSessionInfo"
    GuiStatusbar = "GuiStatusbar"
    GuiTab = "GuiTab"
    GuiTableControl = "GuiTableControl"
    GuiTableColumn = "GuiTableColumn"
    GuiTableRow = "GuiTableRow"
    GuiTabStrip = "GuiTabStrip"
    GuiTextField = "GuiTextField"
    GuiTitlebar = "GuiTitlebar"
    GuiToolbar = "GuiToolbar"
    GuiTree = "GuiTree"
    GuiVComponent = "GuiVComponent"


class VKey(IntEnum):
    """SAP Virtual Key codes for keyboard simulation."""

    ENTER = 0
    F1 = 1
    F2 = 2
    F3 = 3
    F4 = 4
    F5 = 5
    F6 = 6
    F7 = 7
    F8 = 8
    F9 = 9
    F10 = 10
    CTRL_S = 11
    F12 = 12
    SHIFT_F1 = 13
    SHIFT_F2 = 14
    SHIFT_F3 = 15
    SHIFT_F4 = 16
    SHIFT_F5 = 17
    SHIFT_F6 = 18
    SHIFT_F7 = 19
    SHIFT_F8 = 20
    SHIFT_F9 = 21
    SHIFT_CTRL_0 = 22
    SHIFT_F11 = 23
    SHIFT_F12 = 24
    CTRL_F1 = 25
    CTRL_F2 = 26
    CTRL_F3 = 27
    CTRL_F4 = 28
    CTRL_F5 = 29
    CTRL_F6 = 30
    CTRL_F7 = 31
    CTRL_F8 = 32
    CTRL_F9 = 33
    CTRL_F10 = 34
    CTRL_F11 = 35
    CTRL_F12 = 36
    CTRL_SHIFT_F1 = 37
    CTRL_SHIFT_F2 = 38
    CTRL_SHIFT_F3 = 39
    CTRL_SHIFT_F4 = 40
    CTRL_SHIFT_F5 = 41
    CTRL_SHIFT_F6 = 42
    CTRL_SHIFT_F7 = 43
    CTRL_SHIFT_F8 = 44
    CTRL_SHIFT_F9 = 45
    CTRL_SHIFT_F10 = 46
    CTRL_SHIFT_F11 = 47
    CTRL_SHIFT_F12 = 48
    CTRL_E = 70
    CTRL_F = 71
    CTRL_SLASH = 72
    CTRL_BACKSLASH = 73
    CTRL_N = 74
    CTRL_O = 75
    CTRL_X = 76
    CTRL_C = 77
    CTRL_V = 78
    CTRL_Z = 79
    CTRL_PAGE_UP = 80
    PAGE_UP = 81
    PAGE_DOWN = 82
    CTRL_PAGE_DOWN = 83
    CTRL_G = 84
    CTRL_R = 85
    CTRL_P = 86

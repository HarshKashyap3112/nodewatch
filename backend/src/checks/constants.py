from enum import Enum


class CheckType(str, Enum):
    PROCESS_RUNNING = "process_running"
    PORT_OPEN = "port_open"
    DISK_SPACE = "disk_space"
    CUSTOM = "custom"


class CheckStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"

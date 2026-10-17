from enum import Enum

class SourceType(str, Enum):
    FILE = "file"
    GITHUB = "github"
    URL = "url"
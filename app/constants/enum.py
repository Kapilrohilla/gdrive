from enum import Enum


class TokenType(str, Enum):
    GUEST = "guest"
    ACCESS = "access"
    REFRESH = "refresh"


class VisitorIdentifierType(str, Enum):
    MAC_ADDRESS = "mac_address"
    UUID = "uuid"


class IdentityStatus(str, Enum):
    PENDING = "verification_pending"
    ACTIVE = "active"
    BLOCKED = "blocked"


class IdentityProvider(str, Enum):
    GITHUB = "github"
    GOOGLE = "google"
    LOCAL = "local"


class OutboxStatus(str, Enum):
    PENDING = "pending"
    ENQUEUED = "enqueued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AggregateType(str, Enum):
    FILE = "file"
    USER = "user"
    FOLDER = "folder"
    AUTH = "auth"


class IdentifierType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    USERNAME = "username"


class UserStatus(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"

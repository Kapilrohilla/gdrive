from enum import Enum, StrEnum


class TokenType(StrEnum):
    GUEST = "guest"
    ACCESS = "access"
    REFRESH = "refresh"


class VisitorIdentifierType(StrEnum):
    MAC_ADDRESS = "mac_address"
    UUID = "uuid"


class IdentityStatus(StrEnum):
    PENDING = "verification_pending"
    ACTIVE = "active"
    BLOCKED = "blocked"


class IdentityProvider(StrEnum):
    GITHUB = "github"
    GOOGLE = "google"
    LOCAL = "local"


class OutboxStatus(StrEnum):
    PENDING = "pending"
    ENQUEUED = "enqueued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AggregateType(StrEnum):
    FILE = "file"
    USER = "user"
    FOLDER = "folder"
    AUTH = "auth"
    SHORT_URL = "short_url"


class IdentifierType(StrEnum):
    EMAIL = "email"
    PHONE = "phone"
    USERNAME = "username"


class UserStatus(StrEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"


class ResourceEventActorType(StrEnum):
    USER = "user"
    VISITOR = "visitor"
    SYSTEM = "system"

class ResourceEventResourceType(StrEnum):
    FILE = "file"
    FOLDER = "folder"

class OutboxTopics(StrEnum):
    CREATE_RESOURCE_EVENT = "create_resource_event"
    GENERATE_FILE_THUMBNAIL = "generate_file_thumbnail"

class ResourceEventActions(StrEnum):
    CREATED = "created"
    VIEWED = "viewed"
    DOWNLOADED = "downloaded"
    UPDATED = "updated"
    MOVED = "moved"
    RENAMED = "renamed"
    SHARED = "shared"
    RESTORED = "restored"
    DELETED = "deleted"
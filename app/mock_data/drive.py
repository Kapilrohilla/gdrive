"""Mock drive data for frontend development."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

ME = {
    "id": "user-me",
    "name": "Me",
    "avatarUrl": "https://i.pravatar.cc/150?u=me",
    "isMe": True,
}

SARAH = {
    "id": "user-sarah",
    "name": "Sarah Chen",
    "avatarUrl": "https://i.pravatar.cc/150?u=sarah",
}

ALEX = {
    "id": "user-alex",
    "name": "Alex Rivera",
    "avatarUrl": "https://i.pravatar.cc/150?u=alex",
}

NOW = datetime(2026, 7, 19, 12, 0, 0)

FOLDERS = [
    {
        "id": "folder-projects",
        "name": "Projects",
        "kind": "folder",
        "itemCount": 12,
        "modifiedAt": (NOW - timedelta(days=2)).isoformat(),
        "modifiedLabel": "You modified · 2d ago",
        "owner": ME,
        "parentId": None,
    },
    {
        "id": "folder-travel",
        "name": "Travel Photos 2024",
        "kind": "folder",
        "itemCount": 248,
        "modifiedAt": (NOW - timedelta(days=5)).isoformat(),
        "modifiedLabel": "You modified · 5d ago",
        "owner": ME,
        "parentId": None,
    },
    {
        "id": "folder-client",
        "name": "Client Documents",
        "kind": "folder",
        "itemCount": 56,
        "modifiedAt": (NOW - timedelta(days=1)).isoformat(),
        "modifiedLabel": "You modified · 1d ago",
        "owner": ME,
        "parentId": None,
    },
    {
        "id": "folder-marketing",
        "name": "Marketing Shared",
        "kind": "folder",
        "itemCount": 8,
        "modifiedAt": (NOW - timedelta(hours=6)).isoformat(),
        "modifiedLabel": "Shared by Sarah · 6h ago",
        "owner": SARAH,
        "shared": True,
        "parentId": None,
    },
]

FILES = [
    {
        "id": "file-budget",
        "name": "Budget_Q4_Final.xlsx",
        "kind": "spreadsheet",
        "sizeBytes": 245760,
        "sizeLabel": "240 KB",
        "modifiedAt": (NOW - timedelta(hours=2)).isoformat(),
        "modifiedLabel": "You modified · 2h ago",
        "owner": ME,
        "starred": True,
        "typeLabel": "Google Sheet",
        "storageUsedLabel": "240 KB",
        "location": "My Drive",
    },
    {
        "id": "file-pitch",
        "name": "Presentation_pitch.pptx",
        "kind": "presentation",
        "sizeBytes": 3145728,
        "sizeLabel": "3.0 MB",
        "modifiedAt": (NOW - timedelta(days=1)).isoformat(),
        "modifiedLabel": "Shared by Sarah · 1d ago",
        "owner": SARAH,
        "shared": True,
        "typeLabel": "Google Slides",
        "storageUsedLabel": "3.0 MB",
        "location": "My Drive",
    },
    {
        "id": "file-hero",
        "name": "Hero_Banner_V1.jpg",
        "kind": "image",
        "sizeBytes": 1843200,
        "sizeLabel": "1.8 MB",
        "modifiedAt": (NOW - timedelta(hours=5)).isoformat(),
        "modifiedLabel": "You modified · 5h ago",
        "owner": ME,
        "thumbnailUrl": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=300&fit=crop",
        "typeLabel": "JPEG Image",
        "storageUsedLabel": "1.8 MB",
        "location": "My Drive",
    },
    {
        "id": "file-design",
        "name": "Design_System_v2.pdf",
        "kind": "pdf",
        "sizeBytes": 524288,
        "sizeLabel": "512 KB",
        "modifiedAt": (NOW - timedelta(days=3)).isoformat(),
        "modifiedLabel": "You modified · 3d ago",
        "owner": ME,
        "starred": True,
        "typeLabel": "PDF Document",
        "storageUsedLabel": "512 KB",
        "location": "My Drive",
    },
    {
        "id": "file-q4-doc",
        "name": "Q4 Growth Strategy.docx",
        "kind": "document",
        "sizeBytes": 2516582,
        "sizeLabel": "2.4 MB",
        "modifiedAt": (NOW - timedelta(hours=1, minutes=15)).isoformat(),
        "modifiedLabel": "10:45 AM",
        "owner": ME,
        "typeLabel": "Google Docs",
        "storageUsedLabel": "2.4 MB",
        "location": "My Drive",
    },
    {
        "id": "file-sprint",
        "name": "Sprint_Backlog.xlsx",
        "kind": "spreadsheet",
        "sizeBytes": 862208,
        "sizeLabel": "842 KB",
        "modifiedAt": (NOW - timedelta(hours=3)).isoformat(),
        "modifiedLabel": "9:30 AM",
        "owner": ME,
        "typeLabel": "Google Sheet",
        "storageUsedLabel": "842 KB",
        "location": "My Drive",
    },
    {
        "id": "file-onboarding",
        "name": "Onboarding_Deck.pdf",
        "kind": "pdf",
        "sizeBytes": 4194304,
        "sizeLabel": "4.0 MB",
        "modifiedAt": (NOW - timedelta(hours=4)).isoformat(),
        "modifiedLabel": "8:15 AM",
        "owner": ALEX,
        "shared": True,
        "typeLabel": "PDF Document",
        "storageUsedLabel": "4.0 MB",
        "location": "Shared with me",
    },
    {
        "id": "file-team-photo",
        "name": "Team_Photo_Retreat.jpg",
        "kind": "image",
        "sizeBytes": 3145728,
        "sizeLabel": "3.0 MB",
        "modifiedAt": (NOW - timedelta(days=1, hours=2)).isoformat(),
        "modifiedLabel": "Yesterday, 4:30 PM",
        "owner": SARAH,
        "shared": True,
        "thumbnailUrl": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=400&h=300&fit=crop",
        "typeLabel": "JPEG Image",
        "storageUsedLabel": "3.0 MB",
        "location": "Shared with me",
    },
    {
        "id": "file-roadmap",
        "name": "Product_Roadmap.pptx",
        "kind": "presentation",
        "sizeBytes": 5767168,
        "sizeLabel": "5.5 MB",
        "modifiedAt": (NOW - timedelta(days=4)).isoformat(),
        "modifiedLabel": "Jul 15, 2026",
        "owner": ME,
        "typeLabel": "Google Slides",
        "storageUsedLabel": "5.5 MB",
        "location": "My Drive",
    },
    {
        "id": "file-budget-2024",
        "name": "Budget_2024.xlsx",
        "kind": "spreadsheet",
        "sizeBytes": 1048576,
        "sizeLabel": "1.0 MB",
        "modifiedAt": (NOW - timedelta(days=5)).isoformat(),
        "modifiedLabel": "Jul 14, 2026",
        "owner": ME,
        "typeLabel": "Google Sheet",
        "storageUsedLabel": "1.0 MB",
        "location": "My Drive",
    },
    {
        "id": "file-project-docs",
        "name": "Project_Docs",
        "kind": "folder",
        "sizeLabel": "--",
        "modifiedAt": (NOW - timedelta(days=6)).isoformat(),
        "modifiedLabel": "Jul 13, 2026",
        "owner": ME,
        "typeLabel": "Folder",
        "storageUsedLabel": "--",
        "location": "My Drive",
    },
    {
        "id": "file-old-draft",
        "name": "Old_Draft_v1.docx",
        "kind": "document",
        "sizeBytes": 131072,
        "sizeLabel": "128 KB",
        "modifiedAt": (NOW - timedelta(days=10)).isoformat(),
        "modifiedLabel": "Jul 9, 2026",
        "owner": ME,
        "trashed": True,
        "typeLabel": "Google Docs",
        "storageUsedLabel": "128 KB",
        "location": "Trash",
    },
]

ACTIVITY = {
    "file-budget": [
        {
            "id": "act-1",
            "actor": ME,
            "action": "edited an item",
            "timestamp": (NOW - timedelta(hours=2)).isoformat(),
            "timeLabel": "2 hours ago",
        },
        {
            "id": "act-2",
            "actor": SARAH,
            "action": "shared an item",
            "timestamp": (NOW - timedelta(days=1, hours=3)).isoformat(),
            "timeLabel": "Yesterday, 4:32 PM",
        },
    ],
}

USER_PROFILE = {
    "id": "user-me",
    "name": "Kapil Rohilla",
    "email": "kapil@example.com",
    "avatarUrl": "https://i.pravatar.cc/150?u=kapil",
    "storage": {
        "usedBytes": 115_964_116_992,
        "totalBytes": 161_061_273_600,
        "usedLabel": "10.8 GB",
        "totalLabel": "15 GB",
        "percentUsed": 72,
    },
}

_upload_tasks: dict[str, dict] = {}


def get_browse(folder_id: str | None = None) -> dict:
    breadcrumbs = [
        {"label": "CloudDrive", "id": None},
        {"label": "My Drive", "id": None},
    ]
    return {
        "breadcrumbs": breadcrumbs,
        "folders": FOLDERS,
        "files": FILES[:4],
    }


def get_recent() -> dict:
    today = [f for f in FILES if f["id"] in ("file-q4-doc", "file-sprint", "file-onboarding")]
    yesterday = [f for f in FILES if f["id"] in ("file-hero", "file-team-photo")]
    earlier = [f for f in FILES if f["id"] in ("file-roadmap", "file-budget-2024", "file-project-docs")]

    return {
        "groups": [
            {"label": "TODAY", "items": today},
            {"label": "YESTERDAY", "items": yesterday},
            {"label": "EARLIER THIS WEEK", "items": earlier},
        ]
    }


def get_starred() -> dict:
    return {"items": [f for f in FILES if f.get("starred")]}


def get_shared() -> dict:
    return {"items": [f for f in FILES if f.get("shared")]}


def get_trash() -> dict:
    return {"items": [f for f in FILES if f.get("trashed")]}


def get_file_details(file_id: str) -> dict | None:
    for item in FILES:
        if item["id"] == file_id:
            details = {**item}
            details["activity"] = ACTIVITY.get(file_id, [
                {
                    "id": "act-default",
                    "actor": ME,
                    "action": "modified an item",
                    "timestamp": item["modifiedAt"],
                    "timeLabel": item["modifiedLabel"],
                }
            ])
            return details
    return None


def search_files(query: str) -> dict:
    q = query.lower()
    results = [f for f in FILES if q in f["name"].lower()]
    return {"items": results}


def create_folder(name: str, parent_id: str | None) -> dict:
    folder = {
        "id": f"folder-{uuid4().hex[:8]}",
        "name": name,
        "kind": "folder",
        "itemCount": 0,
        "modifiedAt": NOW.isoformat(),
        "modifiedLabel": "Just now",
        "owner": ME,
        "parentId": parent_id,
    }
    FOLDERS.insert(0, folder)
    return folder


def start_upload(name: str) -> dict:
    task_id = f"upload-{uuid4().hex[:8]}"
    task = {
        "id": task_id,
        "fileName": name,
        "progress": 15,
        "status": "uploading",
    }
    _upload_tasks[task_id] = task
    return task

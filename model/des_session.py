from datetime import datetime, timezone


class DesSession:
    def __init__(
        self,
        name,
        owner,
        description="",
        session_id=None,
        created_at=None,
    ):
        self.session_id = session_id
        self.name = name
        self.owner = owner
        self.description = description
        self.created_at = created_at or datetime.now(timezone.utc)

    @classmethod
    def from_document(cls, document):
        return cls(
            session_id=document["_id"],
            name=document["name"],
            owner=document["owner"],
            description=document.get("description", ""),
            created_at=document.get("created_at"),
        )

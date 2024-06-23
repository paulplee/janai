class File:
    def __init__(self, id, object_type, bytes, created_at, filename, purpose):
        self.id = id
        self.object_type = object_type
        self.bytes = bytes
        self.created_at = created_at
        self.filename = filename
        self.purpose = purpose

    def to_dict(self):
        return {
            'id': self.id,
            'object_type': self.object_type,
            'bytes': self.bytes,
            'created_at': self.created_at,
            'filename': self.filename,
            'purpose': self.purpose
        }
        
    def __repr__(self):
        return (f"File(id='{self.id}', object='{self.object_type}', bytes={self.bytes}, "
                f"created_at={self.created_at}, filename='{self.filename}', purpose='{self.purpose}')")

class VectorStore:
    def __init__(self, id, created_at, file_counts, last_active_at, metadata, name, status, usage_bytes, expires_after=None, expires_at=None):
        self.id = id
        self.created_at = created_at
        self.file_counts = file_counts  # This should be an instance of FileCounts
        self.last_active_at = last_active_at
        self.metadata = metadata
        self.name = name
        self.status = status
        self.usage_bytes = usage_bytes
        self.expires_after = expires_after  # This should be an instance of ExpiresAfter
        self.expires_at = expires_at

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "file_counts": self.file_counts.to_dict() if self.file_counts else None,
            "last_active_at": self.last_active_at,
            "metadata": self.metadata,
            "name": self.name,
            "status": self.status,
            "usage_bytes": self.usage_bytes,
            "expires_after": self.expires_after.to_dict() if self.expires_after else None,
            "expires_at": self.expires_at
        }

    def __repr__(self):
        return f"VectorStore(id='{self.id}', created_at={self.created_at}, name='{self.name}', status='{self.status}')"
        
class FileCounts:
    def __init__(self, in_progress, completed, failed, cancelled, total):
        self.in_progress = in_progress
        self.completed = completed
        self.failed = failed
        self.cancelled = cancelled
        self.total = total

    def to_dict(self):
        return {
            "in_progress": self.in_progress,
            "completed": self.completed,
            "failed": self.failed,
            "cancelled": self.cancelled,
            "total": self.total
        }

class ExpiresAfter:
    def __init__(self, anchor, days):
        self.anchor = anchor
        self.days = days

    def to_dict(self):
        return {
            "anchor": self.anchor,
            "days": self.days
        }
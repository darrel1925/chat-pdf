from typing import Dict, Any
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, BooleanAttribute, MapAttribute, ListAttribute
)
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.exceptions import DoesNotExist
from utils.time_utils import current_time_ms
    
class ThreadPreview(MapAttribute):
    file_size = UnicodeAttribute()
    name = UnicodeAttribute()
    thread_id = UnicodeAttribute()
    updated_at_ms = NumberAttribute()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_size": self.file_size,
            "name": self.name,
            "thread_id": self.thread_id,
            "updated_at_ms": self.updated_at_ms,
        }
    
    @staticmethod
    def from_dict(thread_preview_dict: Dict[str, Any]) -> 'ThreadPreview':
        return ThreadPreview(
            name=thread_preview_dict["name"],
            file_size=thread_preview_dict["file_size"],
            thread_id=thread_preview_dict["thread_id"],
            updated_at_ms=thread_preview_dict["updated_at_ms"],
        )
    
    @staticmethod
    def create(self, thread_id: str) -> 'ThreadPreview':
        return ThreadPreview(
            name="",
            file_size="",
            thread_id=thread_id,
            updated_at_ms=current_time_ms(),
        )

class User(Model):
    """Encapsulates an Amazon DynamoDB table of movie data."""

    class Meta:
        table_name = 'User'

    email = UnicodeAttribute()
    created_at_ms = NumberAttribute()
    threads = ListAttribute(of=ThreadPreview, default=[])
    first_name = UnicodeAttribute(default="")
    id = UnicodeAttribute(hash_key=True)
    is_email_verified = BooleanAttribute(default=False)
    last_name = UnicodeAttribute(default="")
    profile_picture_url = UnicodeAttribute(null=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'email': self.email,
            'created_at_ms': self.created_at_ms,
            'threads': [thread.to_dict() for thread in self.threads],
            'first_name': self.first_name,
            'id': self.id,
            'is_email_verified': self.is_email_verified,
            'last_name': self.last_name,
            'profile_picture_url': self.profile_picture_url,
        }

    @staticmethod
    def from_dict(user_dict: Dict[str, Any]) -> 'User':
        return User(
            email=user_dict['email'],
            created_at_ms=user_dict.get('created_at_ms', 0),
            threads=[ThreadPreview.from_dict(thread) for thread in user_dict.get('threads', [])],
            first_name=user_dict.get('first_name', ""),
            id=user_dict['id'] ,
            is_email_verified=user_dict.get('is_email_verified', False),
            last_name=user_dict.get('last_name', ""),
            profile_picture_url=user_dict.get('profile_picture_url', ""),  # keep as None
        )

    def __eq__(self, other) -> bool:
        return self.to_dict() == other.to_dict()

    def add_thread_preview(self, thread_preview: ThreadPreview) -> ThreadPreview:
        if thread_preview.thread_id in [thread.thread_id for thread in self.threads]:
            print("Cannot add thread_preview that is already present")
            return thread_preview
        
        self.update(
            actions=[
                User.threads.set((
                    User.threads | []
                ).append([thread_preview]))
            ]
        )

        return thread_preview

    def remove_thread_preview(self, thread_id: str) -> None:
        if thread_id not in [thread.thread_id for thread in self.threads]:
            print("Cannot remove thread_preview that is not present")
            return

        self.update(
            actions=[
                User.threads.set(
                    User.threads.remove([thread_id])
                )
            ]
        )
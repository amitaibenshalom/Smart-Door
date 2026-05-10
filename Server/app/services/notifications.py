import logging

from flask import current_app

from app.models import PushDevice

logger = logging.getLogger(__name__)


class NotificationService:
    def send_door_status_changed(self, door, previous_status):
        if not current_app.config["NOTIFICATIONS_ENABLED"]:
            return

        devices = PushDevice.query.filter_by(user_id=door.user_id).all()
        title = f"{door.name} {door.last_status}"
        body = f"{door.name} is now {door.last_status}."

        for device in devices:
            self.send_push(device, title, body, {"door_id": str(door.id)})

    def send_push(self, push_device, title, body, data=None):
        logger.info(
            "Mock push notification platform=%s user_id=%s token=%s title=%s body=%s data=%s",
            push_device.platform,
            push_device.user_id,
            push_device.push_token,
            title,
            body,
            data or {},
        )


notification_service = NotificationService()

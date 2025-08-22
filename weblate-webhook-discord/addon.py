from typing import TYPE_CHECKING

from django.urls import reverse
from weblate.utils.site import get_site_url
from weblate.addons.webhooks import JSONWebhookBaseAddon
from weblate.addons.forms import BaseWebhooksAddonForm
from weblate.auth.models import User
from weblate.trans.models import Change

if TYPE_CHECKING:
    from weblate.addons.models import AddonActivityLog
    from weblate.trans.models import Change

def user_avatar_url(user: User) -> str:
    return get_site_url(reverse("user_avatar", kwargs={"user": user.username, "size": 32}))

def discord_escape(s: str) -> str:
    return s.replace("\\", "\\\\")

class DiscordWebhookAddon(JSONWebhookBaseAddon):
    name = "weblate.webhook.discord"
    verbose = "Discord Webhooks"
    description = "Sends notification to a Discord channel based on selected events."
    icon = "webhook.svg"
    settings_form = BaseWebhooksAddonForm

    def build_webhook_payload(self, change: Change) -> dict[str, int | str | list]:
        embed = {
            "title": change.get_action_display(),
            "fields": [],
        }

        if change.author:
            embed["author"] = {
                "name": change.author.get_visible_name(),
                "icon_url": user_avatar_url(change.author)
            }

        if url := change.get_absolute_url():
            embed["url"] = get_site_url(url)
        
        if change.project:
            embed["description"] = change.project.name

        if change.timestamp:
            embed["timestamp"] = change.timestamp.isoformat()

        if change.component:
            if change.project:
                embed["description"] += " / "
            embed["description"] += change.component.name

        if change.language:
            embed["description"] += "\n" + change.language.name

        if change.unit:
            embed["fields"].append({
                "name": "Source",
                "value": discord_escape(change.unit.source),
            })

        if change.old:
            embed["fields"].append({
                "name": "Old",
                "value": discord_escape(change.old),
                "inline": True,
            })
        
        if change.target:
            embed["fields"].append({
                "name": "New",
                "value": discord_escape(change.target),
                "inline": True,
            })

        payload: dict[str, list] = {
            "embeds": [
                embed
            ]
        }

        return payload

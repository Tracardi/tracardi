from tracardi.domain.subscription import Subscription
from tracardi.context import get_context
from tracardi.service.storage.mysql.schema.table import SubscriptionTable


def map_to_subscription_table(subscription: Subscription) -> SubscriptionTable:
    context = get_context()
    return SubscriptionTable(
        id=subscription.id,
        tenant=context.tenant,
        production=context.production,
        name=subscription.name,
        description=subscription.description,
        enabled=subscription.enabled,
        tags=",".join(subscription.tags) if subscription.tags else "",
        topic=subscription.topic
    )


def map_to_subscription(subscription_table: SubscriptionTable) -> Subscription:
    return Subscription(
        id=subscription_table.id,
        name=subscription_table.name,
        description=subscription_table.description,
        enabled=subscription_table.enabled,
        tags=subscription_table.tags.split(",") if subscription_table.tags else [],
        topic=subscription_table.topic,

        production=subscription_table.production,
        running=subscription_table.running
    )

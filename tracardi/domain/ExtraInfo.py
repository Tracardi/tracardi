def build(origin, object=None, event_id=None, profile_id=None, flow_id=None, node_id=None, user_id=None, error_number=None, traceback=None) -> dict:
    return dict(
        origin=origin,
        class_name=object.__class__.__name__ if object else None,
        package=object.__class__.__module__ if object else None,
        event_id=event_id,
        profile_id=profile_id,
        flow_id=flow_id,
        node_id=node_id,
        user_id=user_id,
        error_number=error_number
    )

def exact(origin, event_id=None, profile_id=None, flow_id=None, node_id=None, class_name=None, package=None, user_id=None, error_number=None, traceback=None) -> dict:
    return dict(
        origin=origin,
        class_name=class_name,
        package=package,
        event_id=event_id,
        profile_id=profile_id,
        flow_id=flow_id,
        node_id=node_id,
        user_id=user_id,
        error_number=error_number
    )

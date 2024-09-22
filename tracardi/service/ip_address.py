from tracardi.config import server


def get_ip_address(request) -> str:

    """
    Returns IP address - if address is forwarded from reverse proxy it takes USE_X_FORWARDED_IP env to figure out
    where the forwarded ip is stored in headers.
    """

    if server.x_forwarded_ip_header is not None and server.x_forwarded_ip_header in request.headers:
        return request.headers[server.x_forwarded_ip_header]
    return request.client.host

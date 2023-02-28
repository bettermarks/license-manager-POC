from urllib.parse import urljoin, quote


def hierarchy_provider_memberships_url(base_url, user_eid):
    """contructs the 'membership url from a HP base url and a user EID"""
    return urljoin(base_url, f"users/{quote(user_eid)}/membership")

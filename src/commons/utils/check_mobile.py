import re


def check_mobile(request):
    MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)
    return MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']) is not None

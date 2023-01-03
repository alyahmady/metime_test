from rest_framework.throttling import ScopedRateThrottle


class RegisterThrottle(ScopedRateThrottle):
    scope = "user_register"

from rest_framework.throttling import ScopedRateThrottle


class UserRegisterThrottle(ScopedRateThrottle):
    scope = "user_register"


class UserUpdateThrottle(ScopedRateThrottle):
    scope = "user_update"

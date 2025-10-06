from rest_framework.throttling import UserRateThrottle

class TenPerHourUserThrottle(UserRateThrottle):
    scope = 'ten_per_hour'

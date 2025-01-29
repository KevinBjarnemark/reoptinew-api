GLOBAL_VALIDATION_RULES = {
    "IMAGE": {
        "VALID_EXTENSIONS": ["jpg", "jpeg", "png", "webp"],
    },
    # Users with an acocunt must be 16 years or older to view posts
    # that may be inappropriate for children.
    "AGE_RESTRICTED_CONTENT_AGE": 16,
    # Users must be 13 years or older to create an account
    "ACCOUNT_MIN_AGE": 13,
}

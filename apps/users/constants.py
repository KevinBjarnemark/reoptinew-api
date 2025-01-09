

VALIDATION_RULES = {
    "USERNAME": {
        "MIN_LENGTH": 2,
        "MAX_Length": 150,
    },
    "PASSWORD": {
        "MIN_LENGTH": 8,
        "MAX_LENGTH": 128,
    },
    "IMAGE": {
        "VALID_EXTENSIONS": ["jpg", "jpeg", "png", "webp"],
    }
}

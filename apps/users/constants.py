

VALIDATION_RULES = {
    "USERNAME": {
        "MIN_LENGTH": 2,

    },
    "PASSWORD": {
        "MIN_LENGTH": 8,
    },
    "IMAGE": {
        "VALID_EXTENSIONS": ["jpg", "jpeg", "png", "webp"],
    }
}

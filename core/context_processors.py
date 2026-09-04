def site_context(request):
    return {
        "SITE_NAME": "Cooperative Gig Services",
        "AVAILABLE_LANGUAGES": [
            ("en", "English"),
            ("hi", "हिन्दी"),
            ("gu", "ગુજરાતી"),
        ],
    }

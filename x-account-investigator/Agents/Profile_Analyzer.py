def profile_agent(state):

    x_data = state.get("x_data", {})

    profile = x_data.get(
        "profile",
        {}
    )

    profile_status = x_data.get(
        "profile_status",
        "unknown"
    )

    if profile_status == "not_found":

        return {
            "profile_analysis": {
                "status": "not_found",
                "summary": (
                    "The X lookup did not return a "
                    "profile for this exact handle."
                )
            }
        }

    if not profile:

        return {
            "profile_analysis": {
                "status": "unavailable",
                "summary": "No X profile data was collected."
            }
        }

    def value(field):

        result = profile.get(field)

        if result is None or result == "":
            return "Not available"

        return result

    analysis = {
        "status": "success",

        "username": value("username"),

        "display_name": value(
            "display_name"
        ),

        "bio": value("bio"),

        "location": value("location"),

        "followers": value(
            "followers"
        ),

        "following": value(
            "following"
        ),

        "tweets_count": value(
            "tweets_count"
        ),

        "verified": value(
            "verified"
        ),

        "created": value(
            "created"
        ),

        "profile_url": value(
            "profile_url"
        )
    }

    return {
        "profile_analysis": analysis
    }
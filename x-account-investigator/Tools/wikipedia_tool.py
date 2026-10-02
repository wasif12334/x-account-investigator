import wikipediaapi


wiki = wikipediaapi.Wikipedia(
    user_agent="XAccountInvestigator/1.0",
    language="en"
)


def wikipedia_lookup(query: str):

    query = query.replace(
        "@",
        ""
    ).strip()

    try:

        page = wiki.page(query)

    except Exception as e:

        return {

            "status": "error",

            "found": False,

            "title": None,

            "summary": None,

            "url": None,

            "error": str(e),
        }

    if not page.exists():

        return {

            "status": "not_found",

            "found": False,

            "title": None,

            "summary": None,

            "url": None,

            "error": None,
        }

    return {

        "status": "success",

        "found": True,

        "title": page.title,

        "summary": page.summary,

        "url": page.fullurl,

        "error": None,
    }
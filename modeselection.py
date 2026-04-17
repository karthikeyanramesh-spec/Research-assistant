def build_query(query, mode):
    if mode == "student":
        return query + " simple explanation tutorial"
    elif mode == "research":
        return query + " latest research detailed"
    elif mode == "developer":
        return query + " implementation code github"
    return query


def isgoodcontent(content):
    return content and len(content) > 500
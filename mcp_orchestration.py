from mcp_integration import tools

def mcp_orchestration(query, mode):

    urls = tools["serper"].func({
        "query": query,
        "mode": mode
    })

    data = tools["scrape"].func({
        "urls": urls
    })

    draft = tools["generate"].func({
        "query": query,
        "mode": mode,
        "data": data
    })

    return draft

    
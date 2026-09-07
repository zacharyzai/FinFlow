PAGE_SIZE = 1000


def fetch_all(query_factory) -> list[dict]:
    """
    Run a paginated Supabase query to completion and return every row.

    PostgREST silently caps any single response at 1000 rows (configurable
    server-side, but off by default) — a bare .select().execute() on a table
    with more rows than that just returns the first 1000, no error, no warning.
    query_factory must be a callable that returns a FRESH, unexecuted query
    builder each call (all .eq()/.gte()/etc. filters already applied) so a new
    .range() can be chained on for each page.
    """
    rows = []
    offset = 0
    while True:
        page = query_factory().range(offset, offset + PAGE_SIZE - 1).execute().data
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return rows

def query_prefix(request, exclude='page'):
    params = request.GET.copy()
    params.pop(exclude, None)
    qs = params.urlencode()
    return (qs + '&') if qs else ''

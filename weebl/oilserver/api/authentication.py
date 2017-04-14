from tastypie.authentication import ApiKeyAuthentication


class WorldReadableApiKeyAuthentication(ApiKeyAuthentication):
    def is_authenticated(self, request, **kwargs):
        if request.method == 'GET':
            return True
        
        return super(GlobalReadApiKeyAuthentication, self).is_authenticated(
            request, **kwargs)

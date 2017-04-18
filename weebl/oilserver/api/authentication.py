from tastypie.authentication import ApiKeyAuthentication


class WorldReadableApiKeyAuthentication(ApiKeyAuthentication):
    def is_authenticated(self, request, **kwargs):
        if request.method == 'GET':
            return True
        
        return super(WorldReadableApiKeyAuthentication, self).is_authenticated(
            request, **kwargs)

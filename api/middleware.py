from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

class BearerTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'

class TokenExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.EXEMPT_URLS = ['/signin/', '/signup/']
        self.TOKEN_LIFETIME_MINUTES = 5
        self.TOKEN_LIFETIME = self.TOKEN_LIFETIME_MINUTES * 60  # Convert to seconds

    def __call__(self, request):
        if not any(request.path.startswith(url) for url in self.EXEMPT_URLS):
            auth_header = request.headers.get('Authorization')
            
            if auth_header and auth_header.startswith('Bearer '):
                token_key = auth_header.split(' ')[1]
                try:
                    token = Token.objects.get(key=token_key)
                    now = timezone.now()
                    token_age = (now - token.created).total_seconds()

                    if token_age > self.TOKEN_LIFETIME:  # > 5 minutes (300 sec)
                        token.delete()
                        return JsonResponse(
                            {'error': 'Token has expired'}, 
                            status=status.HTTP_401_UNAUTHORIZED
                        )
                    
                    # Renew token
                    token.created = now
                    token.save()
                except Token.DoesNotExist:
                    return JsonResponse(
                        {'error': 'Invalid token'}, 
                        status=status.HTTP_401_UNAUTHORIZED
                    )

        response = self.get_response(request)
        return response
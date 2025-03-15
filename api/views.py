from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
import requests
import re

User = get_user_model()

def is_valid_phone(phone):
    phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
    return bool(phone_pattern.match(phone))

def get_id_type(id_value):
    try:
        validate_email(id_value)
        return 'email'
    except ValidationError:
        if is_valid_phone(id_value):
            return 'phone'
    return None

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    id_value = request.data.get('id')
    password = request.data.get('password')
    
    if not id_value or not password:
        return Response({'error': 'Both ID and password are required'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    id_type = get_id_type(id_value)
    if not id_type:
        return Response({'error': 'Invalid ID format'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=id_value).exists():
        return Response({'error': 'User already exists'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=id_value, password=password)
    user.profile.id_type = id_type
    user.profile.save()
    token = Token.objects.create(user=user)
    return Response({
        'token': token.key,
        'expires_in': 300  # 5 minutes in seconds
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def signin(request):
    id_value = request.data.get('id')
    password = request.data.get('password')
    
    if not id_value or not password:
        return Response({'error': 'Both ID and password are required'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=id_value)
        if user.check_password(password):
            # Delete any existing tokens
            Token.objects.filter(user=user).delete()
            # Create new token
            token = Token.objects.create(user=user)
            return Response({
                'token': token.key,
                'expires_in': 300  # 5 minutes in seconds
            })
        else:
            return Response({'error': 'Invalid credentials'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, 
                       status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def info(request):
    user = request.user
    return Response({
        'id': user.username,
        'id_type': user.profile.id_type
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def latency(request):
    try:
        start_time = timezone.now()
        requests.get('https://ya.ru')
        end_time = timezone.now()
        latency = (end_time - start_time).total_seconds() * 1000
        return Response({'latency_ms': round(latency, 2)})
    except requests.RequestException:
        return Response({'error': 'Failed to measure latency'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    all_sessions = request.data.get('all', False)
    
    if all_sessions:
        Token.objects.filter(user=request.user).delete()
    else:
        request.auth.delete()
    
    return Response(status=status.HTTP_200_OK)

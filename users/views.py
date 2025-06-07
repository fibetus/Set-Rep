from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        # Validate required fields
        if not all([username, email, password]):
            return Response(
                {'detail': 'Please provide all required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            return Response(
                {'detail': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=email).exists():
            return Response(
                {'detail': 'Email already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate password
        try:
            validate_password(password)
        except ValidationError as e:
            return Response(
                {'detail': e.messages},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create user with transaction to ensure atomicity
        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=True  # Ensure user is active
            )
            user.save()

        return Response(
            {
                'detail': 'User registered successfully',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'id': user.id
                }
            },
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response(
            {'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

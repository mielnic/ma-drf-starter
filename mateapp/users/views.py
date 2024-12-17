from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.core.mail import EmailMessage
from .serializers import UserRegistrationSerializer, PasswordResetRequestSerializer, ChangePasswordSerializer
from .tokens import account_activation_token
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.contrib.auth import get_user_model
from .functions import checkUserCreationLimit
import logging

logger = logging.getLogger('mateapp')

# Http only jwt

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = TokenObtainPairSerializer

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data
        access_token = data.get("access")
        refresh_token = data.get("refresh")
        
        # Set the access token in a HTTP-only cookie
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            max_age=3600,  # Set according ACCESS_TOKEN_LIFETIME jwt parameter in settings.py.
            samesite='Lax',
            secure=True,  # Use True in production for HTTPS
        )

        # Set the refresh token in a HTTP-only cookie
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            max_age=7 * 24 * 3600,  # Set according REFRESH_TOKEN_LIFETIME jwt parameter in settings.py.
            samesite='Lax',
            secure=True,  # Use True in production for HTTPS
        )
        
        # Optionally, clear any token data from the response body
        response.data = {}
        
        return response

# Register user

class UserRegistrationAPIView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()

            # Prepare de data for the confirmation email.
            current_site = get_current_site(request)
            mail_subject = _('Activate your user account.')
            message = render_to_string('mail/activate_account.html', {
                'user': user.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http'
            })
            email = EmailMessage(mail_subject, message, to=[user.email])

            # Sends the confirmation email
            try:
                email.send()
                logger.info(f'USER REGISTRATION: registration initiated for {user.email}')
                return Response({'message': _('Please go to your email inbox and click on the included activation link to enable your account. <b>Note:</b> Remember to check your spam folder.')}, status=status.HTTP_201_CREATED)
            except Exception as e:
                user.delete()
                logger.error(f'USER REGISTRATION: failed to initiate user registration for {user.email}: {e}')
                return Response({'error': _('There was a problem sending the email. Please contact the Administrator')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Activate User

class ActivateAPIView(APIView):
    def get(self, request, uidb64, token):
        User = get_user_model()

        # We try to get the user from the from the uidb64
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # If succesful, we validate the token
        if user is not None and account_activation_token.check_token(user, token):
            # If REGISTRATION_PARKING is True, user remains validated but inactive until other action is performed in the app logic.
            if settings.REGISTRATION_PARKING == False:
                activeEnabled = checkUserCreationLimit()  # Function that enforce user creation limit.
                if activeEnabled:
                    user.is_active = True
                    user.save()
                    logger.info(f'USER REGISTRATION: registration email verified for {user.email} and user activated.')
                    return Response({'message': _('Your account has been activated.')}, status=status.HTTP_200_OK)
                else:
                    user.is_active = False
                    user.save()
                    logger.info(f'USER REGISTRATION: registration email verified for {user.email}. Activation pending for approval.')
                    return Response({'message': _('Thank you for your confirmation. The Administrator will enable your account soon.')}, status=status.HTTP_202_ACCEPTED)
            else:
                user.is_active = False
                user.save()
                logger.info(f'USER REGISTRATION: registration email verified for {user.email}. Activation pending for approval.')
                return Response({'message': _('Thank you for your confirmation. The Administrator will enable your account soon.')}, status=status.HTTP_202_ACCEPTED)
        else:
            logger.error(f'USER REGISTRATION: registration email failed for {user.email}. Link expired.')
            return Response({'error': _("Activation link is invalid. Contact the administrator.")}, status=status.HTTP_400_BAD_REQUEST)

# Password reset request:

class PasswordResetRequestAPIView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)

        # We vaildate the email in the users database.
        if serializer.is_valid():
            user_email = serializer.validated_data['email']
            User = get_user_model()
            associated_user = User.objects.filter(email=user_email).first()

            if associated_user:
                # We prepare the data for the password reset email.
                mail_subject = _('Password Reset Request')
                message = render_to_string('mail/password_reset.html', {
                    'user': associated_user.first_name,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    'protocol': 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(mail_subject, message, to=[user_email])

                # We try to send the password reset email.
                try:
                    email.send()
                    logger.info(f'USER PASSWORD: password reset link issued to {associated_user.email}.')
                    return Response(
                        {'message': _("Please check your email inbox for the password reset link. Check your spam folder if necessary.")},
                        status=status.HTTP_200_OK
                    )
                except Exception as e:
                    logger.error(f'USER PASSWORD: password reset link was requested {associated_user.email}, but could not be sent: {e}.')
                    return Response(
                        {'error': _('There was a problem sending the email. Please contact the Administrator.')},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                logger.error(f'USER PASSWORD: password reset link was requested {associated_user.email}, but could not be sent.')
                return Response(
                    {'error': _('The email address provided is not registered.')},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Password reset set new password

class PasswordResetConfirmAPIView(APIView):
    def post(self, request, uidb64, token):
        User = get_user_model()

        # We try to get the user from the from the uidb64
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        # If successful, we record the new password.
        if user is not None and account_activation_token.check_token(user, token):
            serializer = ChangePasswordSerializer(data=request.data)

            if serializer.is_valid():
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                logger.info(f'USER PASSWORD: password reseted for {user.email}.')
                return Response({'message': _("Your password has been successfully reset. You may now log in.")}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        logger.error(f'USER PASSWORD: could not reset password for {user.email}. Link is invalid.')
        return Response({'error': _("The link is invalid or expired.")}, status=status.HTTP_400_BAD_REQUEST)
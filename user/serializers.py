from .models import *
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode as uid_decoder
from django.utils.encoding import force_str
from django.contrib.auth.password_validation import validate_password
from django.template.loader import render_to_string

UserModel: UserAccount = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = UserModel
        fields = [
            'email', 'password', 'first_name', 'last_name',
        ]
        extra_kwargs = {
            'email': {'required': True, 'allow_blank': False},
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
        }

    def validate_email(self, email):
        if UserModel.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user is already exists with this email.")
        return email

    def create(self, validated_data):
        user = UserModel.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        # send the user welcome email
        html_template = 'emails/user/email_confirmation_signup_message.html'

        email_context = {
            'user_display_name': user.get_full_name(),
            'WEBSITE_BASE_URL': settings.WEBSITE_BASE_URL
        }
        html_message = render_to_string(html_template, context=email_context)
        subject = render_to_string('emails/user/email_confirmation_subject.txt')
        user.email_user(subject, html_message, html_message=html_message)
        return user


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        exclude = ["user_permissions", "groups", "password"]

    def validate_email(self, email):
        user = self.context['request'].user
        
        # check if this email is already exist
        user = UserAccount.objects.filter(email=email).exclude(email=user.email).first()

        if user:
            raise ValidationError("This email is already using by another user")
        return email


class PasswordResetSerializer(serializers.Serializer):
    """
    Custom Serializer for requesting a password reset e-mail.
    """
    email = serializers.EmailField()
    password_reset_form_class = PasswordResetForm

    def get_email_options(self):
        """Override this method to change default e-mail options"""

        extra_email_context = {
            "WEBSITE_BASE_URL": settings.WEBSITE_BASE_URL,
            "user_name": self.user.get_full_name()
        }
        return {
            'subject_template_name': 'emails/user/reset-password-subject.txt',
            'html_email_template_name': 'emails/user/reset-password-email.html',
            'email_template_name': 'emails/user/reset-password-email.html',
            'extra_email_context': extra_email_context
        }

    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)
        
        if not UserModel.objects.filter(email=value).exists():
            raise serializers.ValidationError('No account found for that email address')
        
        # set user to the class so that we can access it from other methods
        self.user = UserModel.objects.get(email=value)
        return value

    def save(self):
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)
    uid = serializers.CharField()
    token = serializers.CharField()

    set_password_form_class = SetPasswordForm

    def validate(self, attrs):
        self._errors = {}

        # Decode the uidb64 to uid to get User object
        try:
            uid = force_str(uid_decoder(attrs['uid']))
            self.user = UserModel.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            raise ValidationError({'uid': ['Invalid value']})

        # Construct SetPasswordForm instance
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        if not default_token_generator.check_token(self.user, attrs['token']):
            raise ValidationError({'token': ['Invalid value']})

        return attrs

    def save(self):
        return self.set_password_form.save()


class PasswordChangeSerializer(serializers.Serializer):
    
    old_password = serializers.CharField(
        max_length=128,
        error_messages={
            'required': "Current password is required",
            'blank': "Please enter your current password"
        }
    )
    new_password1 = serializers.CharField(
        max_length=128,
        error_messages={
            'required': "New password is required",
            'blank': "Please enter a new password"
        }
    )
    new_password2 = serializers.CharField(
        max_length=128,
        error_messages={
            'required': "Confirm password is required",
            'blank': "Please enter confirm password"
        }
    )

    set_password_form_class = SetPasswordForm

    def __init__(self, *args, **kwargs):
        super(PasswordChangeSerializer, self).__init__(*args, **kwargs)
        self.request = self.context.get('request')
        self.user = getattr(self.request, 'user', None)
        
    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.user,
            not self.user.check_password(value)
        )

        if all(invalid_password_conditions):
            raise serializers.ValidationError("Current password didn't match")
        return value

    def validate(self, attrs):
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()


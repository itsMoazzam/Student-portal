from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.text import slugify
from itertools import count

from .models import (
    Student, ActivityLog, Marks, Message, Task,
    Category, TaskSubmission,SubAdmin, Certificate
)

import random
import time
from django.db import IntegrityError

User = get_user_model()


def _generate_unique_username(first_name: str) -> str:
    base = slugify(first_name) or "user"
    for i in count(start=0):
        candidate = base if i == 0 else f"{base}{i}"
        if not User.objects.filter(username=candidate).exists():
            return candidate

def create_user_with_unique_username(first_name, last_name, email, password, is_student=False, is_subadmin=False):
    for attempt in range(10):
        try:
            username = _generate_unique_username(first_name)
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_student=is_student,
                is_subadmin=is_subadmin,
            )
            user.set_password(password)
            user.save()
            return user
        except IntegrityError:
            time.sleep(random.uniform(0.01, 0.1))  # slight backoff
            continue
    raise Exception("Could not create unique username after 10 attempts.")

        
# ------------------  User & Auth  ------------------ #
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["is_admin"]    = user.is_admin
        token["is_subadmin"] = user.is_subadmin
        token["is_student"]  = user.is_student
        token["username"]    = user.username
        return token


# ------------------  Category  ------------------ #
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ["id", "name"]


# ------------------  Student  ------------------ #
class StudentSerializer(serializers.ModelSerializer):
    user     = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)        # read-only nested

    class Meta:
        model  = Student
        fields = [
            "id", "user", "category", "admission_number",
            "github_url", "linkedin_url",
            "is_public", "is_approved", "approval_requested",
            "degree_completed", "created_at"
        ]
        read_only_fields = ["id", "user", "admission_number",
                            "is_approved", "degree_completed", "created_at"]


#  -------------  student creation -------------
class CreateStudentSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    email     = serializers.EmailField()
    password  = serializers.CharField(write_only=True, style={"input_type": "password"})
    category  = serializers.SlugRelatedField(
        slug_field="name", queryset=Category.objects.all()
    )
    username  = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already in use.")
        return value


    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_username(self, value):
        if value and User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def create(self, validated_data):
        names      = validated_data.pop("full_name").split()
        first_name = names[0]
        last_name  = " ".join(names[1:]) if len(names) > 1 else ""

        explicit_username = validated_data.pop("username", "").strip()

        # --- create the user safely ---
        if explicit_username:
            # honour admin-supplied username but still guard against a rare race
            for _ in range(3):
                try:
                    user = User.objects.create(
                        username   = explicit_username,
                        email      = validated_data["email"],
                        first_name = first_name,
                        last_name  = last_name,
                        is_student = True,
                    )
                    break
                except IntegrityError:
                    raise serializers.ValidationError("Username already taken.")
        else:
            user = create_user_with_unique_username(
                first_name=first_name,
                last_name=last_name,
                email=validated_data["email"],
                password=validated_data["password"],
                is_student=True,
            )

        # set / reset password (create_user_with_unique_username already does this)
        if not explicit_username:
            pass  # password already set inside helper
        else:
            user.set_password(validated_data["password"])
            user.save()

        # create Student profile
        Student.objects.create(user=user, category=validated_data["category"])
        return user


# -------------  leader / sub-admin creation -------------
class CreateLeaderSerializer(serializers.Serializer):
    full_name  = serializers.CharField()
    email      = serializers.EmailField()
    password   = serializers.CharField(write_only=True, style={"input_type": "password"})
    categories = serializers.SlugRelatedField(
        slug_field="name", many=True, queryset=Category.objects.all()
    )
    username   = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already in use.")
        return value


    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_username(self, value):
        if value and User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def create(self, validated_data):
        names      = validated_data.pop("full_name").split()
        first_name = names[0]
        last_name  = " ".join(names[1:]) if len(names) > 1 else ""

        explicit_username = validated_data.pop("username", "").strip()

        if explicit_username:
            for _ in range(3):
                try:
                    user = User.objects.create(
                        username    = explicit_username,
                        email       = validated_data["email"],
                        first_name  = first_name,
                        last_name   = last_name,
                        is_subadmin = True,
                    )
                    break
                except IntegrityError:
                    raise serializers.ValidationError("Username already taken.")
        else:
            user = create_user_with_unique_username(
                first_name=first_name,
                last_name=last_name,
                email=validated_data["email"],
                password=validated_data["password"],
                is_subadmin=True,
            )

        if not explicit_username:
            pass
        else:
            user.set_password(validated_data["password"])
            user.save()

        # link categories
        sub = SubAdmin.objects.create(user=user)
        sub.categories.set(validated_data["categories"])
        return user


# ------------------  Marks & Progress  ------------------ #
class MarksSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Marks
        fields = ["id", "subject", "score", "max_score", "exam_date"]


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ActivityLog
        fields = "__all__"
        read_only_fields = ["timestamp"]

# ------------------  Tasks ------------------ #
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Task
        fields = "__all__"


class TaskSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = TaskSubmission
        fields = "__all__"
        read_only_fields = ["submitted_at", "reviewed_at", "reviewer"]


# ------------------  Messaging  ------------------ #
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Message
        fields = "__all__"
        read_only_fields = ["timestamp"]



class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category = serializers.SlugRelatedField(
        slug_field="name", queryset=Category.objects.all()
    )

    class Meta:
        model  = Student
        fields = [
            "id", "user", "github_url", "linkedin_url",
            "is_public", "is_approved",
            "approval_requested", "degree_completed", "category"
        ]
        read_only_fields = ["id", "user", "is_approved", "degree_completed"]

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'student', 'file', 'signed_by', 'uploaded_at']
        read_only_fields = ['signed_by', 'uploaded_at']
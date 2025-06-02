from rest_framework import serializers
from .models import Student, User, ActivityLog, Marks, Message
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import permissions, generics
from .models import Task ,Category
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"        

class MarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marks
        fields = ['id', 'subject', 'score', 'created_at']

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    marks = MarksSerializer(many=True, read_only=True, source='marks_set')

    class Meta:
        model = Student
        fields = ['id', 'user', 'degree_completed', 'created_at', 'marks']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class CreateStudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True)
    category = serializers.CharField()
    role = serializers.ChoiceField(choices=["student", "subadmin", "admin"])

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'full_name', 'category', 'role']

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        category = validated_data.pop('category')
        role = validated_data.pop('role')
        username = validated_data.get('username')

        if not username:
            username = full_name.split()[0].lower()  # default username from full name
            validated_data['username'] = username

        user = User.objects.create(
            username=username,
            email=validated_data['email'],
            first_name=full_name.split()[0],
            last_name=" ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else "",
        )
        user.set_password(validated_data['password'])
        user.save()

        # Create student or sub-admin etc.
        Student.objects.create(user=user, category=category, role=role)

        return user

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = '__all__'
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['is_superuser'] = user.is_superuser
        token['is_staff'] = user.is_staff
        token['username'] = user.username
        return token
 
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class MessageView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Message.objects.all()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id',
            'user',
            'github_url',
            'linkedin_url',
            'is_public',
            'is_approved',
            'approval_requested',
            'degree_completed',
            'category'
        ]
        read_only_fields = ['id', 'user', 'is_approved', 'degree_completed']
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Student, ActivityLog, Marks, TaskSubmission, Category
from .serializers import *
# from .serializers import TaskSerializer
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView
from .permissions import IsStudent
import csv
from io import TextIOWrapper
from reportlab.pdfgen import canvas
from django.http import HttpResponse
# Admin-only: Create a new student and send email

@api_view(['POST'])
@permission_classes([])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'detail': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is None:
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    token, created = Token.objects.get_or_create(user=user)

    # Determine role
    is_admin = user.is_staff or user.is_superuser
    is_student = Student.objects.filter(user=user).exists()
    
    return Response({
        'token': token.key,
        'is_admin': is_admin,
        'is_student': is_student,
        'username': user.username,
    })


class CreateStudentView(generics.CreateAPIView):
    serializer_class = CreateStudentSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        raw_password = self.request.data.get('password')
        full_name = self.request.data.get('full_name', '')
        username = self.request.data.get('username', '').strip()

        if not username:
            # fallback: use first word of full_name as username
            username = full_name.split()[0].lower()

        # Add username before saving
        serializer.validated_data['username'] = username
        serializer.validated_data['full_name'] = full_name

        user = serializer.save()
        user.set_password(raw_password)
        user.save()

        try:
            send_mail(
                subject='Your Student Portal Login',
                message=(
                    f"Hello {full_name},\n\n"
                    f"Your student account has been created.\n"
                    f"Username: {username}\n"
                    f"Password: {raw_password}\n\n"
                    "Please log in to your dashboard to check your progress.\n\n"
                    "Best regards,\nStudent Portal Team"
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({'error': f'User created but failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Student created and email sent.'}, status=status.HTTP_201_CREATED)

        
# Admin-only: List all students
class StudentListView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAdminUser]

# Admin-only: Mark a student as having completed their degree
class MarkDegreeCompletedView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, *args, **kwargs):
        student = self.get_object()
        student.degree_completed = True
        student.save()
        ActivityLog.objects.create(student=student, action="Degree marked as completed")

        send_mail(
            'Degree Completed!',
            'Congratulations! Your degree is marked as completed. Check your portal to download the certificate.',
            settings.EMAIL_HOST_USER,
            [student.user.email],
            fail_silently=False,
        )
        return Response({"message": "Marked as completed"}, status=200)

# Admin-only: Upload a certificate for the student
class UploadCertificateView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        student = self.get_object()
        certificate = request.FILES.get('certificate')
        if certificate:
            student.certificate = certificate
            student.save()
            return Response({"message": "Certificate uploaded."})
        return Response({"error": "No file provided"}, status=400)

@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def bulk_add_students(request):
    csv_file = request.FILES.get("file")
    if not csv_file:
        return Response({"error": "No file uploaded."}, status=400)

    reader = csv.DictReader(TextIOWrapper(csv_file, encoding='utf-8'))
    created_users = []

    for row in reader:
        username = row.get('username')
        email = row.get('email')
        if not username or not email:
            continue

        if User.objects.filter(username=username).exists():
            continue

        password = User.objects.make_random_password()
        user = User.objects.create_user(username=username, email=email, password=password)
        Student.objects.create(user=user)
        created_users.append(username)

        send_mail(
            subject="Student Account Created",
            message=f"Username: {username}\nPassword: {password}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

    return Response({"created": created_users}, status=201)

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAdminUser])
def manage_categories(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def categorize_student(request, pk):
    category_id = request.data.get('category_id')
    try:
        student = Student.objects.get(pk=pk)
        category = Category.objects.get(id=category_id)
        student.category = category
        student.save()
        return Response({"message": "Student categorized."})
    except (Student.DoesNotExist, Category.DoesNotExist):
        return Response({"error": "Student or category not found."}, status=404)


class AssignTaskView(generics.CreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAdminUser]

@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def review_submission(request, submission_id):
    submission = TaskSubmission.objects.get(id=submission_id)
    status = request.data.get('review_status')
    submission.review_status = status
    submission.save()
    return Response({"message": "Review updated."})



# Student-only: View their own profile and progress
class StudentDashboardView(generics.RetrieveAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsStudent]

    def get_object(self):
        return Student.objects.get(user=self.request.user)

# Admin-only: Upload marks for a student
class UploadMarksView(generics.CreateAPIView):
    serializer_class = MarksSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        marks = serializer.save()
        ActivityLog.objects.create(student=marks.student, action=f"Marks uploaded for {marks.subject}: {marks.score}")

# Student-only: View their own marks summary
class MarksSummaryView(generics.ListAPIView):
    serializer_class = MarksSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Marks.objects.filter(student__user=self.request.user)
class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    
    
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def generate_pdf_report(request, student_id):
    student = Student.objects.get(id=student_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student.user.username}_report.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 800, f"Report for {student.user.username}")
    p.drawString(100, 780, f"Degree Completed: {student.degree_completed}")
    p.drawString(100, 760, f"Category: {student.category or 'N/A'}")
    # Add more info...

    p.showPage()
    p.save()
    return response



class TaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Handle case where student profile might not exist
        try:
            return Task.objects.filter(student=self.request.user.student)
        except Student.DoesNotExist:
            return Task.objects.none()

class TaskDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        try:
            return Task.objects.filter(student=self.request.user.student)
        except Student.DoesNotExist:
            return Task.objects.none()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {'error': 'Task not found or not assigned to you'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        github_link = request.data.get('github_link')
        if not github_link:
            return Response(
                {'error': 'GitHub link is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        instance.github_link = github_link
        instance.status = 'submitted'
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
class StudentProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.student
        except Student.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        github_url = request.data.get('github_url')
        linkedin_url = request.data.get('linkedin_url')
        is_public = request.data.get('is_public')
        
        if github_url:
            instance.github_url = github_url
        if linkedin_url:
            instance.linkedin_url = linkedin_url
        if is_public is not None:
            instance.is_public = is_public
            
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class StudentProfileApprovalView(generics.CreateAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            profile = request.user.student
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        if profile.approval_requested:
            return Response(
                {'error': 'Approval already requested'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        profile.approval_requested = True
        profile.save()
        
        # Add notification logic here
        from django.core.mail import send_mail
        send_mail(
            'New Profile Approval Request',
            f'Student {request.user.username} has requested profile approval.',
            'from@example.com',
            ['admin@example.com'],
            fail_silently=False,
        )
        
        return Response(
            {'status': 'approval requested'}, 
            status=status.HTTP_200_OK
        )
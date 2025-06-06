from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Student, ActivityLog,  TaskSubmission, Category,Task
from .serializers import *
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework_simplejwt.views import TokenObtainPairView
from .permissions import IsStudent
from django.shortcuts import get_object_or_404
from django.utils import timezone  #
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import create_user_with_unique_username
import csv
from io import TextIOWrapper
from reportlab.pdfgen import canvas
from django.http import HttpResponse
import magic
from .permissions import IsSubAdmin
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import ValidationError  # needed for validate_file()
import openpyxl
from django.utils import timezone
from django.http import FileResponse
from tempfile import NamedTemporaryFile

# Admin-only: Create a new student and send email

@api_view(["POST"])
@permission_classes([permissions.AllowAny])   # login view
def jwt_login_view(request):
    login_id = request.data.get("username") or request.data.get("student_id")
    password = request.data.get("password")

    if not login_id or not password:
        return Response({"detail": "username/student_id and password required"},
                        status=400)

    # allow admission_number login
    try:
        user_obj = (User.objects.get(username=login_id) if
                    User.objects.filter(username=login_id).exists()
                    else Student.objects.get(admission_number=login_id).user)
    except (User.DoesNotExist, Student.DoesNotExist):
        return Response({"detail": "User not found"}, status=401)

    if not user_obj.check_password(password):
        return Response({"detail": "Invalid credentials"}, status=401)

    refresh = RefreshToken.for_user(user_obj)
    return Response({
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "is_admin": user_obj.is_admin,
        "is_subadmin": user_obj.is_subadmin,
        "is_student": user_obj.is_student,
        "username": user_obj.username,
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
class UploadCertificateView(generics.CreateAPIView):
    serializer_class = CertificateSerializer  # make one quickly or use FileSerializer
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        cert_file = request.FILES.get("certificate")
        if not cert_file:
            return Response({"error": "No file provided"}, status=400)
        Certificate.objects.create(
            student=student, file=cert_file, signed_by=request.user)
        return Response({"message": "Certificate uploaded"}, status=201)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def bulk_add_students(request):
    csv_file = request.FILES.get("file")
    if not csv_file:
        return Response({"error": "No file uploaded."}, status=400)

    reader = csv.DictReader(TextIOWrapper(csv_file, encoding='utf-8'))
    created_users = []

    for row in reader:
        email = row.get("email")
        first = row.get("first_name", "").strip()
        last  = row.get("last_name", "").strip()
        cat   = Category.objects.filter(name=row.get("category")).first()

        if not email or not first:
            continue
        if User.objects.filter(email=email).exists():
            continue

        pwd  = User.objects.make_random_password()
        user = create_user_with_unique_username(first, last, email, pwd, is_student=True)
        Student.objects.create(user=user, category=cat)
        created_users.append(user.username)

        try:
            send_mail(
                "Student Account Created",
                f"Username: {user.username}\nPassword: {pwd}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            # Log it or collect failed emails
            print(f"Email failed for {email}: {e}")



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



@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def review_submission(request, submission_id):
    try:
        submission = TaskSubmission.objects.get(id=submission_id)
    except TaskSubmission.DoesNotExist:
        return Response({'error': 'Submission not found'}, status=404)

    status_val = request.data.get('review_status')
    if not status_val:
        return Response({'error': 'review_status is required'}, status=400)

    submission.review_status = status_val
    submission.save()
    return Response({"message": "Review updated."})

class SubmissionStatusView(generics.ListAPIView):
    serializer_class = TaskSubmissionSerializer 
    permission_classes = [IsStudent]
    def get_queryset(self):
        return TaskSubmission.objects.filter(student=self.request.user.student)



# Student-only: View their own profile and progress
class StudentDashboardView(generics.RetrieveAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsStudent]

    def get_object(self):
        return Student.objects.get(user=self.request.user)



    
class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    
    
@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def generate_pdf_report(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{student.user.username}_report.pdf"'
    )

    p = canvas.Canvas(response)          # <-- create first
    p.drawString(100, 800, f"Report for {student.user.username}")
    p.drawString(100, 780, f"Degree Completed: {student.degree_completed}")
    p.drawString(100, 760, f"Category: {student.category or 'N/A'}")

    subs = TaskSubmission.objects.filter(student=student)
    p.drawString(100, 740, f"Total Submissions: {subs.count()}")

    p.showPage()
    p.save()
    return response




class TaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Handle case where student profile might not exist
        try:
            return Task.objects.filter(assigned_students=self.request.user.student)
        except Student.DoesNotExist:
            return Task.objects.none()

class TaskDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        try:
            return Task.objects.filter(assigned_students=self.request.user.student)
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
    
class SubmitTaskView(generics.CreateAPIView):
    permission_classes = [IsStudent]
    serializer_class = TaskSubmissionSerializer

    def create(self, request, *args, **kw):
        task = get_object_or_404(Task, pk=kw['pk'],
                                 assigned_students=request.user.student)
        submission, _ = TaskSubmission.objects.get_or_create(
            task=task, student=request.user.student)
        submission.submission_link = request.data['github_link']
        submission.submitted_at = timezone.now()
        submission.save()
        return Response(TaskSubmissionSerializer(submission).data)
    


    
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
            return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if profile.approval_requested:
            return Response({'error': 'Approval already requested'}, status=status.HTTP_400_BAD_REQUEST)
        
        profile.approval_requested = True
        profile.save()
        return Response({'message': 'Approval request submitted.'}, status=status.HTTP_200_OK)

class SubAdminStudentListView(generics.ListAPIView):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated, IsSubAdmin]

    def get_queryset(self):
        cats = self.request.user.subadmin.categories.all()
        return Student.objects.filter(category__in=cats)



ALLOWED_MIME_TYPES = ['application/pdf']

def validate_file(file):
    mime = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)
    if mime not in ALLOWED_MIME_TYPES:
        raise ValidationError("Invalid file type.")
    
    
    
    
    


class AdminResetStudentPassword(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, student_id):
        student = get_object_or_404(Student, pk=student_id)
        new_pw  = request.data.get("new_password")
        if not new_pw:
            return Response({"detail": "new_password required"}, status=400)

        student.user.set_password(new_pw)
        student.user.save(update_fields=["password"])

        send_mail(  # optional notification
            "Your password has been reset",
            f"Hello {student.user.first_name}, your new password: {new_pw}",
            settings.EMAIL_HOST_USER,
            [student.user.email],
            fail_silently=True,
        )
        return Response({"detail": "Password updated"})
    
    
@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def export_students_excel(request):
    """Download an .xlsx file with all students and key fields."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Students"

    # header
    headers = [
        "Admission #", "Full Name", "Username", "Email",
        "Category", "Degree Completed", "Created At"
    ]
    ws.append(headers)

    # rows
    for s in Student.objects.select_related("user", "category"):
        ws.append([
            s.admission_number,
            s.user.get_full_name(),
            s.user.username,
            s.user.email,
            s.category.name if s.category else "",
            "Yes" if s.degree_completed else "No",
            timezone.localtime(s.created_at).strftime("%Y-%m-%d"),
        ])

    # auto-width
    for col in ws.columns:
        max_length = max(len(str(cell.value)) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = max_length + 2

    # save to temp file
    tmp = NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(tmp.name)
    tmp.seek(0)

    filename = f"students_{timezone.now().date()}.xlsx"
    return FileResponse(tmp, as_attachment=True, filename=filename)
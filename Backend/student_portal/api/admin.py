from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, ActivityLog

# Registering the custom User model
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_student', 'is_admin', 'is_staff')
    list_filter = ('is_student', 'is_admin', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('is_student', 'is_admin')}),
    )

# Register Student model
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'degree_completed', 'created_at')
    list_filter = ('degree_completed',)
    search_fields = ('user__username', 'user__email')

# Register ActivityLog model
@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'action', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('student__user__username', 'action')

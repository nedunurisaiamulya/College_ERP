from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
#from import_export.admin import ImportExportModelAdmin
# Register your models here.
#username:ammu
#pswd:a


class ClassInline(admin.TabularInline):
    model = Class
    extra = 0


class DeptAdmin(admin.ModelAdmin):
    inlines = [ClassInline]
    list_display = ('name', 'id')
    search_fields = ('name', 'id')
    ordering = ['name']


class StudentInline(admin.TabularInline):
    model = Student
    extra = 0


class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'dept', 'sem', 'section')
    search_fields = ('id', 'dept__name', 'sem', 'section')
    ordering = ['dept__name', 'sem', 'section']
    inlines = [StudentInline]


class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'dept')
    search_fields = ('id', 'name', 'dept__name')
    ordering = ['dept', 'id']


class AssignTimeInline(admin.TabularInline):
    model = AssignTime
    extra = 0


class AssignAdmin(admin.ModelAdmin):
    inlines = [AssignTimeInline]
    list_display = ('class_id', 'course', 'teacher')
    search_fields = ('class_id__dept__name', 'class_id__id', 'course__name', 'teacher__name', 'course__shortname')
    ordering = ['class_id__dept__name', 'class_id__id', 'course__id']
    raw_id_fields = ['class_id', 'course', 'teacher']


class MarksInline(admin.TabularInline):
    model = Marks
    extra = 0


class StudentCourseAdmin(admin.ModelAdmin):
    inlines = [MarksInline]
    list_display = ('student', 'course',)
    search_fields = ('student__name', 'course__name', 'student__class_id__id', 'student__class_id__dept__name')
    ordering = ('student__class_id__dept__name', 'student__class_id__id', 'student__USN')


#@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('USN', 'name', 'class_id')
    search_fields = ('USN', 'name', 'class_id__id', 'class_id__dept__name')
    ordering = ['class_id__dept__name', 'class_id__id', 'USN']


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'dept')
    search_fields = ('name', 'dept__name')
    ordering = ['dept__name', 'name']


class SemAdmin(admin.ModelAdmin):
    list_display = ('year_sem', 'sem_class_id')
    search_fields = ('year_sem',)
    ordering = ['year_sem', ]


class SemMarksInline(admin.TabularInline):
    model = SemMarks
    extra = 0


class SemStudentCourseAdmin(admin.ModelAdmin):
    inlines = [SemMarksInline]
    list_display = ('student', 'sem', 'cgpa')
    search_fields = ('student__student_name',  'sem__year_sem', 'student__class_id', 'student__class_id__dept__name')
    ordering = ('student__class_id__dept__name', 'student__class_id__id', 'student__USN')


class TodoListAdmin(admin.ModelAdmin):
    list_display = ("title", "created", "due_date")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


admin.site.register(User, UserAdmin)
admin.site.register(Dept, DeptAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Assign, AssignAdmin)
admin.site.register(StudentCourse, StudentCourseAdmin)
admin.site.register(Sem, SemAdmin)
admin.site.register(SemStudentCourse, SemStudentCourseAdmin)
admin.site.register(TodoList, TodoListAdmin)
admin.site.register(Category, CategoryAdmin)
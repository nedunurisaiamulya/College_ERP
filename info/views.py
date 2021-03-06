from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import *
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Q
# Create your views here.


@login_required
def index(request):
    if request.user.is_teacher:
        return render(request, 'info/t_Dashboard.html', {'time':datetime.now()})
    if request.user.is_student:
        return render(request, 'info/S_Dashboard.html', {'time':datetime.now(), 'nbar': 'home'})
    return render(request, 'info/logout.html')


@login_required()
def attendance(request, stud_id):
    stud = Student.objects.get(USN=stud_id)
    ass_list = Assign.objects.filter(class_id_id=stud.class_id)
    att_list = []
    for ass in ass_list:
        try:
            a = AttendanceTotal.objects.get(student=stud, course=ass.course)
        except AttendanceTotal.DoesNotExist:
            a = AttendanceTotal(student=stud, course=ass.course)
            a.save()
        att_list.append(a)
    return render(request, 'info/attendance.html', {'att_list': att_list, 'nbar':'attendance'})


@login_required()
def attendance_detail(request, stud_id, course_id):
    stud = get_object_or_404(Student, USN=stud_id)
    cr = get_object_or_404(Course, id=course_id)
    att_list = Attendance.objects.filter(course=cr, student=stud).order_by('date')
    return render(request, 'info/att_detail.html', {'att_list': att_list, 'cr': cr, 'nbar':'attendance'})


# def student_search(request, class_id):
#     field = request.POST['fields']
#     search = request.POST['search']
#     class1 = get_object_or_404(Class, id=class_id)
#     if field == 'USN':
#         student_list = class1.student_set.filter(USN__icontains=search)
#     elif field == 'name':
#         student_list = class1.student_set.filter(name__icontains=search)
#     else:
#         student_list = class1.student_set.filter(sex__iexact=search)
#     return render(request, 'info/class1.html', {'class1': class1, 'student_list': student_list})


# Teacher Views

@login_required
def t_clas(request, teacher_id, choice):
    teacher1 = get_object_or_404(Teacher, id=teacher_id)
    if choice == 1:
        bar= {
            'nbar': 'Assign Attendance'}
    elif choice == 2:
        bar = {
            'nbar': 'Internal Marks'}
    elif choice == 3:
        bar = {
            'nbar': 'Semester'}
    print("------------------------", bar['nbar'])
    return render(request, 'info/t_clas.html', {'teacher1': teacher1, 'choice': choice, 'bar': bar['nbar']})


@login_required()
def t_student(request, assign_id):
    ass = Assign.objects.get(id=assign_id)
    att_list = []
    for stud in ass.class_id.student_set.all():
        print("*******************", stud)
        try:
            a = AttendanceTotal.objects.get(student=stud, course=ass.course)
        except AttendanceTotal.DoesNotExist:
            a = AttendanceTotal(student=stud, course=ass.course)
            a.save()
        att_list.append(a)
    return render(request, 'info/t_students.html', {'att_list': att_list,  'bar' :'Assign Attendance'})


@login_required()
def t_class_date(request, assign_id):
    now = timezone.now()
    ass = get_object_or_404(Assign, id=assign_id)
    att_list = ass.attendanceclass_set.filter(date__lte=now).order_by('-date')
    return render(request, 'info/t_class_date.html', {'att_list': att_list , 'bar':'Assign Attendance'})


@login_required()
def cancel_class(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    assc.status = 2
    assc.save()
    return HttpResponseRedirect(reverse('t_class_date', args=(assc.assign_id,)))


@login_required()
def t_attendance(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    ass = assc.assign
    c = ass.class_id
    context = {
        'ass': ass,
        'c': c,
        'assc': assc,
        'bar': 'Assign Attendance',
    }
    print("-----", context['bar'])
    return render(request, 'info/t_attendance.html', context)


@login_required()
def edit_att(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    cr = assc.assign.course
    att_list = Attendance.objects.filter(attendanceclass=assc, course=cr)
    context = {
        'assc': assc,
        'att_list': att_list,
        'bar' : 'Assign Attendance'
    }
    return render(request, 'info/t_edit_att.html', context)


@login_required()
def confirm(request, ass_c_id):
    assc = get_object_or_404(AttendanceClass, id=ass_c_id)
    ass = assc.assign
    cr = ass.course
    cl = ass.class_id
    for i, s in enumerate(cl.student_set.all()):
        status = request.POST[s.USN]
        if status == 'present':
            status = 'True'
        else:
            status = 'False'
        if assc.status == 1:
            try:
                a = Attendance.objects.get(course=cr, student=s, date=assc.date, attendanceclass=assc)
                a.status = status
                a.save()
            except Attendance.DoesNotExist:
                a = Attendance(course=cr, student=s, status=status, date=assc.date, attendanceclass=assc)
                a.save()
        else:
            a = Attendance(course=cr, student=s, status=status, date=assc.date, attendanceclass=assc)
            a.save()
            assc.status = 1
            assc.save()

    return HttpResponseRedirect(reverse('t_class_date', args=(ass.id,)))


@login_required()
def t_attendance_detail(request, stud_id, course_id):
    stud = get_object_or_404(Student, USN=stud_id)
    cr = get_object_or_404(Course, id=course_id)
    att_list = Attendance.objects.filter(course=cr, student=stud).order_by('date')
    return render(request, 'info/t_att_detail.html', {'att_list': att_list, 'cr': cr, 'bar' :'Assign Attendance'})


@login_required()
def change_att(request, att_id):
    a = get_object_or_404(Attendance, id=att_id)
    a.status = not a.status
    a.save()
    return HttpResponseRedirect(reverse('t_attendance_detail', args=(a.student.USN, a.course_id)))


@login_required()
def t_extra_class(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    c = ass.class_id
    context = {
        'ass': ass,
        'c': c,
        'bar':'Assign Attendance',
    }
    return render(request, 'info/t_extra_class.html', context)


@login_required()
def e_confirm(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    cr = ass.course
    cl = ass.class_id
    assc = ass.attendanceclass_set.create(status=1, date=request.POST['date'])
    assc.save()

    for i, s in enumerate(cl.student_set.all()):
        status = request.POST[s.USN]
        if status == 'present':
            status = 'True'
        else:
            status = 'False'
        date = request.POST['date']
        a = Attendance(course=cr, student=s, status=status, date=date, attendanceclass=assc)
        a.save()

    return HttpResponseRedirect(reverse('t_clas', args=(ass.teacher_id,1)))


@login_required()
def t_report(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    sc_list = []
    for stud in ass.class_id.student_set.all():
        a = StudentCourse.objects.get(student=stud, course=ass.course)
        sc_list.append(a)
    return render(request, 'info/t_report.html', {'sc_list': sc_list})


@login_required()
def timetable(request, class_id):
    asst = AssignTime.objects.filter(assign__class_id=class_id)
    matrix = [['' for i in range(8)] for j in range(6)]

    for i, d in enumerate(DAYS_OF_WEEK):
        t = 0
        for j in range(6):
            if j == 0:
                matrix[i][0] = d[0]
                continue
            if j == 4 : #or j == 8:
                continue
            try:
                a = asst.get(period=time_slots[t][0], day=d[0])
                matrix[i][j] = a.assign.course.shortname
            except AssignTime.DoesNotExist:
                pass
            t += 1

    context = {'matrix': matrix,
               'nbar': 'timetable',
               }
    return render(request, 'info/timetable.html', context)


@login_required()
def t_timetable(request, teacher_id):
    asst = AssignTime.objects.filter(assign__teacher_id=teacher_id)
    class_matrix = [[True for i in range(8)] for j in range(6)]
    for i, d in enumerate(DAYS_OF_WEEK):
        t = 0
        for j in range(8):
            if j == 0:
                class_matrix[i][0] = d[0]
                continue
            if j == 4 or j == 8:
                continue
            try:
                a = asst.get(period=time_slots[t][0], day=d[0])
                class_matrix[i][j] = a
            except AssignTime.DoesNotExist:
                pass
            t += 1
    context = {
        'class_matrix': class_matrix,
        'nbar': 'timetable',
    }
    return render(request, 'info/t_timetable.html', context)


@login_required()
def free_teachers(request, asst_id):
    asst = get_object_or_404(AssignTime, id=asst_id)
    ft_list = []
    t_list = Teacher.objects.filter(assign__class_id__id=asst.assign.class_id_id)
    for t in t_list:
        at_list = AssignTime.objects.filter(assign__teacher=t)
        if not any([True if at.period == asst.period and at.day == asst.day else False for at in at_list]):
            ft_list.append(t)

    return render(request, 'info/free_teachers.html', {'ft_list': ft_list})


# student marks


@login_required()
def marks_list(request, stud_id):
    stud = Student.objects.get(USN=stud_id,)
    ass_list = Assign.objects.filter(class_id_id=stud.class_id)
    sc_list = []
    for ass in ass_list:
        try:
            sc = StudentCourse.objects.get(student=stud, course=ass.course)
        except StudentCourse.DoesNotExist:
            sc = StudentCourse(student=stud, course=ass.course)
            sc.save()
            sc.marks_set.create(type='I', name='Internal test 1')
            sc.marks_set.create(type='I', name='Internal test 2')
            sc.marks_set.create(type='I', name='Internal test 3')
            sc.marks_set.create(type='E', name='Event 1')
            sc.marks_set.create(type='E', name='Event 2')
            sc.marks_set.create(type='S', name='Semester End Exam')
        sc_list.append(sc)

    return render(request, 'info/marks_list.html', {'sc_list': sc_list, 'nbar':'internal'})


# teacher marks


@login_required()
def t_marks_list(request, assign_id):
    ass = get_object_or_404(Assign, id=assign_id)
    m_list = MarksClass.objects.filter(assign=ass)
    return render(request, 'info/t_marks_list.html', {'m_list': m_list, 'bar':'Internal Marks'})


@login_required()
def t_marks_entry(request, marks_c_id):
    mc = get_object_or_404(MarksClass, id=marks_c_id)
    ass = mc.assign
    c = ass.class_id
    context = {
        'ass': ass,
        'c': c,
        'mc': mc,
    }
    return render(request, 'info/t_marks_entry.html', context)


@login_required()
def marks_confirm(request, marks_c_id):
    mc = get_object_or_404(MarksClass, id=marks_c_id)
    ass = mc.assign
    cr = ass.course
    cl = ass.class_id
    for s in cl.student_set.all():
        mark = request.POST[s.USN]
        sc = StudentCourse.objects.get(course=cr, student=s)
        m = sc.marks_set.get(name=mc.name)
        m.marks1 = mark
        m.save()
    mc.status = True
    mc.save()

    return HttpResponseRedirect(reverse('t_marks_list', args=(ass.id,)))


@login_required()
def edit_marks(request, marks_c_id):
    mc = get_object_or_404(MarksClass, id=marks_c_id)
    cr = mc.assign.course
    stud_list = mc.assign.class_id.student_set.all()
    m_list = []
    for stud in stud_list:
        sc = StudentCourse.objects.get(course=cr, student=stud)
        m = sc.marks_set.get(name=mc.name)
        m_list.append(m)
    context = {
        'mc': mc,
        'm_list': m_list,
        'bar':'Internal Marks'
    }
    return render(request, 'info/edit_marks.html', context)


@login_required()
def student_marks(request, assign_id):
    ass = Assign.objects.get(id=assign_id)
    sc_list = StudentCourse.objects.filter(student__in=ass.class_id.student_set.all(), course=ass.course)
    return render(request, 'info/t_student_marks.html', {'sc_list': sc_list, 'bar':'Internal Marks'})


#testing
def t_Dashboard(request):
    return render(request, 'info/t_Dashboard.html',{'time':datetime.now(), 'nbar': 'home'})


def t_semester(request, assign_id):
    # if request.GET.get('search'):
    #     search = request.GET.get('search')
    #     sem_list = SemStudentCourse.objects.all()
    #     sem_marks = SemMarks.objects.filter(Q(student_sem__student__USN=search) & Q(student_sem__sem__year_sem=sem))
    # content = {
    #     'USN' : search,
    #     'sem_marks': sem_marks,
    #     'sem_list': sem_list,
    # }
    return render(request, 'info/t_semester.html', {'bar':'Semester'})


def test(request, stud_id):
    sem_list = SemStudentCourse.objects.all()
    sem_marks = SemMarks.objects.filter(Q(student_sem__student__USN=stud_id) & Q(student_sem__sem__year_sem=sem))
    print(sem_list,'---------------------------------------------')
    content = {
        'USN': stud_id,
        'sem_marks': sem_marks,
        'sem_list': sem_list,
        'nbar': 'semester',
    }
    return  render(request, 'info/semester.html', content)


def sem(request, stud_id, sem):
    print('currebt sem ----------------------------------------------', stud_id , sem)
    sem_marks = SemMarks.objects.filter(Q(student_sem__student__USN=stud_id) & Q(student_sem__sem__year_sem=sem))
    context = {
        'USN':stud_id,
        'sem_marks' :sem_marks,
        'sem': sem,
        'nbar':'semester'
               }
    for i in sem_marks:
        print("********************", i.subject)
    return render(request, 'info/sem.html', context )


def t_profile(request):
    return render(request,'info/t_profile.html', {'bar' :'Profile'})


def profile(request):
    return render(request,'info/profile.html', {'bar' :'Profile'})


def stud_In(request, assign_id):
    ass = Assign.objects.get(id=assign_id)
    att_list = []
    for stud in ass.class_id.student_set.all():
        print("*******************", stud)
        try:
            a = AttendanceTotal.objects.get(student=stud, course=ass.course)
        except AttendanceTotal.DoesNotExist:
            a = AttendanceTotal(student=stud, course=ass.course)
            a.save()
        att_list.append(a)
    return render(request, 'info/stu_In_class.html', {'att_list': att_list,  'bar' :'Semester'})


def t_sem_details(request, stud_id):
    sem_list = SemStudentCourse.objects.all()
    content ={
        'USN': stud_id,
        'sem_list': sem_list,
        'bar': 'Semester',
    }
    print("........................",sem_list)
    return render(request, 'info/t_sem_details.html', content)


def sub(request, stud_id, sem):
    print('currebt sem ----------------------------------------------', stud_id , sem)
    sem_marks = SemMarks.objects.filter(Q(student_sem__student__USN=stud_id) & Q(student_sem__sem__year_sem=sem))
    context = {
        'USN':stud_id,
        'sem_marks' :sem_marks,
        'sem': sem,
        'bar':'Semester'
               }
    for i in sem_marks:
        print("********************", i.subject)
    return render(request, 'info/t_subjects.html', context )

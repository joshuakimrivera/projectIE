from django import template
from grading_system.models import SemesterFinalGrade, SubjectInstance, SubjectGrade
from django.contrib.auth import get_user_model
import re

User = get_user_model()

register = template.Library()


@register.simple_tag
def compute_gpa(semester_grade_id):
    total_units = 0
    pattern = r'^NSTP|PHED'
    semester_grade_instance = SemesterFinalGrade.objects.get(
        id=int(semester_grade_id))
    # get total units
    for subject_grade in semester_grade_instance.subject_grades.all():
        if subject_grade.final_grade not in (
                'P', 'W', 'D',
                'NOT S', 'INC', '') and not re.search(pattern, subject_grade.subject_instance.subject.subject_code):
            total_units = total_units + subject_grade.subject_instance.subject.units
    if not total_units:
        semester_grade_instance.grade = ''
        return ''
    raw_sum = 0.0
    # total oll the given grades
    for subject_grade in semester_grade_instance.subject_grades.all():
        try:
            if not re.search(pattern, subject_grade.subject_instance.subject.subject_code):
                raw_sum = raw_sum + \
                    (float(subject_grade.final_grade) *
                     subject_grade.subject_instance.subject.units)
        except ValueError:
            continue
    # compute the GPA
    result = str(round(raw_sum / total_units, 2))
    semester_grade_instance.grade = result
    semester_grade_instance.save()
    return result


@register.simple_tag
def is_already_enrolled(user_id, subject_instance_id):
    subject_instance = SubjectInstance.objects.get(id=int(subject_instance_id))
    user = User.objects.get(id=int(user_id))
    try:
        SubjectGrade.objects.get(
            subject_instance=subject_instance,
            student=user.student_profile
        )
        return True
    except SubjectGrade.DoesNotExist:
        return False

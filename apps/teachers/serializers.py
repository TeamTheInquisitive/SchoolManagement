from rest_framework import serializers
from .models import TeacherProfile, TeacherClassAssignment, CLASS_TEACHER_PRIVILEGES, SUBJECT_TEACHER_PRIVILEGES
from apps.accounts.serializers import UserSerializer


class TeacherClassAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherClassAssignment
        fields = ['id', 'class_name', 'section', 'subject', 'is_class_teacher', 'privileges', 'created_at']
        read_only_fields = ['id', 'created_at']


class TeacherProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class_assignments = TeacherClassAssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = TeacherProfile
        fields = ['id', 'user', 'employee_id', 'subject', 'qualification',
                  'specialization', 'joining_date', 'workload_hours', 'department',
                  'employment_type', 'class_assignments', 'created_at']
        read_only_fields = ['id', 'created_at']


class CreateTeacherSerializer(serializers.Serializer):
    employee_id = serializers.CharField(max_length=20)
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, default='')
    subject = serializers.CharField(max_length=100)
    qualification = serializers.CharField(max_length=255, required=False, default='')
    joining_date = serializers.DateField(required=False, allow_null=True)
    workload_hours = serializers.IntegerField(required=False, default=0)


class AssignClassSerializer(serializers.Serializer):
    class_name = serializers.CharField(max_length=20)
    section = serializers.CharField(max_length=10)
    subject = serializers.CharField(max_length=100)
    is_class_teacher = serializers.BooleanField(default=False)


class UpdatePrivilegesSerializer(serializers.Serializer):
    privileges = serializers.JSONField()


class ApplyTemplateSerializer(serializers.Serializer):
    template = serializers.ChoiceField(choices=['class_teacher', 'subject_teacher'])

    def get_privileges(self):
        return CLASS_TEACHER_PRIVILEGES if self.validated_data['template'] == 'class_teacher' else SUBJECT_TEACHER_PRIVILEGES

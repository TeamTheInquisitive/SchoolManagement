from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.core.permissions import IsAdmin
from apps.accounts.models import User
from .models import TeacherProfile, TeacherClassAssignment
from .serializers import (
    TeacherProfileSerializer, CreateTeacherSerializer,
    AssignClassSerializer, UpdatePrivilegesSerializer, ApplyTemplateSerializer,
)


class TeacherListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = TeacherProfileSerializer

    def get_queryset(self):
        return TeacherProfile.objects.filter(school=self.request.user.school).select_related('user')

    def create(self, request, *args, **kwargs):
        serializer = CreateTeacherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Create user account
        user = User.objects.create_user(
            email=data['email'], password='changeme123',
            full_name=data['full_name'], phone=data.get('phone', ''),
            role='teacher', school=request.user.school,
        )
        # Create teacher profile
        profile = TeacherProfile.objects.create(
            user=user, school=request.user.school,
            employee_id=data['employee_id'], subject=data['subject'],
            qualification=data.get('qualification', ''),
            joining_date=data.get('joining_date'),
            workload_hours=data.get('workload_hours', 0),
        )
        return Response(TeacherProfileSerializer(profile).data, status=status.HTTP_201_CREATED)


class TeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    serializer_class = TeacherProfileSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return TeacherProfile.objects.filter(school=self.request.user.school)

    def perform_destroy(self, instance):
        instance.user.is_active = False
        instance.user.save()


class AssignClassView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, id):
        teacher = TeacherProfile.objects.get(id=id, school=request.user.school)
        serializer = AssignClassSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment = TeacherClassAssignment.objects.create(teacher=teacher, **serializer.validated_data)
        from .serializers import TeacherClassAssignmentSerializer
        return Response(TeacherClassAssignmentSerializer(assignment).data, status=status.HTTP_201_CREATED)


class UpdatePrivilegesView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, id, assignment_id):
        assignment = TeacherClassAssignment.objects.get(
            id=assignment_id, teacher__id=id, teacher__school=request.user.school
        )
        serializer = UpdatePrivilegesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment.privileges = serializer.validated_data['privileges']
        assignment.save()
        from .serializers import TeacherClassAssignmentSerializer
        return Response(TeacherClassAssignmentSerializer(assignment).data)


class RemoveClassAssignmentView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, id, assignment_id):
        TeacherClassAssignment.objects.filter(
            id=assignment_id, teacher__id=id, teacher__school=request.user.school
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ApplyTemplateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, id, assignment_id):
        assignment = TeacherClassAssignment.objects.get(
            id=assignment_id, teacher__id=id, teacher__school=request.user.school
        )
        serializer = ApplyTemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assignment.privileges = serializer.get_privileges()
        assignment.save()
        from .serializers import TeacherClassAssignmentSerializer
        return Response(TeacherClassAssignmentSerializer(assignment).data)

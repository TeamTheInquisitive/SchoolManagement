from django.urls import path
from . import views

urlpatterns = [
    path('', views.TeacherListCreateView.as_view(), name='teacher_list_create'),
    path('<uuid:id>/', views.TeacherDetailView.as_view(), name='teacher_detail'),
    path('<uuid:id>/assign-class/', views.AssignClassView.as_view(), name='assign_class'),
    path('<uuid:id>/privileges/<uuid:assignment_id>/', views.UpdatePrivilegesView.as_view(), name='update_privileges'),
    path('<uuid:id>/class-assignment/<uuid:assignment_id>/', views.RemoveClassAssignmentView.as_view(), name='remove_assignment'),
    path('<uuid:id>/privileges/<uuid:assignment_id>/apply-template/', views.ApplyTemplateView.as_view(), name='apply_template'),
]

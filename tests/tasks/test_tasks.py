import json
from datetime import timedelta
from unittest.mock import Mock

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from accounts.models import Company, UserCompany
from invoices.models import Client
from tasks.models import Task, TaskCategory, TaskComment, TaskStatusHistory

User = get_user_model()


# ==================== FIXTURES ====================


@pytest.fixture
def user():
    """Utilisateur de test"""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def admin_user():
    """Utilisateur admin de test"""
    return User.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
    )


@pytest.fixture
def company(db):
    """Entreprise de test"""
    return Company.objects.create(
        name="Test Company",
        identifier="12345678901234",
        address="10 rue de Paris",
        postal_code="75000",
        city="Paris",
        country="France",
        contact_email="company@example.com",
    )


@pytest.fixture
def other_company(db):
    """Autre entreprise pour tester les permissions"""
    return Company.objects.create(
        name="Other Company",
        identifier="98765432109876",
        address="20 avenue de Lyon",
        postal_code="69000",
        city="Lyon",
        country="France",
        contact_email="other@example.com",
    )


@pytest.fixture
def company_user_link(user, company):
    """Lien entre utilisateur et entreprise"""
    return UserCompany.objects.create(
        user=user,
        company=company,
        is_primary=True,
    )


@pytest.fixture
def category(db):
    """Catégorie de tâche"""
    return TaskCategory.objects.create(
        code="DEV",
        name="Développement",
        description="Tâches de développement",
        is_active=True,
    )


@pytest.fixture
def customer(company):
    """Client de test"""
    return Client.objects.create(
        company=company,
        name="Test Client",
        identifier="12345678900000",
        contact_email="client@example.com",
        address="10 rue du Client",
        postal_code="75000",
        city="Paris",
        country="France",
    )


@pytest.fixture
def task(company, user, category, customer):
    """Tâche de test"""
    return Task.objects.create(
        title="Test Task",
        description="Description de test",
        company=company,
        created_by=user,
        assigned_to=user,
        category=category,
        client=customer,
        priority=2,
        status="pending",
        due_date=timezone.now() + timedelta(days=3),
    )


@pytest.fixture
def overdue_task(company, user):
    """Tâche en retard"""
    return Task.objects.create(
        title="Overdue Task",
        description="Tâche en retard",
        company=company,
        created_by=user,
        assigned_to=user,
        priority=1,
        status="pending",
        due_date=timezone.now() - timedelta(days=2),
    )


# ==================== TESTS TASK_LIST ====================


@pytest.mark.django_db
class TestTaskList:
    def test_task_list_no_company(self, client, user):
        client.force_login(user)
        url = reverse("tasks:task_list")
        response = client.get(url)
        assert response.status_code == 400
        assert "Aucune entreprise associée" in response.content.decode()

    def test_task_list_success(self, client, user, company_user_link, task):
        client.force_login(user)
        url = reverse("tasks:task_list")
        response = client.get(url)
        assert response.status_code == 200
        assert "tasks" in response.context
        assert task in response.context["tasks"]

    def test_task_list_filter_by_status(
        self, client, user, company_user_link, task, company
    ):
        completed_task = Task.objects.create(
            title="Completed Task",
            company=company,
            created_by=user,
            status="completed",
        )
        client.force_login(user)
        url = reverse("tasks:task_list") + "?status=completed"
        response = client.get(url)
        assert response.status_code == 200
        assert completed_task in response.context["tasks"]
        assert task not in response.context["tasks"]

    def test_task_list_filter_by_client(
        self, client, user, company_user_link, task, company
    ):
        task_without_client = Task.objects.create(
            title="Task without client",
            company=company,
            created_by=user,
        )
        client.force_login(user)
        url = reverse("tasks:task_list") + f"?client={task.client.id}"
        response = client.get(url)
        assert response.status_code == 200
        assert task in response.context["tasks"]
        assert task_without_client not in response.context["tasks"]

    def test_task_list_sort_by_due_date(
        self, client, user, company_user_link, task, company
    ):
        urgent_task = Task.objects.create(
            title="Urgent Task",
            company=company,
            created_by=user,
            due_date=timezone.now() + timedelta(days=1),
        )
        client.force_login(user)
        url = reverse("tasks:task_list") + "?sort=due_date"
        response = client.get(url)
        tasks_list = list(response.context["tasks"])
        assert tasks_list[0] == urgent_task
        assert tasks_list[1] == task

    def test_task_list_statistics(
        self, client, user, company_user_link, task, overdue_task
    ):
        client.force_login(user)
        url = reverse("tasks:task_list")
        response = client.get(url)
        stats = response.context["stats"]
        assert stats["total"] == 2
        assert stats["pending"] == 2
        assert stats["overdue"] == 1


# ==================== TESTS GET_TASKS (AJAX) ====================


@pytest.mark.django_db
class TestGetTasks:
    def test_get_tasks_urgency_sort(self, client, user, company, task):
        client.force_login(user)
        url = reverse("tasks:get_tasks") + "?sort=urgency"
        response = client.get(url)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert "tasks" in data

    def test_get_tasks_due_date_sort(self, client, user, company, task):
        client.force_login(user)
        url = reverse("tasks:get_tasks") + "?sort=due_date"
        response = client.get(url)
        assert response.status_code == 200

    def test_get_tasks_only_assigned(self, client, user, company_user_link, company):
        other_user = User.objects.create_user(
            username="other", email="other@test.com", password="pass"
        )
        Task.objects.create(
            title="My Task", company=company, assigned_to=user, status="pending"
        )
        Task.objects.create(
            title="Other Task",
            company=company,
            assigned_to=other_user,
            status="pending",
        )
        client.force_login(user)
        url = reverse("tasks:get_tasks")
        response = client.get(url)
        data = json.loads(response.content)
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "My Task"


# ==================== TESTS CREATE/EDIT TASK ====================


@pytest.mark.django_db
class TestCreateOrEditTask:
    def test_create_task_get(self, client, user, company_user_link, category):
        client.force_login(user)
        url = reverse("tasks:create_task")
        response = client.get(url)
        assert response.status_code == 200
        assert "categories" in response.context
        assert category in response.context["categories"]

    def test_create_task_post(self, client, user, company_user_link, category):
        client.force_login(user)
        url = reverse("tasks:create_task")
        data = {
            "title": "New Task",
            "description": "Description",
            "category": category.id,
            "priority": 2,
            "due_date": (timezone.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
        }
        response = client.post(url, data)
        assert response.status_code == 302
        task = Task.objects.get(title="New Task")
        assert task.description == "Description"
        assert task.category == category
        assert task.priority == 2
        assert task.created_by == user

    def test_create_task_no_company(self, client, user):
        client.force_login(user)
        url = reverse("tasks:create_task")
        response = client.post(url, {"title": "Test"})
        assert response.status_code == 400

    def test_edit_task_get(self, client, user, company_user_link, task):
        client.force_login(user)
        url = reverse("tasks:task_edit", kwargs={"task_id": task.id})
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["task"] == task

    def test_edit_task_post(self, client, user, company_user_link, task):
        client.force_login(user)
        url = reverse("tasks:task_edit", kwargs={"task_id": task.id})
        response = client.post(
            url,
            {
                "title": "Updated Task",
                "description": "Updated description",
                "priority": 1,
            },
        )
        assert response.status_code == 302
        task.refresh_from_db()
        assert task.title == "Updated Task"
        assert task.priority == 1

    def test_edit_task_permission_denied(
        self, client, user, other_company, company_user_link
    ):
        other_task = Task.objects.create(
            title="Other Task", company=other_company, created_by=user
        )
        client.force_login(user)
        url = reverse("tasks:task_edit", kwargs={"task_id": other_task.id})
        response = client.get(url)
        assert response.status_code == 403


# ==================== TESTS TASK_DETAIL ====================


@pytest.mark.django_db
class TestTaskDetail:
    def test_task_detail_success(self, client, user, company_user_link, task):
        client.force_login(user)
        url = reverse("tasks:task_detail", kwargs={"task_id": task.id})
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["task"] == task

    def test_task_detail_with_comments(self, client, user, company_user_link, task):
        comment = TaskComment.objects.create(
            task=task, user=user, comment="Test comment"
        )
        client.force_login(user)
        url = reverse("tasks:task_detail", kwargs={"task_id": task.id})
        response = client.get(url)
        assert comment in response.context["comments"]

    def test_task_detail_permission_denied(self, client, user, other_company):
        other_task = Task.objects.create(title="Other Task", company=other_company)
        client.force_login(user)
        url = reverse("tasks:task_detail", kwargs={"task_id": other_task.id})
        response = client.get(url)
        assert response.status_code == 403


# ==================== TESTS UPDATE STATUS ====================


@pytest.mark.django_db
class TestTaskUpdateStatus:
    def test_update_status_success(self, client, user, company_user_link, task):
        client.force_login(user)
        url = reverse("tasks:update_status", kwargs={"task_id": task.id})
        response = client.post(url, {"status": "in_progress", "notes": "Started work"})
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["success"] is True
        assert data["new_status"] == "in_progress"

    def test_update_status_completed(self, client, user, company_user_link, task):
        client.force_login(user)
        url = reverse("tasks:update_status", kwargs={"task_id": task.id})
        client.post(url, {"status": "completed"})
        task.refresh_from_db()
        assert task.status == "completed"
        assert task.completed_at is not None

    def test_update_status_creates_history(self, client, user, company_user_link, task):
        client.force_login(user)
        url = reverse("tasks:update_status", kwargs={"task_id": task.id})
        client.post(url, {"status": "in_progress", "notes": "Test note"})
        history = TaskStatusHistory.objects.filter(task=task).first()
        assert history is not None

    def test_update_status_invalid(self, client, user, company_user_link, task):
        client.force_login(user)
        url = reverse("tasks:update_status", kwargs={"task_id": task.id})
        response = client.post(url, {"status": "invalid_status"})
        assert response.status_code == 400

    def test_update_status_get_method(self, client, user, company_user_link, task):
        client.force_login(user)
        url = reverse("tasks:update_status", kwargs={"task_id": task.id})
        response = client.get(url)
        assert response.status_code == 405


# ==================== TESTS ADD COMMENT ====================


@pytest.mark.django_db
class TestTaskAddComment:
    def test_add_comment_success(self, client, user, company_user_link, task):
        client.force_login(user)
        url = reverse("tasks:add_comment", kwargs={"task_id": task.id})
        response = client.post(url, {"comment": "Test comment", "is_internal": "true"})
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["success"] is True
        assert data["comment"] == "Test comment"

    def test_add_comment_empty(self, client, user, company_user_link, task):
        client.force_login(user)
        url = reverse("tasks:add_comment", kwargs={"task_id": task.id})
        response = client.post(url, {"comment": "   "})
        assert response.status_code == 400

    def test_add_comment_external(self, client, user, company_user_link, task):
        client.force_login(user)
        url = reverse("tasks:add_comment", kwargs={"task_id": task.id})
        client.post(url, {"comment": "External comment", "is_internal": "false"})
        comment = TaskComment.objects.get(task=task)
        assert comment.is_internal is False


# ==================== TESTS ASSIGN ====================


@pytest.mark.django_db
class TestTaskAssign:
    def test_assign_task_success(self, client, admin_user, company_user_link, task):
        other_user = User.objects.create_user(
            username="assigned", email="assigned@test.com", password="pass"
        )
        other_user.get_full_name = Mock(return_value="Assigned User")
        client.force_login(admin_user)
        url = reverse("tasks:assign", kwargs={"task_id": task.id})
        response = client.post(url, {"user_id": other_user.id})
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["success"] is True

    def test_assign_task_permission_denied(self, client, user, company_user_link, task):
        user.is_admin = Mock(return_value=False)
        client.force_login(user)
        url = reverse("tasks:assign", kwargs={"task_id": task.id})
        response = client.post(url, {"user_id": user.id})
        assert response.status_code == 403

    def test_assign_task_unassign(self, client, admin_user, company_user_link, task):
        client.force_login(admin_user)
        url = reverse("tasks:assign", kwargs={"task_id": task.id})
        client.post(url, {})
        task.refresh_from_db()
        assert task.assigned_to is None


# ==================== TESTS API SUMMARY ====================


@pytest.mark.django_db
class TestApiTasksSummary:
    def test_tasks_summary(self, client, user, company_user_link, task, overdue_task):
        Task.objects.create(
            title="Urgent",
            company=company_user_link.company,
            assigned_to=user,
            priority=1,
            urgency_score=80,
            status="pending",
        )
        client.force_login(user)
        url = reverse("tasks:api_summary")
        response = client.get(url)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert "my_tasks" in data

    def test_tasks_summary_by_type(self, client, user, company_user_link, company):
        Task.objects.create(
            title="Payment Task",
            company=company,
            assigned_to=user,
            task_type="payment_overdue",
            status="pending",
        )
        client.force_login(user)
        url = reverse("tasks:api_summary")
        response = client.get(url)
        data = json.loads(response.content)
        assert "by_type" in data

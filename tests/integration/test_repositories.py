import uuid
import pytest
from internal.domain.errors import ErrNotFound, ErrAlreadyExists, ErrConflict
from internal.domain.models import User, Subject, Attendance
from internal.repository.postgres import (
    PostgresUserRepository, PostgresSubjectRepository, PostgresAttendanceRepository,
)


def unique(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def test_subject_create_and_read(test_pool):
    repo = PostgresSubjectRepository(test_pool)
    created = repo.create(Subject(name=unique("Алгоритмы")))
    assert created.subject_id
    assert repo.get_by_id(created.subject_id).name == created.name
    repo.delete(created.subject_id)


def test_missing_subject_returns_not_found(test_pool):
    repo = PostgresSubjectRepository(test_pool)
    with pytest.raises(ErrNotFound):
        repo.get_by_id(str(uuid.uuid4()))


def test_duplicate_subject_returns_already_exists(test_pool):
    repo = PostgresSubjectRepository(test_pool)
    name = unique("Базы данных")
    first = repo.create(Subject(name=name))
    try:
        with pytest.raises(ErrAlreadyExists):
            repo.create(Subject(name=name))
    finally:
        repo.delete(first.subject_id)


def test_list_respects_limit(test_pool):
    repo = PostgresSubjectRepository(test_pool)
    created = [repo.create(Subject(name=unique("Тестовый предмет"))) for _ in range(4)]
    try:
        assert len(repo.list(limit=2, offset=0)) <= 2
    finally:
        for item in created:
            repo.delete(item.subject_id)


def test_update_and_delete(test_pool):
    repo = PostgresSubjectRepository(test_pool)
    item = repo.create(Subject(name=unique("Физика")))
    changed_name = unique("Физика обновлённая")
    item.name = changed_name
    repo.update(item)
    assert repo.get_by_id(item.subject_id).name == changed_name
    repo.delete(item.subject_id)
    with pytest.raises(ErrNotFound):
        repo.get_by_id(item.subject_id)


def test_user_get_by_email_sql_injection_is_data(test_pool):
    user_repo = PostgresUserRepository(test_pool)
    role_name = unique("test_role")
    with test_pool.connection() as conn:
        role = conn.execute(
            "INSERT INTO roles (name) VALUES (%s) RETURNING role_id", (role_name,)
        ).fetchone()
    user = user_repo.create(User(
        role_id=str(role["role_id"]), first_name="Тест", last_name="Пользователь",
        email=unique("user") + "@example.test", password_hash="test_hash",
    ))
    try:
        assert user.created_at is not None
        assert "password_hash" not in user.to_public_dict()
        with pytest.raises(ErrNotFound):
            user_repo.get_by_email("' OR '1'='1")
        assert user_repo.get_by_email(user.email).user_id == user.user_id
    finally:
        user_repo.delete(user.user_id)
        with test_pool.connection() as conn:
            conn.execute("DELETE FROM roles WHERE role_id = %s", (role["role_id"],))


def test_attendance_create_read_update_delete(test_pool):
    """Проверяет CRUD отметки, создавая минимальный набор связанных записей."""
    attendance_repo = PostgresAttendanceRepository(test_pool)
    user_repo = PostgresUserRepository(test_pool)
    subject_repo = PostgresSubjectRepository(test_pool)
    suffix = uuid.uuid4().hex[:10]
    with test_pool.connection() as conn:
        role = conn.execute("INSERT INTO roles(name) VALUES (%s) RETURNING role_id", (f"role_{suffix}",)).fetchone()
        faculty = conn.execute("INSERT INTO faculties(name) VALUES (%s) RETURNING faculty_id", (f"faculty_{suffix}",)).fetchone()
        dept = conn.execute("INSERT INTO departments(faculty_id,name) VALUES (%s,%s) RETURNING department_id", (faculty["faculty_id"], f"dept_{suffix}")).fetchone()
        group = conn.execute("INSERT INTO student_groups(department_id,name,admission_year) VALUES (%s,%s,2024) RETURNING group_id", (dept["department_id"], f"group_{suffix}")).fetchone()
    student = user_repo.create(User(role_id=str(role["role_id"]), group_id=str(group["group_id"]),
                                    first_name="Иван", last_name="Тестов", email=f"{suffix}@example.test", password_hash="hash"))
    teacher = user_repo.create(User(role_id=str(role["role_id"]), first_name="Анна", last_name="Преподаватель", email=f"teacher_{suffix}@example.test", password_hash="hash"))
    subject = subject_repo.create(Subject(name=f"Предмет_{suffix}"))
    with test_pool.connection() as conn:
        lesson = conn.execute(
            "INSERT INTO lessons(subject_id,group_id,teacher_id,lesson_date) VALUES (%s,%s,%s,now()) RETURNING lesson_id",
            (subject.subject_id, group["group_id"], teacher.user_id),
        ).fetchone()
    item = attendance_repo.create(Attendance(lesson_id=str(lesson["lesson_id"]), student_id=student.user_id,
                                             marked_by=teacher.user_id, status="present", method="manual"))
    try:
        assert item.attendance_id
        assert attendance_repo.get_by_id(item.attendance_id).status == "present"
        item.status = "late"
        attendance_repo.update(item)
        assert attendance_repo.get_by_id(item.attendance_id).status == "late"
        attendance_repo.delete(item.attendance_id)
        with pytest.raises(ErrNotFound):
            attendance_repo.get_by_id(item.attendance_id)
    finally:
        with test_pool.connection() as conn:
            conn.execute("DELETE FROM lessons WHERE lesson_id = %s", (lesson["lesson_id"],))
        subject_repo.delete(subject.subject_id)
        user_repo.delete(student.user_id)
        user_repo.delete(teacher.user_id)
        with test_pool.connection() as conn:
            conn.execute("DELETE FROM student_groups WHERE group_id = %s", (group["group_id"],))
            conn.execute("DELETE FROM departments WHERE department_id = %s", (dept["department_id"],))
            conn.execute("DELETE FROM faculties WHERE faculty_id = %s", (faculty["faculty_id"],))
            conn.execute("DELETE FROM roles WHERE role_id = %s", (role["role_id"],))

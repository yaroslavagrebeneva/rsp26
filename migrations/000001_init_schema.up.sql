-- CheckIn: начальная схема PostgreSQL по ER-модели проекта.
-- UUID генерируется PostgreSQL 16; таблицы и связи создаются в порядке зависимостей.

CREATE TABLE roles (
    role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    CONSTRAINT chk_roles_name CHECK (length(trim(name)) > 0)
);

CREATE TABLE faculties (
    faculty_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    CONSTRAINT chk_faculties_name CHECK (length(trim(name)) > 0)
);

CREATE TABLE departments (
    department_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    faculty_id UUID NOT NULL REFERENCES faculties(faculty_id) ON DELETE RESTRICT,
    name VARCHAR(255) NOT NULL,
    CONSTRAINT uq_departments_faculty_name UNIQUE (faculty_id, name),
    CONSTRAINT chk_departments_name CHECK (length(trim(name)) > 0)
);
CREATE INDEX idx_departments_faculty_id ON departments(faculty_id);

CREATE TABLE student_groups (
    group_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    department_id UUID NOT NULL REFERENCES departments(department_id) ON DELETE RESTRICT,
    name VARCHAR(100) NOT NULL UNIQUE,
    admission_year SMALLINT NOT NULL CHECK (admission_year BETWEEN 2000 AND 2100),
    CONSTRAINT chk_student_groups_name CHECK (length(trim(name)) > 0)
);
CREATE INDEX idx_student_groups_department_id ON student_groups(department_id);

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id UUID NOT NULL REFERENCES roles(role_id) ON DELETE RESTRICT,
    group_id UUID REFERENCES student_groups(group_id) ON DELETE SET NULL,
    department_id UUID REFERENCES departments(department_id) ON DELETE SET NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(30),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_users_first_name CHECK (length(trim(first_name)) > 0),
    CONSTRAINT chk_users_last_name CHECK (length(trim(last_name)) > 0),
    CONSTRAINT chk_users_email CHECK (position('@' IN email) > 1)
);
CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_users_group_id ON users(group_id);
CREATE INDEX idx_users_department_id ON users(department_id);

CREATE TABLE subjects (
    subject_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    CONSTRAINT chk_subjects_name CHECK (length(trim(name)) > 0)
);

CREATE TABLE teacher_subjects (
    teacher_subject_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    subject_id UUID NOT NULL REFERENCES subjects(subject_id) ON DELETE RESTRICT,
    CONSTRAINT uq_teacher_subject UNIQUE (teacher_id, subject_id)
);
CREATE INDEX idx_teacher_subjects_teacher_id ON teacher_subjects(teacher_id);
CREATE INDEX idx_teacher_subjects_subject_id ON teacher_subjects(subject_id);

CREATE TABLE lessons (
    lesson_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id UUID NOT NULL REFERENCES subjects(subject_id) ON DELETE RESTRICT,
    group_id UUID NOT NULL REFERENCES student_groups(group_id) ON DELETE RESTRICT,
    teacher_id UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    lesson_date TIMESTAMPTZ NOT NULL,
    lesson_type VARCHAR(50) NOT NULL DEFAULT 'lecture',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_lessons_type CHECK (lesson_type IN ('lecture', 'practice', 'laboratory', 'seminar', 'other'))
);
CREATE INDEX idx_lessons_subject_id ON lessons(subject_id);
CREATE INDEX idx_lessons_group_id ON lessons(group_id);
CREATE INDEX idx_lessons_teacher_id ON lessons(teacher_id);
CREATE INDEX idx_lessons_date ON lessons(lesson_date);

CREATE TABLE qr_sessions (
    qr_session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID NOT NULL REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT chk_qr_session_expiry CHECK (expires_at > created_at)
);
CREATE INDEX idx_qr_sessions_lesson_id ON qr_sessions(lesson_id);
CREATE INDEX idx_qr_sessions_expires_at ON qr_sessions(expires_at);

CREATE TABLE attendance (
    attendance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID NOT NULL REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    qr_session_id UUID REFERENCES qr_sessions(qr_session_id) ON DELETE SET NULL,
    marked_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'absent',
    method VARCHAR(20) NOT NULL DEFAULT 'manual',
    marked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_attendance_lesson_student UNIQUE (lesson_id, student_id),
    CONSTRAINT chk_attendance_status CHECK (status IN ('present', 'absent', 'late')),
    CONSTRAINT chk_attendance_method CHECK (method IN ('qr', 'manual', 'teacher')),
    CONSTRAINT chk_attendance_qr_method CHECK (method <> 'qr' OR qr_session_id IS NOT NULL)
);
CREATE INDEX idx_attendance_lesson_id ON attendance(lesson_id);
CREATE INDEX idx_attendance_student_id ON attendance(student_id);
CREATE INDEX idx_attendance_qr_session_id ON attendance(qr_session_id);
CREATE INDEX idx_attendance_marked_by ON attendance(marked_by);

CREATE TABLE absence_reasons (
    reason_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attendance_id UUID NOT NULL REFERENCES attendance(attendance_id) ON DELETE CASCADE,
    reason_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    reviewed_at TIMESTAMPTZ,
    CONSTRAINT chk_absence_reason_type CHECK (reason_type IN ('illness', 'family', 'personal', 'other')),
    CONSTRAINT chk_absence_reason_status CHECK (status IN ('pending', 'accepted', 'rejected')),
    CONSTRAINT chk_absence_reason_description CHECK (length(trim(description)) > 0)
);
CREATE INDEX idx_absence_reasons_attendance_id ON absence_reasons(attendance_id);
CREATE INDEX idx_absence_reasons_status ON absence_reasons(status);

CREATE TABLE documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reason_id UUID NOT NULL REFERENCES absence_reasons(reason_id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_documents_file_name CHECK (length(trim(file_name)) > 0),
    CONSTRAINT chk_documents_file_path CHECK (length(trim(file_path)) > 0)
);
CREATE INDEX idx_documents_reason_id ON documents(reason_id);

CREATE TABLE teacher_comments (
    comment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reason_id UUID NOT NULL REFERENCES absence_reasons(reason_id) ON DELETE CASCADE,
    teacher_id UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    comment TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_teacher_comments_comment CHECK (length(trim(comment)) > 0)
);
CREATE INDEX idx_teacher_comments_reason_id ON teacher_comments(reason_id);
CREATE INDEX idx_teacher_comments_teacher_id ON teacher_comments(teacher_id);

CREATE TABLE explanation_requests (
    request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attendance_id UUID NOT NULL REFERENCES attendance(attendance_id) ON DELETE CASCADE,
    teacher_id UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    student_id UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    message TEXT NOT NULL,
    response_text TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    answered_at TIMESTAMPTZ,
    CONSTRAINT chk_explanation_requests_status CHECK (status IN ('pending', 'answered', 'cancelled')),
    CONSTRAINT chk_explanation_requests_message CHECK (length(trim(message)) > 0)
);
CREATE INDEX idx_explanation_requests_attendance_id ON explanation_requests(attendance_id);
CREATE INDEX idx_explanation_requests_teacher_id ON explanation_requests(teacher_id);
CREATE INDEX idx_explanation_requests_student_id ON explanation_requests(student_id);
CREATE INDEX idx_explanation_requests_status ON explanation_requests(status);

CREATE TABLE curator_groups (
    curator_group_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    curator_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    group_id UUID NOT NULL REFERENCES student_groups(group_id) ON DELETE CASCADE,
    CONSTRAINT uq_curator_group UNIQUE (curator_id, group_id)
);
CREATE INDEX idx_curator_groups_curator_id ON curator_groups(curator_id);
CREATE INDEX idx_curator_groups_group_id ON curator_groups(group_id);

CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    group_id UUID REFERENCES student_groups(group_id) ON DELETE SET NULL,
    student_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_notifications_type CHECK (length(trim(type)) > 0),
    CONSTRAINT chk_notifications_title CHECK (length(trim(title)) > 0)
);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_group_id ON notifications(group_id);
CREATE INDEX idx_notifications_student_id ON notifications(student_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);

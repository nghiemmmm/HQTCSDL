from enum import Enum


class quyen(str, Enum):
    PGV = "PGV"
    GIANG_VIEN = "GIANGVIEN"
    SINH_VIEN = "SINHVIEN"


class Permission(str, Enum):
    CREATE_USER = "create_user"

    VIEW_SUBJECT = "view_subject"
    CREATE_SUBJECT = "create_subject"
    UPDATE_SUBJECT = "update_subject"
    DELETE_SUBJECT = "delete_subject"

    VIEW_CLASS = "view_class"
    CREATE_CLASS = "create_class"
    UPDATE_CLASS = "update_class"
    DELETE_CLASS = "delete_class"

    VIEW_STUDENT = "view_student"
    CREATE_STUDENT = "create_student"
    UPDATE_STUDENT = "update_student"
    DELETE_STUDENT = "delete_student"

    VIEW_TEACHER = "view_teacher"
    CREATE_TEACHER = "create_teacher"
    UPDATE_TEACHER = "update_teacher"
    DELETE_TEACHER = "delete_teacher"

    VIEW_QUESTION = "view_question"
    CREATE_QUESTION = "create_question"
    UPDATE_QUESTION = "update_question"
    DELETE_QUESTION = "delete_question"

    VIEW_EXAM_REGISTRATION = "view_exam_registration"
    CREATE_EXAM_REGISTRATION = "create_exam_registration"
    UPDATE_EXAM_REGISTRATION = "update_exam_registration"
    DELETE_EXAM_REGISTRATION = "delete_exam_registration"

    TAKE_EXAM = "take_exam"
    PRACTICE_EXAM = "practice_exam"

    VIEW_OWN_SCORE = "view_own_score"
    VIEW_STUDENT_SCORE = "view_student_score"
    VIEW_SCORE_REPORT = "view_score_report"

    VIEW_OWN_EXAM = "view_own_exam"
    VIEW_STUDENT_EXAM = "view_student_exam"
    PRINT_SCORE_TABLE = "print_score_table"


ROLE_PERMISSIONS = {
    quyen.PGV: [
        Permission.CREATE_USER,

        Permission.VIEW_SUBJECT,
        Permission.CREATE_SUBJECT,
        Permission.UPDATE_SUBJECT,
        Permission.DELETE_SUBJECT,

        Permission.VIEW_CLASS,
        Permission.CREATE_CLASS,
        Permission.UPDATE_CLASS,
        Permission.DELETE_CLASS,

        Permission.VIEW_STUDENT,
        Permission.CREATE_STUDENT,
        Permission.UPDATE_STUDENT,
        Permission.DELETE_STUDENT,

        Permission.VIEW_TEACHER,
        Permission.CREATE_TEACHER,
        Permission.UPDATE_TEACHER,
        Permission.DELETE_TEACHER,

        Permission.VIEW_QUESTION,
        Permission.CREATE_QUESTION,
        Permission.UPDATE_QUESTION,
        Permission.DELETE_QUESTION,

        Permission.VIEW_EXAM_REGISTRATION,
        Permission.CREATE_EXAM_REGISTRATION,
        Permission.UPDATE_EXAM_REGISTRATION,
        Permission.DELETE_EXAM_REGISTRATION,

        Permission.VIEW_STUDENT_SCORE,
        Permission.VIEW_SCORE_REPORT,
        Permission.VIEW_STUDENT_EXAM,
        Permission.PRINT_SCORE_TABLE,
    ],

    quyen.GIANG_VIEN: [
        Permission.VIEW_QUESTION,
        Permission.CREATE_QUESTION,
        Permission.UPDATE_QUESTION,
        Permission.DELETE_QUESTION,

        Permission.VIEW_EXAM_REGISTRATION,
        Permission.CREATE_EXAM_REGISTRATION,
        Permission.UPDATE_EXAM_REGISTRATION,
        Permission.PRACTICE_EXAM,
        Permission.VIEW_STUDENT_SCORE,
        Permission.VIEW_SCORE_REPORT,
        Permission.VIEW_STUDENT_EXAM,
        Permission.PRINT_SCORE_TABLE,
    ],

    quyen.SINH_VIEN: [
        Permission.TAKE_EXAM,
        Permission.VIEW_OWN_SCORE,
        Permission.VIEW_OWN_EXAM,
    ],
}


def get_user_permissions(role: str) -> list[Permission]:
    try:
        role_enum = quyen(role)
        return ROLE_PERMISSIONS.get(role_enum, [])
    except ValueError:
        return []


def has_permission(user_role: str, required_permission: Permission | str) -> bool:
    permissions = get_user_permissions(user_role)
    try:
        permission = Permission(required_permission)
    except ValueError:
        return False

    return permission in permissions

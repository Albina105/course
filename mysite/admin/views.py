from mysite.database.models import User, RefreshToken, Category, Course, StudyGroup, Application, Enrollment

from sqladmin import ModelView


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.full_name, User.email, User.role, User.user_status]

class RefreshTokenAdmin(ModelView, model=RefreshToken):
    column_list = [RefreshToken.id, RefreshToken.user_id, RefreshToken.created_at]

class CategoryAdmin(ModelView, model=Category):
    column_list = [Category.id, Category.category_name]

class CourseAdmin(ModelView, model=Course):
    column_list = [Course.id, Course.title, Course.level, Course.price, Course.is_active]

class StudyGroupAdmin(ModelView, model=StudyGroup):
    column_list = [StudyGroup.id, StudyGroup.name, StudyGroup.course_id, StudyGroup.teacher_id, StudyGroup.status]

class ApplicationAdmin(ModelView, model=Application):
    column_list = [Application.id, Application.student_id, Application.course_id, Application.status]

class EnrollmentAdmin(ModelView, model=Enrollment):
    column_list = [Enrollment.id, Enrollment.student_id, Enrollment.group_id, Enrollment.status]

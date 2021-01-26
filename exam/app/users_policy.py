from flask_login import current_user

ADMIN_ROLE_ID = 1
MODERATOR_ID = 2
USER_ID=3

def is_admin():
    return current_user.role_id == ADMIN_ROLE_ID

def is_moderator():
    return current_user.role_id == MODERATOR_ID

def is_user():
    return current_user.role_id == USER_ID

class UsersPolicy:

    def __init__(self, record= None):
        self.record = record

    def edit_films(self):
        return is_admin() or is_moderator()

    def show(self):
        is_showing_user=current_user.id == self.record.id
        return is_admin() or is_showing_user or is_moderator() or is_user()

    def new(self):
        return is_admin() 

    def delete(self):
        return is_admin() 

    def make_review(self):
        return is_admin() or is_moderator() or is_user()

    def edit_reviews(self):
        return is_moderator() or is_admin()
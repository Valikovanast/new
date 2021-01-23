from flask_login import current_user

ADMIN_ROLE_ID = 1

def is_admin():
    return current_user.role_id == ADMIN_ROLE_ID

class UsersPolicy:

    def __init__(self, record= None):
        self.record = record

    def edit(self):
        is_editing_user=current_user.id == self.record.id
        return is_admin() or is_editing_user

    def show(self):
        is_showing_user=current_user.id == self.record.id
        return is_admin() or is_showing_user

    def new(self):
        return is_admin() 

    def delete(self):
        return is_admin() 
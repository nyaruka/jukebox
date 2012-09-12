from django.contrib.auth.models import User, Group
from django import forms
from smartmin.views import *
from smartmin.users.views import *

class UserCRUDL(UserCRUDL):
     actions = ('create','update','list', 'register')


     class Register(SmartCreateView):
        form_class = UserForm
        permission = None
        success_message = "User Registered Successfully."
        success_url = '@users.user_login'
        fields = ('username', 'new_password', 'first_name', 'last_name', 'email', )
        field_config = {
            'groups': dict(help="Users will only get those permissions that are allowed for their group."),
            'new_password': dict(label="Password"),
            'groups': dict(help="Users will only get those permissions that are allowed for their group."),
            'new_password': dict(help="Set the user's initial password here."),
        }

        
            
        def post_save(self, obj):
            """
            Make sure our groups are up to date
            """
            group = Group.objects.get(name="Viewers")
            obj.groups.add(group)

            return obj

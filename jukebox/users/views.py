from smartmin.views import *

class UserCRUDL(smartmin.users.UserCRUDL):
     class Register(SmartCreateView):
        form_class = UserForm
        permission = None
        success_message = "User Registered Successfully."
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

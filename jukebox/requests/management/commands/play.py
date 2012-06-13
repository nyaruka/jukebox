from django.core.management.base import BaseCommand, CommandError
import datetime
from optparse import make_option
from requests.models import Request
from subprocess import call
import sys
import os
from time import sleep

class Command(BaseCommand):
    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        
        lock_file = '/tmp/player.lock'
        if os.path.exists(lock_file):
            sys.exit(0)
        else:
            call(["touch", lock_file])

        try:
            while(True):
                try:
                    playlist = Request.objects.filter(status='Q').order_by('created_on')
                    for request in playlist:
                        request.status = 'P'
                        request.save()

                        try:
                            call(["mpg123", request.track.mp3_file.path])
                        except:
                            import traceback
                            traceback.print_exc()
                            sys.exit(1)
                        finally:
                            request.status = 'C'
                            request.save()

                    if not playlist:
                        sleep(5)

                except:
                    import traceback
                    traceback.print_exc()
                    sys.exit(1)

        finally:
            call(["rm", lock_file])

            
                    
            

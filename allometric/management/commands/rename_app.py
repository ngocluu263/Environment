from django.core.management.base import BaseCommand
import json

class Command(BaseCommand):
    help = u"Rename app in json dump"

    def handle(self, *args, **options):
        try:
            old_app = args[0]
            new_app = args[1]
            filename = args[2]
        except IndexError:
            print u'usage :', __name__.split('.')[-1], 'old_app new_app dumpfile.json'
            return

        try:
            dump_file = open(filename, 'r')
        except IOError:
            print filename, u"doesn't exist"
            return

        objects = json.loads(dump_file.read())
        dump_file.close()

        for obj in objects:
            obj["model"] = obj["model"].replace(old_app, new_app, 1)

            if obj["fields"].has_key("content_type") and (old_app == obj["fields"]["content_type"][0]):
                obj["fields"]["content_type"][0] = new_app

        dump_file = open(filename, 'w')
        dump_file.write(json.dumps(objects, indent=4))
        dump_file.close()

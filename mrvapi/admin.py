from django.contrib import admin
from mrvapi.models import Project, ProjectBoundary, Parcel, Plot, Tree

class TreeInline(admin.TabularInline):
    model = Tree
    #fields = ('genus','species','dbh')
    extra = 0
    
class PlotInline(admin.StackedInline):
    model = Plot
    #fields = ('name','shape_reported','area_reported')
    inlines = [TreeInline, ]
    extra = 0

class ParcelInline(admin.StackedInline):
    model = Parcel
    #fields = ('name','area_reported')
    inlines = [PlotInline, ]
    extra = 0

    # I must force this Admin Model to use Model.delete() and not the more efficient QuerySet.delete()
    # as I have overridden the Parcel.delete() method to prohibit deletion of last parcel in a project
    # See: http://stackoverflow.com/a/1471977/1545769 and https://github.com/django/django/commit/5bdee2556e
    actions=['delete_selected_one_at_a_time']
    def get_actions(self, request):
        actions = super(PhotoBlogEntryAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions
    def delete_selected_one_at_a_time(self, request, queryset):
        for obj in queryset:
            obj.delete()
        if queryset.count() == 1:
            message_bit = "1 photoblog entry was"
        else:
            message_bit = "%s photoblog entries were" % queryset.count()
        self.message_user(request, "%s successfully deleted." % message_bit)
        # FIXME: This success message is incorrect if you tried to delete the 
        # last parcel, which is silently suppressed in Parcel.delete()
    delete_selected_one_at_a_time.short_description = "Delete selected parcels"


class ProjectBoundaryInline(admin.TabularInline):
    model = ProjectBoundary
    extra = 0


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name','owner','abstract','nUploads','nBoundaries','nParcels','nPlots','nTrees')

    inlines = [ProjectBoundaryInline, ParcelInline, ]

    def nUploads(self, obj):
        return len(Upload.objects.filter(project=obj))

    def nBoundaries(self, obj):
        return len(ProjectBoundary.objects.filter(project=obj))

    def nParcels(self, obj):
        return len(Parcel.objects.filter(project=obj))

    def nPlots(self, obj):
        return len(Plot.objects.filter(parcel__project=obj))

    def nTrees(self, obj):
        return len(Tree.objects.filter(plot__parcel__project=obj))

admin.site.register(Project, ProjectAdmin)

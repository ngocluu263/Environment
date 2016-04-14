from django.conf.urls import patterns, url, include
#from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView
from core.views import *


urlpatterns = patterns('',
                       # Add user page
                       url(r'^settings/$', SettingsView.as_view(), name='settings'),
                       url(r'^account/$', AccountView.as_view(), name='account'),
                       url(r'^utilities/$', UtilitiesView.as_view(), name='utilities'),
                       url(r'^splash/$', SplashView.as_view(), name='splash'),
                       url(r'^dashboard/$', ProjectDashboardView.as_view(), name='project-dashboard'),
                       url(r'^utilities/add_user/$', AddUserView.as_view(), name='add_user'),
                       url(r'^utilities/copy_project/$', CopyProjectView.as_view(), name='copy_project'),
                       url(r'^utilities/copy_project/success/$', CopyProjectSuccessView.as_view(), name='copy_project_success'),
                       url(r'^utilities/copy_project/reset/(?P<pk>\d+)/$', CopyProjectResetSecretView, name='copy_project_reset_secret'),
                       #url(r'^utilities/aeq/$', ListAEQ.as_view(), name='aeq_list'),
                       #url(r'^utilities/aeq/add/$', CreateAEQ.as_view(), name='aeq_create'),
                       url(r'^project/add/$', CreateProjectView.as_view(), name='create-project'),
                       #url(r'^utilities/aeq/(?P<pk>\d+)/update/$', UpdateAEQ.as_view(), name='aeq_update'),
                       #url(r'^utilities/aeq/(?P<pk>\d+)/delete/confirm/$', DeleteAEQ.as_view(), name='aeq_delete_confirm'),
                       #url(r'^utilities/aeq/(?P<pk>\d+)/delete/$', 'core.views.deleteAEQ', name='delete_aeq'),
                       url(r'^debug/$', 'core.views.debug', name='debug'),
                       url(r'^switch-project/(?P<project_id>\d+)/$', 'core.views.switchproject', name='switch-project'),
                       url(r'^edit_project/(?P<pk>\d+)/$', EditProjectView.as_view(), name='edit-project'),
                       url(r'^review_project/(?P<pk>\d+)/$', ReviewProjectView.as_view(), name='review-project'),
                       url(r'^project_documents/(?P<pk>\d+)/$', ProjectDocumentsView.as_view(), name='project-documents'),
                       url(r'^delete/(?P<pk>\d+)/$', 'core.views.deleteproject', name='delete-project'),
                       url(r'^create-parcel/(?P<pk>\d+)/$', CreateParcelView.as_view(), name='create-parcel'),
                       url(r'^project-settings/(?P<pk>\d+)/$', ProjectSettingsView.as_view(), name='project-settings'),
                       url(r'^project-settings/(?P<pk>\d+)/copy_project/$', CopyProjectSettings, name='copy-project-settings'),
                       url(r'^project-settings/add-user/(?P<pk>\d+)/$', AddUserProject.as_view(), name='add-user-project'),
                       url(r'^project_documents/(?P<pk>\d+)/deletefolder/(?P<ppk>\d+)/$', 'core.views.deleteFolder', name='delete-folder'),
                       url(r'^project_documents/(?P<pk>\d+)/upload/(?P<ppk>\d+)/$', 'core.views.documentUpload', name='upload_folder'),
                       url(r'^project_documents/(?P<pk>\d+)/download/$', 'core.views.zipDownload', name="download-document"),
                       url(r'^project-settings/list_permissions/(?P<pk>\d+)/$', ListUsersProject.as_view(), name='list-permissions')
                       )

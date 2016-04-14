from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView
from models import *
from forms import LandCover_Form, Practice_Form, Parcel_Form, ReferenceScenario_Form, ProjectScenario_Form
from views import *
#from django.core.urlresolvers import reverse
#from django.contrib.auth.views import login

urlpatterns = patterns('',
    #url(r'^$', HomeView.as_view(), name='ecalc-home'),
    url(r'^$', ProjectsView.as_view(), name='ecalc-home'),  # changed HomeView to Projects List View after adding mroe tools to WOYP section

    url(r'^setup/$', 'ecalc.views.setup', name='setup'),

    # Reporting
    url(r'^project/(?P<pk>\d+)/report/$', ReportWizardView.as_view(REPORT_WIZARD_FORMS), name='ecalc-report-wizard'),
    url(r'^project/(?P<pk>\d+)/report/ccmtt/$', ReportWizardGEFTrackingToolCCM, name='ecalc-report-wizard-gef-tt-ccm'),
    url(r'^project/(?P<pk>\d+)/report/sfmtt/$', ReportWizardGEFTrackingToolSFM, name='ecalc-report-wizard-gef-tt-sfm'),
    
    # Projects
    url(r'^projects/$', 
        ProjectsView.as_view(), name="ecalc-projects"),
    url(r'^project/(?P<pk>\d+)/$', 
        ProjectView.as_view(), name="ecalc-project"),    
    url(r'^project/new/$', 
        CreateProjectView.as_view(), name="ecalc-project-new"),
    url(r'^project/(?P<pk>\d+)/delete/$', 
        DeleteView_.as_view(model=Project, success_url='/ecalc/projects/'), name="ecalc-project-del"),
    
    # Land Covers
    url(r'^project/(?P<ppk>\d+)/landcovers/$',
        ListView_.as_view(model=LandCover), name=LandCover.get_list_urlname()),
    url(r'^project/(?P<ppk>\d+)/landcover/(?P<pk>\d+)/$',
        UpdateLandcover.as_view(model=LandCover,form_class=LandCover_Form), name=LandCover.get_absolute_urlname()),
    url(r'^project/(?P<ppk>\d+)/landcover/new/$',
        CreateLandcover.as_view(model=LandCover,form_class=LandCover_Form, template_name='ecalc/create_landcover_form.html'), name=LandCover.get_new_urlname()),
    url(r'^project/(?P<ppk>\d+)/landcover/newpu/$',
        CreateViewPopup.as_view(model=LandCover,form_class=LandCover_Form), name=LandCover.get_newpu_urlname()),                       
    url(r'^project/(?P<ppk>\d+)/landcover/(?P<pk>\d+)/delete',
        'ecalc.views.DeleteLandcover', name=LandCover.get_delete_urlname()),
    
    # Practice
    url(r'^project/(?P<ppk>\d+)/practices/$',
        ListView_.as_view(model=Practice), name=Practice.get_list_urlname()),
    url(r'^project/(?P<ppk>\d+)/practice/(?P<pk>\d+)/$',
        UpdatePractice.as_view(model=Practice,form_class=Practice_Form), name=Practice.get_absolute_urlname()),
    url(r'^project/(?P<ppk>\d+)/practice/new/$',
        CreatePractice.as_view(model=Practice,form_class=Practice_Form, template_name='ecalc/create_practice_form.html'), name=Practice.get_new_urlname()),
    url(r'^project/(?P<ppk>\d+)/practice/newpu/$',
        CreateViewPopup.as_view(model=Practice,form_class=Practice_Form), name=Practice.get_newpu_urlname()), 
    url(r'^project/(?P<ppk>\d+)/practice/(?P<pk>\d+)/delete',
        'ecalc.views.DeletePractice', name=Practice.get_delete_urlname()),
                       
    # Wizard views
    url(r'^wiz/(?P<pk>\d+)/review/$', 'ecalc.views.review_project', name='ecalc-step-1'),
    url(r'^wiz/project/$',
        CreateProjectView.as_view(wiz_nexturlname='ecalc-wiz-parcel'), name='ecalc-wiz-project'),
    # url(r'^wiz/(?P<ppk>\d+)/tempparcel/$',
    #     CreateParcelView.as_view(model=Parcel, form_class=Parcel_Form, wiz_nexturlname='ecalc-refscenario') name='ecalc-wiz-parcel-temp'),
    url(r'^wiz/(?P<ppk>\d+)/parcel/$',
        CreateView_.as_view(model=Parcel,template_name='ecalc/create_parcel_form.html',form_class=Parcel_Form,wiz_nexturlname='ecalc-wiz-refscenario'), name='ecalc-wiz-parcel'),
    #url(r'^wiz/(?P<ppk>\d+)/practice/$',
    #    CreateView_.as_view(model=Practice,form_class=Practice_Form,wiz_nexturlname='ecalc-wiz-basescenario'), name='ecalc-wiz-practice'),
    url(r'^wiz/(?P<ppk>\d+)/scenario/base/$',
        CreateScenarioView.as_view(model=Scenario, form_class=ReferenceScenario_Form, wiz_nexturlname='ecalc-wiz-projscenario', template_name='ecalc/reference_scenario_form.html'), name='ecalc-wiz-refscenario'),
    url(r'^wiz/(?P<ppk>\d+)/scenario/test/$',
        CreateScenarioView.as_view(model=Scenario, form_class=ProjectScenario_Form, template_name='ecalc/project_scenario_form.html'), name='ecalc-wiz-projscenario'),
    
    # Parcels
    url(r'^project/(?P<ppk>\d+)/parcels/$',
        ListView_.as_view(model=Parcel), name=Parcel.get_list_urlname()),
    url(r'^project/(?P<ppk>\d+)/parcel/(?P<pk>\d+)/$',
        ParcelUpdateView.as_view(model=Parcel,form_class=Parcel_Form), name=Parcel.get_absolute_urlname()),
    url(r'^project/(?P<ppk>\d+)/parcel/new/$',
        CreateView_.as_view(model=Parcel,form_class=Parcel_Form,template_name='ecalc/create_parcel_form.html'), name=Parcel.get_new_urlname()),
    url(r'^project/(?P<ppk>\d+)/parcel/(?P<pk>\d+)/delete',
        'ecalc.views.DeleteParcel', name='ecalc-parcel-delete'),


    # Reference Scenarios
    url(r'^project/(?P<ppk>\d+)/refscenarios/$', 
        RefScenarioListView.as_view(), name='ecalc-referencescenarios'),
    url(r'^project/(?P<ppk>\d+)/refscenario/(?P<pk>\d+)/$',
        UpdateScenarioView.as_view(model=Scenario,form_class=ReferenceScenario_Form, template_name='ecalc/reference_scenario_form.html'), name='ecalc-referencescenario'),
    url(r'^project/(?P<ppk>\d+)/refscenario/new/$',
        CreateScenarioView.as_view(model=Scenario,form_class=ReferenceScenario_Form, template_name='ecalc/reference_scenario_form.html'), name='ecalc-referencescenario-new'),
    url(r'^project/(?P<ppk>\d+)/refscenario/(?P<pk>\d+)/delete',
        'ecalc.views.DeleteScenario', name='ecalc-referencescenario-del'),

    # Project Scenarios
    url(r'^project/(?P<ppk>\d+)/projscenarios/$', 
        ProjScenarioListView.as_view(), name='ecalc-projectscenarios'),
    url(r'^project/(?P<ppk>\d+)/projscenario/(?P<pk>\d+)/$',
        UpdateProjScenarioView.as_view(model=Scenario,form_class=ProjectScenario_Form, template_name='ecalc/project_scenario_form.html'), name='ecalc-projectscenario'),
    url(r'^project/(?P<ppk>\d+)/projscenario/new/$',
        CreateScenarioView.as_view(model=Scenario,form_class=ProjectScenario_Form, template_name='ecalc/project_scenario_form.html'), name='ecalc-projectscenario-new'),
    url(r'^project/(?P<ppk>\d+)/projscenario/(?P<pk>\d+)/delete',
        'ecalc.views.DeleteScenario', name='ecalc-projectscenario-del'),  
    
    # Carbonpools
    url(r'^project/(?P<ppk>\d+)/scenario/(?P<spk>\d+)/results/$',
        CarbonPoolsView.as_view(), name='ecalc-carbonpools'),
    #url(r'^project/(?P<project_id>\d+)/scenario/(?P<scenario_id>\d+)/results/graph/$', 'ecalc.graphs.serve_scenario_graph', name='scenario_graph'),

    # Create test
    url(r'^createtest/(?P<name>.*)/$', 'ecalc.views.createtest', name='ecalc-createtest'),
    #url(r'^project/PrepopulateForm/$', 'ecalc.views.PrepopulateProjectForm', name='ecalc-prepopulate'),
    url(r'^core/', include('core.urls')),
)

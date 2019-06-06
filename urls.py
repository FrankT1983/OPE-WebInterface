from django.conf.urls import  url
from django.contrib import admin
from . import views
admin.autodiscover()

# remember: if new parameter name is introduced and the @login_required decorator is used in the function it has
# to be added to the lokal decorator implemenation of @login_required




urlpatterns = [
    url(r'^(?i)CreateWorkflow/$', views.CreateWorkflow, name='CreateWorkflow'),
    url(r'^(?i)GetWorkflow/(?P<workflowId>[0-9]+)/$', views.GetWorkflow, name='GetWorkflow'),
    url(r'^(?i)GetBlock/(?P<blocktype>[a-zA-Z0-9.]+)/$', views.GetBlock, name='GetBlock'),
    url(r'^(?i)PrepareRun/(?P<workflowId>[0-9]+)/$',views.PrepareRun, name='PrepareRun'),
    url(r'^(?i)ExecuteRun/(?P<workflowId>[0-9]+)/$', views.ExecuteRun, name='ExecuteRun'),
    url(r'^(?i)ViewWorkflows/$', views.ViewWorkflows, name='ViewWorkflows'),
    url(r'^(?i)ViewWorkResultPreview/(?P<runId>[a-z0-9.-]+)/(?P<blockId>[a-zA-Z0-9.]+)/(?P<portId>[a-zA-Z0-9.]+)/(?P<datasetId>[0-9]+)/$', views.ViewWorkResultPreview, name='ViewWorkResultPreview'),
    url(r'^(?i)ViewWorkResultFromFile/(?P<fileId>[0-9]+)/$', views.ViewResultFile, name='ViewResultFile'),
    url(r'^(?i)ViewRunStatistics/(?P<runId>[a-z0-9.-]+)/(?P<datasetId>[0-9]+)/$', views.ViewRunStatistics, name='ViewRunStatistics'),
    url(r'^$', views.oppWelcomePage, name='oppWelcomePage'),
    url(r'^(?i)ViewRunOverview/$', views.ViewRunOverview, name='ViewRunOverview'),
    url(r'^(?i)ViewRunStatistics/(?P<runId>[a-z0-9.-]+)/(?P<datasetId>[0-9]+)/$', views.ViewRunStatistics, name='ViewRunStatistics'),
    url(r'^(?i)GetGitVersions/(?P<gitUrl>[\w|\W]+)/(?P<gitPath>[\w|\W]+)/$', views.GetGitVersions, name='GetGitVersions'),
    url(r'^(?i)DeleteWorkflow/(?P<workflowId>[0-9]+)/$', views.DeleteWorkflow, name='DeleteWorkflow'),

    url(r'^(?i)CreateWorkflow/save/$', views.save),   # for debugging env
    url(r'^(?i)save/$',views.save),

    url(r'^(?i)getThumbAddress/(?P<imageId>[0-9]+)/$', views.getThumbAddress , name="getThumbAddress")
    ]

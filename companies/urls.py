from django.conf.urls import url
from . import views

app_name = 'companies'

urlpatterns = [
    # /companies/
    url(r'^$', views.IndexView.as_view(), name='index'),

    # /companies/list/
    url(r'^list/$', views.CompanyView.as_view(), name='company_list'),

    # /companies/graphs/
    url(r'^graphs/$', views.BokehView.as_view(), name='bokeh'),

    # /companies/directors/
    url(r'^directors/$', views.DirectorView.as_view(), name='director_list'),

    # /companies/listings/
    url(r'^listings/$', views.ListingView.as_view(), name='listing_list'),

    # /companies/listings/<listing_id>/
    url(r'^listings/(?P<pk>[0-9]+)/$', views.ListingDetailView.as_view(), name='listing_detail'),

    # /companies/directors/<director_id>/
    url(r'^directors/(?P<pk>[0-9]+)/$', views.DirectorDetailView.as_view(), name='director_detail'),

    # /companies/register
    url(r'^register/$', views.UserFormView.as_view(), name='register'),

    # /companies/<company_id>/
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),

    # /companies/company/add/
    url(r'company/add/$', views.CompanyCreate.as_view(), name='company-add'),

    # /company/2/
    url(r'company/(?P<pk>[0-9]+)/$', views.CompanyUpdate.as_view(), name='company-update'),

    # /music/company/2/delete/
    url(r'company/(?P<pk>[0-9]+)/delete/$', views.CompanyDelete.as_view(), name='company-delete'),

    # /companies/api/companies/
    url(r'^api/companies/', views.CompanyList.as_view(), name='company-api'),

    # /companies/api/ticker/
    url(r'^api/ticker/', views.TickerList.as_view(), name='ticker-api'),

    # /companies/api/directors/
    url(r'^api/directors/', views.DirectorList.as_view(), name='director-api'),

    # /companies/api/boardmembers/
    url(r'^api/boardmembers/', views.BoardMemberList.as_view(), name='boardmember-api'),

]

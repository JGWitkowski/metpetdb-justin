from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# from django.views.generic.simple import direct_to_template
# from django.views.generic.simple import redirect_to
# from django.views.generic import TemplateView


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from tastyapi.resources import SampleResource, RockTypeResource, \
                               SubsampleResource, SubsampleTypeResource, \
                               ReferenceResource, ChemicalAnalysisResource, \
                               MineralResource, UserResource, RegionResource, \
                               MetamorphicGradeResource, \
                               MetamorphicRegionResource
from tastypie.api import Api

api_v1 = Api(api_name='v1')
api_v1.register(UserResource())
api_v1.register(SampleResource())
api_v1.register(RockTypeResource())
api_v1.register(SubsampleResource())
api_v1.register(SubsampleTypeResource())
api_v1.register(ReferenceResource())
api_v1.register(ChemicalAnalysisResource())
api_v1.register(MineralResource())
api_v1.register(RegionResource())
api_v1.register(MetamorphicGradeResource())
api_v1.register(MetamorphicRegionResource())

urlpatterns = patterns('',
url(r'^webservices/sample/(\d+)/$','webservices.views.sample', name='sample'),
url(r'^webservices/subsample/(\d+)/$','webservices.views.subsample', name='subsample'),
url(r'^webservices/chemicalanalysis/(\d+)/$', 'webservices.views.chemicalanalysis', name='chemanalysis'),
url(r'^api/metpetdb/$','webservices.views.metpetdb'),
#sample list url
url(r'^webservices/samplelist/$', 'webservices.views.samplelist', name='samplelist'),
url(r'^$', 'webservices.views.index', name='index'),
url(r'^search/$', 'webservices.views.search', name='search'),
#api calls
url(r'^webservices/sample/(\d+)/json/$','webservices.api.sample'),
url(r'^webservices/subsample/(\d+)/json/$','webservices.api.subsample'),
url(r'^webservices/chemicalanalysis/(\d+)/json$', 'webservices.api.chemical_analysis'),
url(r'^webservices/sample/(\d+)/images/json/$','webservices.views.sample_images'),
#below URLs- Not sure if these are used anywhere as of now
url(r'^webservices/samples$', 'webservices.views.samples'),
url(r'^webservices/chemicalanalyses$', 'webservices.views.chemical_analyses'),

url(r'tastyapi/', include(api_v1.urls)),
# url(r'tastyapi/views/access/(\d+)','tastyapi.views.access', name='access'),

    # Examples:
    # url(r'^$', 'metpetdb.views.home', name='home'),
    # url(r'^metpetdb/', include('metpetdb.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
# url(r'^admin/', include(admin.site.urls)),
)
urlpatterns+=staticfiles_urlpatterns()


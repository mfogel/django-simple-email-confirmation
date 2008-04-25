from django.conf.urls.defaults import *

from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    
    (r'^$', direct_to_template, {"template": "homepage.html"}),
    (r'^signup/$', 'devtest.views.signup'),
    
    (r'^admin/', include('django.contrib.admin.urls')),
)

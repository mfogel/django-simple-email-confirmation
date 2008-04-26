from django.conf.urls.defaults import *

from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    
    (r'^$', direct_to_template, {"template": "homepage.html"}),
    (r'^signup/$', 'devtest.views.signup'),
    (r'^login/$', 'django.contrib.auth.views.login', {"template_name": "login.html"}),
    (r'^logout/$', 'django.contrib.auth.views.logout', {"template_name": "logout.html"}),
    
    (r'^admin/', include('django.contrib.admin.urls')),
)

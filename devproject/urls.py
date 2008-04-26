from django.conf.urls.defaults import *

urlpatterns = patterns('',
    
    (r'^$', 'devtest.views.homepage'),
    
    (r'^signup/$', 'devtest.views.signup'),
    (r'^login/$', 'django.contrib.auth.views.login', {"template_name": "login.html"}),
    (r'^logout/$', 'django.contrib.auth.views.logout', {"template_name": "logout.html"}),
    
    (r'^confirm_email/(\w+)/$', 'emailconfirmation.views.confirm_email'),
    
    (r'^admin/', include('django.contrib.admin.urls')),
)

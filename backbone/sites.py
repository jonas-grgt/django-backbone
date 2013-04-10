class BackboneSite(object):

    def __init__(self, name='backbone'):
        self._registry = []
        self.name = name

    def register(self, backbone_view_class, **kwargs):
        """
        Registers the given backbone view class.
        Can take url_path_prefix, url_path_suffix or base_url_name as extra parameters.
        """
        kwargs.update(backbone_view_class=backbone_view_class)

        if backbone_view_class not in self._registry:
            self._registry.append(kwargs)

    def unregister(self, backbone_view_class):
        for registered_view in self._registry:
            if backbone_view_class == registered_view.get('backbone_view_class'):
                self._registry.remove(registered_view)

    def generate_url(self, registered_view):
        try:
            from django.conf.urls import url, patterns
        except ImportError:  # For backwards compatibility with Django <=1.3
            from django.conf.urls.defaults import url, patterns

        view_class = registered_view.get('backbone_view_class')

        app_label = view_class.model._meta.app_label
        module_name = view_class.model._meta.module_name

        if 'url_path_prefix' in registered_view:
            url_path = r'^%s' % registered_view.get('url_path_prefix')
        else:
            url_path = r'^%s/%s' % (app_label, module_name)

        if 'url_path_suffix' in registered_view:
            url_path += registered_view.get('url_path_suffix')

        if 'base_url_name' in registered_view:
            base_url_name = registered_view.get('base_url_name')
        else:
            base_url_name = '%s_%s' % (app_label, module_name)

        return patterns('',
            url(url_path + '$', view_class.as_view(), name=base_url_name),
            url(url_path + '/(?P<id>\d+)$', view_class.as_view(),
                name=base_url_name + '_detail')
        )

    def get_urls(self):
        try:
            from django.conf.urls import patterns
        except ImportError:  # For backwards compatibility with Django <=1.3
            from django.conf.urls.defaults import patterns

        urlpatterns = patterns('')
        for registered_view in self._registry:
            urlpatterns += self.generate_url(registered_view)
        return urlpatterns

    @property
    def urls(self):
        return (self.get_urls(), 'backbone', self.name)

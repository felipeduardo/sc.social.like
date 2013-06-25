# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from Products.Five import BrowserView
from sc.social.like.controlpanel.likes import LikeControlPanelAdapter
from sc.social.like.interfaces import IHelperView
from sc.social.like.plugins import IPlugin
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.interface import implements


class HelperView(BrowserView):
    """ Social Like configuration helpers
    """
    implements(IHelperView)

    def __init__(self, context, request, *args, **kwargs):
        super(HelperView, self).__init__(context, request, *args, **kwargs)
        context = aq_inner(context)
        self.context = context
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.portal = self.portal_state.portal()
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')

    @memoize_contextless
    def configs(self):
        adapter = LikeControlPanelAdapter(self.portal)
        return adapter

    @memoize_contextless
    def enabled_portal_types(self):
        configs = self.configs()
        return configs.enabled_portal_types

    @memoize_contextless
    def plugins_enabled(self):
        configs = self.configs()
        return configs.plugins_enabled or []

    @memoize_contextless
    def typebutton(self):
        configs = self.configs()
        return configs.typebutton

    @memoize
    def enabled(self):
        enabled_portal_types = self.enabled_portal_types()
        return self.context.portal_type in enabled_portal_types

    @memoize_contextless
    def available_plugins(self):
        registered = dict(getUtilitiesFor(IPlugin))
        return registered

    @memoize_contextless
    def plugins(self):
        available = self.available_plugins()
        enabled = self.plugins_enabled()
        plugins = []
        for plugin_id in enabled:
            plugin = available.get(plugin_id, None)
            if plugin:
                plugins.append(plugin)
        return plugins

    @memoize
    def view_template_id(self):
        return self.context_state.view_template_id()

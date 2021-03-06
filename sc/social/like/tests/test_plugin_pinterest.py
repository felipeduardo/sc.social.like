# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from sc.social.like.controlpanel.likes import LikeControlPanelAdapter
from sc.social.like.interfaces import ISocialLikeLayer
from sc.social.like.plugins.pinterest import browser
from sc.social.like.plugins.interfaces import IPlugin
from sc.social.like.testing import INTEGRATION_TESTING
from sc.social.like.testing import generate_image
from zope.component import getUtilitiesFor
from zope.interface import alsoProvides

import unittest2 as unittest

name = 'Pinterest'


class PluginTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        alsoProvides(self.portal.REQUEST, ISocialLikeLayer)
        self.plugins = dict(getUtilitiesFor(IPlugin))

    def test_plugin_available(self):
        self.assertTrue(name in self.plugins)

    def test_plugin_config(self):
        plugin = self.plugins[name]
        self.assertEqual(plugin.name, name)
        self.assertEqual(plugin.id, 'pinterest')

    def test_plugin_config_view(self):
        plugin = self.plugins[name]
        self.assertEqual(plugin.config_view(),
                         None)

    def test_plugin_view(self):
        plugin = self.plugins[name]
        self.assertEqual(plugin.view(),
                         '@@pinterest-plugin')

    def test_plugin_metadata(self):
        plugin = self.plugins[name]
        self.assertEqual(plugin.metadata(),
                         None)

    def test_plugin_plugin(self):
        plugin = self.plugins[name]
        self.assertEqual(plugin.plugin(),
                         'plugin')


class PluginViewsTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.adapter = LikeControlPanelAdapter(self.portal)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.setup_content(self.portal)
        alsoProvides(self.portal.REQUEST, ISocialLikeLayer)
        self.plugins = dict(getUtilitiesFor(IPlugin))
        self.plugin = self.plugins[name]

    def setup_content(self, portal):
        portal.invokeFactory('News Item', 'my-newsitem')
        portal.invokeFactory('Image', 'my-image')
        self.newsitem = portal['my-newsitem']
        self.newsitem.setImage(generate_image(1024, 768))
        self.image = portal['my-image']
        self.image.setImage(generate_image(1024, 768))

    def image_url(self, obj, field='image', scale='large'):

        view = obj.unrestrictedTraverse('@@images')
        scale = view.scale(fieldname='image', scale='large')
        return scale.url

    def test_plugin_view(self):
        plugin = self.plugin
        portal = self.portal
        plugin_view = plugin.view()
        view = portal.restrictedTraverse(plugin_view)
        self.assertTrue(isinstance(view, browser.PluginView))

    def test_plugin_view_html(self):
        plugin = self.plugin
        newsitem = self.newsitem
        plugin_view = plugin.view()
        view = newsitem.restrictedTraverse(plugin_view)
        html = view.plugin()
        self.assertTrue('js/pinit.js' in html)
        self.assertTrue('pin_it_button.png' in html)

    def test_plugin_view_image(self):
        plugin = self.plugin
        image = self.image
        expected = self.image_url(image)

        plugin_view = plugin.view()
        view = image.restrictedTraverse(plugin_view)

        # At image, use local image
        image_url = view.image_url()
        self.assertEqual(expected, image_url)

    def test_plugin_view_newsitem(self):
        plugin = self.plugin
        newsitem = self.newsitem
        expected = self.image_url(newsitem)

        plugin_view = plugin.view()
        view = newsitem.restrictedTraverse(plugin_view)

        # At newsitem, use image
        image_url = view.image_url()
        self.assertEqual(expected, image_url)

    def test_plugin_view_document(self):
        plugin = self.plugin
        self.portal.invokeFactory('Document', 'my-document')
        document = self.portal['my-document']
        expected = 'logo.png'

        plugin_view = plugin.view()
        view = document.restrictedTraverse(plugin_view)

        # At document, return logo
        image_url = view.image_url()
        self.assertTrue(expected in image_url)

    def test_plugin_view_typebutton(self):
        portal = self.portal
        plugin = self.plugin

        plugin_view = plugin.view()
        view = portal.restrictedTraverse(plugin_view)
        self.assertEqual(view.typebutton, 'beside')

        # Change to vertical
        adapter = self.adapter
        adapter.typebutton = 'vertical'
        view = portal.restrictedTraverse(plugin_view)
        self.assertEqual(view.typebutton, 'above')

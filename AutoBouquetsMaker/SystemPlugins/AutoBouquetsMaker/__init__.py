# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ, path
import gettext

PluginLanguageDomain = "AutoBouquetsMaker"

def localeInit():
    lang = language.getLanguage()[:2]
    environ["LANGUAGE"] = lang
    PluginLanguagePath = resolveFilename(SCOPE_LANGUAGE, '') #%s/LC_MESSAGES/' % lang)
    #print '%s%s/LC_MESSAGES/%s.mo' % (PluginLanguagePath,lang,PluginLanguageDomain)
    if not path.exists( '%s%s/LC_MESSAGES/%s.mo' % (PluginLanguagePath,lang,PluginLanguageDomain)):
        PluginLanguagePath = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/AutoBouquetsMaker/locale")

    print "[AutoBouquetsMaker] PluginLanguagePath:" + PluginLanguagePath
    gettext.bindtextdomain(PluginLanguageDomain, PluginLanguagePath)

def _(txt):
    if gettext.dgettext(PluginLanguageDomain, txt):
        return gettext.dgettext(PluginLanguageDomain, txt)
    else:
        print "[" + PluginLanguageDomain + "] fallback to default translation for " + txt
        return gettext.gettext(txt)

language.addCallback(localeInit())

'''
Created on April 15, 2015

@author: Haithem SOUALA
'''
from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from recipes.models import Category, Unit

admin.site.register(Unit)
admin.site.register(Category,MPTTModelAdmin)
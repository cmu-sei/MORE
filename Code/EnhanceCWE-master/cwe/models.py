# @OPENSOURCE_HEADER_START@
# MORE Tool 
# Copyright 2016 Carnegie Mellon University.
# All Rights Reserved.
#
# THIS SOFTWARE IS PROVIDED "AS IS," WITH NO WARRANTIES WHATSOEVER.
# CARNEGIE MELLON UNIVERSITY EXPRESSLY DISCLAIMS TO THE FULLEST EXTENT
# PERMITTEDBY LAW ALL EXPRESS, IMPLIED, AND STATUTORY WARRANTIES,
# INCLUDING, WITHOUT LIMITATION, THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF PROPRIETARY
# RIGHTS.
#
# Released under a modified BSD license, please see license.txt for full
# terms. DM-0003473
# @OPENSOURCE_HEADER_END@
from django.db import models
from django.contrib.auth.models import User
from django.db import IntegrityError
from base.models import BaseModel
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from cwe_search import CWESearchLocator

class Category(BaseModel):
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        # override default permissions to add 'view' permission that give readonly access rights
        default_permissions = ('add', 'change', 'delete', 'view')

    def __unicode__(self):
        return self.name


@receiver(pre_delete, sender=Category, dispatch_uid='category_delete_signal')
def pre_delete_category(sender, instance, using, **kwargs):
    """
    Prevent Category deletion if CWEs are referring to it
    """
    if instance.cwes.exists():
        raise IntegrityError(
            _('The %(name)s "%(obj)s" cannot be deleted as there are CWEs referring to it!') % {
                'name': force_text(instance._meta.verbose_name),
                'obj': force_text(instance.__unicode__()),
            })


class Keyword(BaseModel):
    name = models.CharField(max_length=32, unique=True)

    class Meta:
        verbose_name = "Keyword"
        verbose_name_plural = "Keywords"

    def __unicode__(self):
        return self.name

@receiver(pre_save, sender=Keyword, dispatch_uid='keyword_pre_save_signal')
def pre_save_keyword(sender, instance, *args, **kwargs):
    """ Change the keyword name to a stemmed format """
    if isinstance(instance.name, basestring):
        cwe_search = CWESearchLocator.get_instance()
        stemmed_name = cwe_search.stem_text([instance.name.lower()])
        if stemmed_name:
            # stem_text() returns a list, so we are reading the first element
            stemmed_name = stemmed_name[0]

            # raise an error if the stemmed name already exist in the database
            if Keyword.objects.filter(name__exact=stemmed_name).exists():
                raise IntegrityError("Keyword stemmed name (%s) already exist!" % stemmed_name)
            else:
                instance.name = stemmed_name

class CWE(BaseModel):
    code = models.IntegerField(unique=True)
    name = models.CharField(max_length=128, db_index=True)
    description = models.TextField(null=True, blank=True)
    categories = models.ManyToManyField(Category, related_name='cwes')
    keywords = models.ManyToManyField(Keyword, related_name='cwes', blank=True)

    class Meta:
        verbose_name = "CWE"
        verbose_name_plural = "CWEs"
        # override default permissions to add 'view' permission that give readonly access rights
        default_permissions = ('add', 'change', 'delete', 'view')

    def __unicode__(self):
        return "CWE-%s: %s" % (self.code, self.name)

@receiver(pre_delete, sender=CWE, dispatch_uid='cwe_delete_signal')
def pre_delete_cwe(sender, instance, using, **kwargs):
    """
    Prevent CWE deletion if misuse cases are referring to it
    """
    if instance.misuse_cases.exists():
        raise IntegrityError(
            _('The %(name)s "%(obj)s" cannot be deleted as there are misuse cases referring to it!') % {
                'name': force_text(instance._meta.verbose_name),
                'obj': force_text(instance.__unicode__()),
            })

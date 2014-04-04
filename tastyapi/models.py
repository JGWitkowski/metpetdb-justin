#from migration_test
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals
import uuid

from django.db.models import Model, BigIntegerField, CharField, DateTimeField, FloatField, ForeignKey, IntegerField,ManyToManyField, SmallIntegerField, TextField, AutoField, OneToOneField
from django.db.models import BooleanField, PositiveIntegerField
from django.db.models import Field
from django.db.models import Q
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.gis.db.models import GeoManager, PolygonField, PointField, GeometryField
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.db import models as DjangoModels
from tastypie.models import ApiKey
from django.contrib.gis.db import models

from . import utils

# from tastypie.models import create_api_key

PUBLIC_GROUP_DEFAULT_NAME = 'public_group'

USER_GROUP_DEFAULT_PREFIX = 'user_group_'

class GroupExtra(Model):
    group = OneToOneField(Group)
    group_type = CharField(max_length=10, choices=(('public', 'public'),
                                                          ('u_uid', 'user'),
                                                          ('p_pid', 'project')))
    owner = ForeignKey(AuthUser, blank=True, null=True)


class GroupAccess(Model):
    group = ForeignKey(Group)
    read_access = BooleanField()
    write_access = BooleanField()
    content_type = ForeignKey(ContentType)
    object_id = PositiveIntegerField()
    accessible_object = generic.GenericForeignKey('content_type', 'object_id')
    class Meta:
        unique_together = ('group', 'content_type', 'object_id')
        get_latest_by = 'id'


def get_public_groups():
    """Get or create the public group(s) as a queryset."""
    public_groups = Group.objects.filter(groupextra__group_type='public')
    if not public_groups.exists():
        # None exist, create a new one
        new_public = Group.objects.create(name=PUBLIC_GROUP_DEFAULT_NAME)
        GroupExtra(group=new_public, group_type='public').save()
    return public_groups

# import the logging library
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

# Called after a User instance is saved:
@receiver(post_save, sender=AuthUser)
def fix_user_groups(sender, instance, created, raw, **kwargs):
    logger.error("hi")
    # if created:
    #     print "hi"
    #     ApiKey.objects.create(user=instance)
    # else
    #     print "bye"
    """Ensure that the user has their own group and is in the public group(s)."""
    return # TODO: Make this send email instead of fixing groups immediately
    if raw:
        # DB is in an inconsistent state; abort
        return
    if not created:
        return

    # Verify there is precisely one uid group for this user.


@receiver(pre_save)
def fix_public(sender, instance, raw, **kwargs):
    """Make public objects publicly accessible and private objects not."""
    if raw:
        # DB is in an inconsistent state; abort
        return
    if not hasattr(sender, 'public_data'):
        # We don't need to fix this one; abort
        return
    try:
        if sender.select_for_update().get(instance).public_data == instance.public_data:
            # Did not change, abort
            return
    except sender.DoesNotExist:
        pass
    sender_type = ContentType.objects.get_for_model(sender)
    public_groups = get_public_groups()
    query = Q(groupaccess__object_id=instance.pk,
              groupaccess__content_type=sender_type)
    groups_with_item = public_groups.filter(query)
    groups_without_item = public_groups.exclude(groups_with_item)
    if instance.public_data == 'Y':
        for group in groups_without_item.select_for_update():
            group.groupaccess.create(read_access=True, write_access=False,
                                     content_type=sender_type,
                                     object_id=instance.pk)
    else:
        for group in groups_with_item.select_for_update():
            group.groupaccess.delete(content_type=sender_type,
                                     object_id=instance.pk)

@receiver(post_save)
def create_group_access(sender, instance, created, **kwargs):
    if sender in [Sample, Subsample]:
        ctype = ContentType.objects.get_for_model(instance)
        group_id = instance.user.django_user.groups.filter(
                      name__endswith=instance.user.django_user.username)[0].id

        # Create a group access only if one doesn't already exists.
        # This will be true when we are updating an existing sample.
        try:
            group_access = GroupAccess.objects.get(group_id=group_id,
                                                   content_type = ctype,
                                                   object_id=instance.sample_id,
                                                   )
        except GroupAccess.DoesNotExist:
            GroupAccess.objects.create(
                id = utils.get_next_id(GroupAccess),
                group_id = group_id,
                read_access = True,
                write_access = True,
                content_type = ctype,
                object_id = instance.sample_id)


class BinaryField(Field):
    description = 'A sequence of bytes'
    def db_type(self, connection):
        return 'bytea'
    def get_prep_value(self, value):
        return bytearray(value)
    def get_prep_lookup(self, lookup_type, value):
        if lookup_type in ['iexact', 'icontains', 'istartswith', 'iendswith',
                           'year', 'month', 'day', 'week_day', 'hour', 'minute',
                           'second', 'iregex']:
            raise TypeError('%r is not a supported lookup type.' % lookup_type)
        else:
            return super(Field, self).get_prep_lookup(lookup_type, value)

PUBLIC_DATA_CHOICES = (('Y', 'Yes'),('N', 'No'))


# class GeometryColumn(models.Model):
#     f_table_catalog = models.CharField(max_length=256)
#     f_table_schema = models.CharField(max_length=256)
#     f_table_name = models.CharField(max_length=256)
#     f_geometry_column = models.CharField(max_length=256)
#     coord_dimension = models.IntegerField()
#     srid = models.IntegerField()
#     type = models.CharField(max_length=30)
#     id = models.IntegerField(primary_key=True)
#     class Meta:
#         db_table = 'geometry_columns'


class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    version = models.IntegerField()
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=255, unique=True)
    password = models.TextField() # This field type is a guess.
    address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=50, blank=True)
    province = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=15, blank=True)
    institution = models.CharField(max_length=300, blank=True)
    reference_email = models.CharField(max_length=255, blank=True)
    confirmation_code = models.CharField(max_length=32, blank=True)
    enabled = models.CharField(max_length=1)
    role_id = models.SmallIntegerField(null=True, blank=True)
    contributor_code = models.CharField(max_length=32, blank=True)
    contributor_enabled = models.CharField(max_length=1, blank=True)
    professional_url = models.CharField(max_length=255, blank=True)
    research_interests = models.CharField(max_length=1024, blank=True)
    request_contributor = models.CharField(max_length=1, blank=True)
    django_user = OneToOneField(AuthUser, blank=True, null=True)

    def manual_verify(self):
        """Called to request full verification.

        Adds the user to a personal group so they may upload and share data.
        """
        if self.django_user is None:
            raise ValueError("This user doesn't exist in django.contrib.auth yet.")
        user_groups = Group.objects.filter(groupextra__group_type='u_uid',
                                           groupextra__owner=self.django_user)
        user_groups = user_groups.select_for_update()
        if user_groups.count() != 1:
            # There isn't, so get rid of whichever do exist and create from scratch
            user_groups.delete()
            user_group_name = USER_GROUP_DEFAULT_PREFIX + self.django_user.username
            user_group = Group.objects.create(name=user_group_name)
            user_group.user_set.add(self.django_user)
            GroupExtra(group=user_group, group_type='u_uid', owner=self.django_user).save()

        # also add to public groups so they may read public data
        # if self.django_user is None:
        #         raise ValueError("This user doesn't exist in django.contrib.auth yet.")
        public_groups = get_public_groups()
        for group in public_groups.select_for_update():
            if group not in self.django_user.groups.all():
                self.django_user.groups.add(group)

    class Meta:
        db_table = 'users'


class UsersRole(models.Model): #needs primary ID?
    user_id = models.IntegerField()
    role_id = models.SmallIntegerField()
    class Meta:
        db_table = 'users_roles'

class ImageType(models.Model):
    image_type_id = models.SmallIntegerField(primary_key=True)
    image_type = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=10, unique=True, blank=True)
    comments = models.CharField(max_length=250, blank=True)
    class Meta:
        db_table = 'image_type'


class Georeference(models.Model):
    georef_id = models.BigIntegerField(primary_key=True)
    title = models.TextField()
    first_author = models.TextField()
    second_authors = models.TextField(blank=True)
    journal_name = models.TextField()
    full_text = models.TextField()
    reference_number = models.TextField(blank=True)
    reference_id = models.BigIntegerField(null=True, blank=True)
    journal_name_2 = models.TextField(blank=True)
    doi = models.TextField(blank=True)
    publication_year = models.TextField(blank=True)
    class Meta:
        db_table = 'georeference'


class ImageFormat(models.Model):
    image_format_id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    class Meta:
        db_table = 'image_format'


class MetamorphicGrade(models.Model):
    metamorphic_grade_id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    def __unicode__(self):
        return self.name
    class Meta:
        # managed = False
        db_table = u'metamorphic_grades'

class MetamorphicRegion(models.Model):
    metamorphic_region_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    shape = models.PolygonField(null=True, blank=True)
    description = models.TextField(blank=True)
    label_location = models.PointField(null=True, blank=True)
    objects = models.GeoManager()
    def __unicode__(self):
        return self.name
    class Meta:
        # managed = False
        db_table = u'metamorphic_regions'

class MineralType(models.Model):
    mineral_type_id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    class Meta:
        db_table = 'mineral_types'


class Mineral(models.Model):
    mineral_id = models.SmallIntegerField(primary_key=True)
    real_mineral = models.ForeignKey('self')
    name = models.CharField(max_length=100, unique=True)
    def __unicode__(self):
        return self.name
    class Meta:
        # managed = False
        db_table = u'minerals'


class Reference(models.Model):
    reference_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    def __unicode__(self):
        return self.name
    class Meta:
        # managed = False
        db_table = u'reference'

class Region(models.Model):
    region_id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    def __unicode__(self):
        return self.name
    class Meta:
        # managed = False
        db_table = u'regions'
        get_latest_by = "region_id"

class RockType(models.Model):
    rock_type_id = models.SmallIntegerField(primary_key=True)
    rock_type = models.CharField(max_length=100, unique=True)
    def __unicode__(self):
        return self.rock_type
    class Meta:
        # managed = False
        db_table = u'rock_type'

class Role(models.Model):
    role_id = models.SmallIntegerField(primary_key=True)
    role_name = models.CharField(max_length=50)
    rank = models.SmallIntegerField(null=True, blank=True)
    class Meta:
        db_table = 'roles'


class SpatialRefSys(models.Model):
    srid = models.IntegerField(primary_key=True)
    auth_name = models.CharField(max_length=256, blank=True)
    auth_srid = models.IntegerField(null=True, blank=True)
    srtext = models.CharField(max_length=2048, blank=True)
    proj4text = models.CharField(max_length=2048, blank=True)
    class Meta:
        db_table = 'spatial_ref_sys'

class SubsampleType(models.Model):
    subsample_type_id = models.SmallIntegerField(primary_key=True)
    subsample_type = models.CharField(max_length=100, unique=True)
    class Meta:
        db_table = 'subsample_type'


class AdminUser(models.Model):
    admin_id = models.IntegerField(primary_key=True)
    user = models.ForeignKey('User')
    class Meta:
        db_table = 'admin_users'

class Element(models.Model):
    element_id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    alternate_name = models.CharField(max_length=100, blank=True)
    symbol = models.CharField(max_length=4, unique=True)
    atomic_number = models.IntegerField()
    weight = models.FloatField(null=True, blank=True)
    order_id = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'elements'


class ElementMineralType(models.Model):
    element = models.ForeignKey(Element)
    mineral_type = models.ForeignKey(MineralType)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = 'element_mineral_types'


class ImageReference(models.Model):
    image = models.ForeignKey('Image')
    reference = models.ForeignKey('Reference')
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = 'image_reference'


class Oxide(models.Model):
    oxide_id = models.SmallIntegerField(primary_key=True)
    element = models.ForeignKey(Element)
    oxidation_state = models.SmallIntegerField(null=True, blank=True)
    species = models.CharField(max_length=20, unique=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    cations_per_oxide = models.SmallIntegerField(null=True, blank=True)
    conversion_factor = models.FloatField()
    order_id = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'oxides'


class OxideMineralType(models.Model):
    oxide = models.ForeignKey('Oxide')
    mineral_type = models.ForeignKey(MineralType)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = 'oxide_mineral_types'

class Project(models.Model):
    project_id = models.IntegerField(primary_key=True)
    version = models.IntegerField()
    user = models.ForeignKey('User')
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300, blank=True)
    isactive = models.CharField(max_length=1, blank=True)
    class Meta:
        db_table = 'projects'


# Update:
    # deal with public data change
    # from public to not public if public_data set to N and vice versa

class Sample(models.Model):
    sample_id = models.BigIntegerField(primary_key=True)
    version = models.IntegerField()
    sesar_number = models.CharField(max_length=9, blank=True)
    public_data = models.CharField(max_length=1)
    collection_date = models.DateTimeField(null=True, blank=True)
    date_precision = models.SmallIntegerField(null=True, blank=True)
    number = models.CharField(max_length=35)
    rock_type = models.ForeignKey(RockType)
    user = models.ForeignKey('User', related_name='+')
    location_error = models.FloatField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    collector_name = models.CharField(max_length=50, blank=True)
    collector = models.ForeignKey('User', related_name='+', null=True,
                                  db_column='collector_id', blank=True)
    location_text = models.CharField(max_length=50, blank=True)
    location = models.PointField()
    objects = models.GeoManager()
    metamorphic_grades = ManyToManyField(MetamorphicGrade,
                                         through='SampleMetamorphicGrade')
    metamorphic_regions = ManyToManyField(MetamorphicRegion,
                                          through='SampleMetamorphicRegion')
    minerals = ManyToManyField(Mineral, through='SampleMineral')
    references = ManyToManyField(Reference, through='SampleReference')
    regions = ManyToManyField(Region, through='SampleRegion')
    group_access = generic.GenericRelation(GroupAccess)

    def __unicode__(self):
        return u'Sample #' + unicode(self.sample_id)
    class Meta:
        # managed = False
        db_table = u'samples'
        get_latest_by = "sample_id"
        permissions = (('read_sample', 'Can read sample'),)
                        # 'create_sample', 'Can create sample',)
    def save(self, **kwargs):
        # Assign a sample ID only for create requests
        self.sample_id = self.sample_id or utils.get_next_id(Sample)
        super(Sample, self).save()


@receiver(post_save, sender=Sample)
def create_sample_group_access(sender, instance, created, **kwargs):
    ctype = ContentType.objects.get_for_model(instance)
    group_id = instance.user.django_user.groups.filter(
                    name__iendswith=instance.user.django_user.username)[0].id
    try: id = GroupAccess.objects.latest('id').id + 1
    except GroupAccess.DoesNotExist: id = 1

    # Create a group access only if one doesn't already exists.
    # This will be true when we are updating an existing sample.
    try:
        group_access = GroupAccess.objects.get(group_id = group_id,
                                               content_type = ctype,
                                               object_id = instance.sample_id)
    except GroupAccess.DoesNotExist:
        GroupAccess.objects.create(
            id = id,
            group_id = group_id,
            read_access = True,
            write_access = True,
            content_type = ctype,
            object_id = instance.sample_id)

class SampleMetamorphicGrade(models.Model):
    sample = models.ForeignKey('Sample')
    metamorphic_grade = models.ForeignKey(MetamorphicGrade)
    id = models.IntegerField(primary_key=True)
    class Meta:
        # managed = False
        unique_together = (('sample', 'metamorphic_grade'),)
        db_table = u'sample_metamorphic_grades'
        get_latest_by = 'id'

class SampleMetamorphicRegion(models.Model):
    sample = models.ForeignKey('Sample')
    metamorphic_region = models.ForeignKey(MetamorphicRegion)
    id = models.IntegerField(primary_key=True)
    class Meta:
        # managed = False
        unique_together = (('sample', 'metamorphic_region'),)
        db_table = u'sample_metamorphic_regions'
        get_latest_by = 'id'

class SampleMineral(models.Model):
    mineral = models.ForeignKey(Mineral)
    sample = models.ForeignKey('Sample')
    amount = models.CharField(max_length=30, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        # managed = False
        unique_together = (('mineral', 'sample'),)
        db_table = u'sample_minerals'
        get_latest_by = 'id'

class SampleReference(models.Model):
    sample = models.ForeignKey('Sample')
    reference = models.ForeignKey(Reference)
    id = models.IntegerField(primary_key=True)
    class Meta:
        # managed = False
        unique_together = (('sample', 'reference'),)
        db_table = u'sample_reference'
        get_latest_by = 'id'


class SampleRegion(models.Model):
    sample = models.ForeignKey('Sample')
    region = models.ForeignKey(Region)
    id = models.IntegerField(primary_key=True)
    class Meta:
        # managed = False
        unique_together = (('sample', 'region'),)
        db_table = u'sample_regions'
        get_latest_by = 'id'

class SampleAliase(models.Model):
    sample_alias_id = models.BigIntegerField(primary_key=True)
    sample = models.ForeignKey('Sample', null=True, blank=True)
    alias = models.CharField(max_length=35)
    def __unicode__(self):
        return self.alias
    class Meta:
        # managed = False
        db_table = u'sample_aliases'
        unique_together = (('sample', 'alias'),)


class Subsample(models.Model):
    subsample_id = models.BigIntegerField(primary_key=True)
    version = models.IntegerField()
    public_data = models.CharField(max_length=1)
    sample = models.ForeignKey(Sample)
    user = models.ForeignKey('User')
    grid_id = models.BigIntegerField(null=True, blank=True)
    name = models.CharField(max_length=100)
    subsample_type = models.ForeignKey(SubsampleType)
    group_access = generic.GenericRelation(GroupAccess)
    class Meta:
        db_table = u'subsamples'
        # managed = False
        permissions = (('read_subsample', 'Can read subsample'),)
    def save(self, **kwargs):
        # Assign a sample ID only for create requests
        if self.subsample_id is None:
            try: id = Subsample.objects.latest('subsample_id').subsample_id + 1
            except Subsample.DoesNotExist: id = 1
            self.subsample_id = id
        subsample = super(Subsample, self).save()

@receiver(post_save, sender=Subsample)
def create_subsample_group_access(sender, instance, created, **kwargs):

    ctype = ContentType.objects.get_for_model(instance)
    group_id = instance.user.django_user.groups.filter(
                    name__endswith=instance.user.django_user.username)[0].id
    logger.error("sender: {}, instance: {}, created: {}, kwargs: {}".format(sender, instance, created, kwargs))
    try: id = GroupAccess.objects.latest('id').id + 1
    except GroupAccess.DoesNotExist: id = 1

    # Create a group access only if one doesn't already exists.
    # This will be true when we are updating an existing sample.

    try:
        group_access = GroupAccess.objects.get(group_id = group_id,
                                               content_type = ctype,
                                               object_id = instance.subsample_id)
    except GroupAccess.DoesNotExist:
        GroupAccess.objects.create(
            id = id,
            group_id = group_id,
            read_access = True,
            write_access = True,
            content_type = ctype,
            object_id = instance.subsample_id)

class Grid(models.Model):
    grid_id = models.BigIntegerField(primary_key=True)
    version = models.IntegerField()
    subsample = models.ForeignKey('Subsample')
    width = models.SmallIntegerField()
    height = models.SmallIntegerField()
    public_data = models.CharField(max_length=1)
    class Meta:
        db_table = 'grids'


class ChemicalAnalyses(models.Model):
    chemical_analysis_id = models.BigIntegerField(primary_key=True)
    version = models.IntegerField()
    subsample = models.ForeignKey('Subsample')
    public_data = models.CharField(max_length=1)
    reference_x = models.FloatField(null=True, blank=True)
    reference_y = models.FloatField(null=True, blank=True)
    stage_x = models.FloatField(null=True, blank=True)
    stage_y = models.FloatField(null=True, blank=True)
    image = models.ForeignKey('Image', null=True, blank=True)
    analysis_method = models.CharField(max_length=50, blank=True)
    where_done = models.CharField(max_length=50, blank=True)
    analyst = models.CharField(max_length=50, blank=True)
    analysis_date = models.DateTimeField(null=True, blank=True)
    date_precision = models.SmallIntegerField(null=True, blank=True)
    reference = models.ForeignKey('Reference', null=True, blank=True)
    description = models.CharField(max_length=1024, blank=True)
    mineral = models.ForeignKey('Mineral', null=True, blank=True)
    user = models.ForeignKey('User')
    large_rock = models.CharField(max_length=1)
    total = models.FloatField(null=True, blank=True)
    spot_id = models.BigIntegerField()
    class Meta:
        db_table = 'chemical_analyses'

class ChemicalAnalysisElement(models.Model):
    chemical_analysis = models.ForeignKey(ChemicalAnalyses)
    element = models.ForeignKey('Element')
    amount = models.FloatField()
    precision = models.FloatField(null=True, blank=True)
    precision_type = models.CharField(max_length=3, blank=True)
    measurement_unit = models.CharField(max_length=4, blank=True)
    min_amount = models.FloatField(null=True, blank=True)
    max_amount = models.FloatField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = 'chemical_analysis_elements'

class ChemicalAnalysisOxide(models.Model):
    chemical_analysis = models.ForeignKey(ChemicalAnalyses)
    oxide = models.ForeignKey('Oxide')
    amount = models.FloatField()
    precision = models.FloatField(null=True, blank=True)
    precision_type = models.CharField(max_length=3, blank=True)
    measurement_unit = models.CharField(max_length=4, blank=True)
    min_amount = models.FloatField(null=True, blank=True)
    max_amount = models.FloatField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = 'chemical_analysis_oxides'


class Image(models.Model):
    image_id = models.BigIntegerField(primary_key=True)
    checksum = models.CharField(max_length=50)
    version = models.IntegerField()
    sample = models.ForeignKey('Sample', null=True, blank=True)
    subsample = models.ForeignKey('Subsample', null=True, blank=True)
    image_format = models.ForeignKey(ImageFormat, null=True, blank=True)
    image_type = models.ForeignKey(ImageType)
    width = models.SmallIntegerField()
    height = models.SmallIntegerField()
    collector = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=1024, blank=True)
    scale = models.SmallIntegerField(null=True, blank=True)
    user = models.ForeignKey('User')
    public_data = models.CharField(max_length=1)
    group_access = generic.GenericRelation(GroupAccess)
    checksum_64x64 = models.CharField(max_length=50)
    checksum_half = models.CharField(max_length=50)
    filename = models.CharField(max_length=256)
    checksum_mobile = models.CharField(max_length=50, blank=True)
    class Meta:
        # managed = False
        db_table = u'images'
        permissions = (('read_image', 'Can read image'),)



class ImageComment(models.Model):
    comment_id = models.BigIntegerField(primary_key=True)
    image = models.ForeignKey('Image')
    comment_text = models.TextField()
    version = models.IntegerField()
    class Meta:
        db_table = 'image_comments'


class ImageOnGrid(models.Model):
    image_on_grid_id = models.BigIntegerField(primary_key=True)
    grid = models.ForeignKey(Grid)
    image = models.ForeignKey('Image')
    top_left_x = models.FloatField()
    top_left_y = models.FloatField()
    z_order = models.SmallIntegerField()
    opacity = models.SmallIntegerField()
    resize_ratio = models.FloatField()
    width = models.SmallIntegerField()
    height = models.SmallIntegerField()
    checksum = models.CharField(max_length=50)
    checksum_64x64 = models.CharField(max_length=50)
    checksum_half = models.CharField(max_length=50)
    locked = models.CharField(max_length=1)
    angle = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = 'image_on_grid'



class ProjectInvite(models.Model):
    invite_id = models.IntegerField(primary_key=True)
    project = models.ForeignKey('Project')
    user = models.ForeignKey('User')
    action_timestamp = models.DateTimeField()
    status = models.CharField(max_length=32, blank=True)
    class Meta:
        db_table = 'project_invites'

class ProjectMember(models.Model):
    project = models.ForeignKey('Project')
    user = models.ForeignKey('User')
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = 'project_members'

class ProjectSample(models.Model):
    project = models.ForeignKey('Project')
    sample = models.ForeignKey('Sample')
    id = models.IntegerField(primary_key=True)
    class Meta:
        db_table = 'project_samples'


class SampleComment(models.Model):
    comment_id = models.BigIntegerField(primary_key=True)
    sample = models.ForeignKey('Sample')
    user = models.ForeignKey('User')
    comment_text = models.TextField()
    date_added = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'sample_comments'


class UploadedFile(models.Model):
    uploaded_file_id = models.BigIntegerField(primary_key=True)
    hash = models.CharField(max_length=50)
    filename = models.CharField(max_length=255)
    time = models.DateTimeField()
    user = models.ForeignKey('User', null=True, blank=True)
    class Meta:
        db_table = 'uploaded_files'


class XrayImage(models.Model):
    image = models.ForeignKey(Image, primary_key=True)
    element = models.CharField(max_length=256, blank=True)
    dwelltime = models.SmallIntegerField(null=True, blank=True)
    current = models.SmallIntegerField(null=True, blank=True)
    voltage = models.SmallIntegerField(null=True, blank=True)
    class Meta:
        db_table = 'xray_image'

from django.contrib.contenttypes.models import ContentType
from tastyapi.models import Group, GroupExtra, GroupAccess
from tastyapi.models import User, Sample, Subsample, SubsampleType, \
                            RockType, ChemicalAnalyses, Region, SampleRegion,\
                            SampleReference, SampleMetamorphicGrade, \
                            SampleMineral, SampleMetamorphicRegion, \
                            GroupExtra, get_public_groups

from django.contrib.auth.models import User as AuthUser
from tastypie.test import ResourceTestCase
from tastypie.models import ApiKey
import nose.tools as nt
from .base_class import TestSetUp, client
import logging

client = TestApiClient()

valid_post_data = {
    'user': '/tastyapi/v1/user/1/',
    'sesar_number': '14342',
    'public_data': 'Y',
    'date_precision': '1',
    'number': 'NL-67:2005-06290',
    'rock_type': '/tastyapi/v1/rock_type/16/',
    'description': 'Created by a test case',
    'location_error': '2000',
    'country': 'Brazil',
    'location_text': 'amfadf',
    'location': 'POINT (-49.3400382995604971 -16.5187797546387003)'
}


class TestSetUp(ResourceTestCase):
    fixtures = ['auth_users.json', 'users.json']

    def setUp(self):
        super(TestSetUp, self).setUp()
        auth_user = AuthUser.objects.get(pk = 1)
        ApiKey.objects.create(user = auth_user)
        self.user = User.objects.get(pk = 1)
        self.user.manual_verify()

        auth_user = AuthUser.objects.get(pk = 2)
        ApiKey.objects.create(user = auth_user)
        user = User.objects.get(pk = 2)
        user.manual_verify()

        # A user who doesn't have their own personal group
        auth_user = AuthUser.objects.get(pk = 3)
        ApiKey.objects.create(user = auth_user)

    def get_credentials(self, user_id = 1):
        auth_user = AuthUser.objects.get(pk = user_id)
        return "ApiKey sibel:{0}".format(ApiKey.objects.get(user =
                                                            auth_user).key)

    def test_valid_registration_sibel(self):
        nt.assert_equal(len(self.user.django_user.groups.all()), 2)
        personal_group = self.user.django_user.groups.all()[0]
        public_group = self.user.django_user.groups.all()[1]
        public_groups = get_public_groups()
        nt.assert_equal("user_group_sibel", personal_group.name)
        nt.assert_in(public_group, public_groups)

class SubSampleReadResourceTest(TestSetUp):
    fixtures = ['auth_users.json', 'users.json', 'rock_types.json']
    def setUp(self):
        super(SubSampleReadResourceTest, self).setUp()
        #rock_type = RockType.objects.get(pk = 16)
        rock_type = RockType.objects.get(pk = 16)
        sam = Sample.objects.create(user = self.user,
                              version = 1,
                              sesar_number = 14342,
                              public_data = 'Y',
                              date_precision = '1',
                              number = 'NL-67:2005-06290',
                              rock_type = rock_type,
                              description = 'Created by a test case',
                              location_error = 2000,
                              country = 'Brazil',
                              location_text = 'anfdaf',
                              location = 'POINT(-49.3400382995604971 \
                                                -16.5187797546387003)')
        subsamtype = SubsampleType.objects.create(subsample_type_id = 1,
          subsample_type = "Test Subsample Type"
        )
        Subsample.objects.create(version = 1,
                                 public_data = 'Y',
                                 user = self.user,
                                 grid_id = 1,
                                 name = "Test Name for SubSample",
                                 subsample_type = subsamtype,
                                 sample = sam
        )
    # def test_finds_an_existing_SubSample(self):
    #     self.test_valid_registration_sibel()
    #     credentials = self.get_credentials()
    #     print(credentials)
    #     resp = client.get('/tastyapi/v1/subsample/1/',
    #                       authentication = credentials, format = 'json')
    #     self.assertHttpOK(resp)
    # '''    subsample_id = models.BigIntegerField(primary_key=True)
    # version = models.IntegerField()
    # public_data = models.CharField(max_length=1)
    # sample = models.ForeignKey(Sample)
    # user = models.ForeignKey('User')
    # grid_id = models.BigIntegerField(null=True, blank=True)
    # name = models.CharField(max_length=100)
    # subsample_type = models.ForeignKey(SubsampleType)'''

    def test_finds_an_existing_subsample(self):
        credentials = self.get_credentials()
        nt.assert_equal(Subsample.objects.all().count(), 1)
        print "SubSample"
        print Subsample.objects.get(pk=1)
        print "SubSample"
        resp = client.get('/tastyapi/v1/subsample/1/',
                          authentication = credentials, format = 'json')
        print resp
        self.assertHttpOK(resp)

    def test_does_not_find_a_non_existent_subsample(self):
        credentials = self.get_credentials()
        resp = client.get('/tastyapi/v1/subsample/1000/',
                          authentication = credentials, format = 'json')
        self.assertHttpNotFound(resp)

    def test_cannot_read_a_subsample_without_an_apikey(self):
        resp = client.get('/tastyapi/v1/subsample/1/', format = 'json')
        self.assertHttpUnauthorized(resp)

class SubSampleResourceCreateTest(TestSetUp):
    fixtures = ['auth_users.json', 'users.json', 'rock_types.json', 'subsample_types.json']
    def setUp(self):
        super(SubSampleResourceCreateTest, self).setUp()
        rock_type = RockType.objects.get(pk = 16)
        sam = Sample.objects.create(user = self.user,
                            version = 1,
                            sesar_number = 14342,
                            public_data = 'Y',
                            date_precision = '1',
                            number = 'NL-67:2005-06290',
                            rock_type = rock_type,
                            description = 'Created by a test case',
                            location_error = 2000,
                            country = 'Brazil',
                            location_text = 'anfdaf',
                            location = 'POINT(-49.3400382995604971 \
                                              -16.5187797546387003)')
    #subsamtype = SubsampleType.objects.create(subsample_type_id = 1,
    #      subsample_type = "Test Subsample Type")
    def test_authorized_user_can_create_a_subsample(self):
        nt.assert_equal(Subsample.objects.count(), 0)
        credentials = self.get_credentials()
        print credentials
        resp = client.post('/tastyapi/v1/subsample/', data = subsample_data,
                           authentication = credentials, format = 'json')
        self.assertHttpCreated(resp)
        nt.assert_equal(Sample.objects.count(), 1)

    def test_unauthorized_user_cannot_create_a_subsample(self):
        nt.assert_equal(Subsample.objects.count(), 0)
        credentials = self.get_credentials(user_id = 3)
        resp = client.post('/tastyapi/v1/subsample/', data = subsample_data,
                           authentication = credentials, format = 'json')
        self.assertHttpUnauthorized(resp)
        nt.assert_equal(Subsample.objects.count(), 0)

class SubsampleResourceUpdateDeleteTest(TestSetUp):
    fixtures = ['auth_users.json', 'users.json', 'rock_types.json', 'subsample_types.json']
    def setUp(self):
        super(SubsampleResourceUpdateDeleteTest, self).setUp()
        rock_type = RockType.objects.get(pk = 16)
        sam = Sample.objects.create(user = self.user,
                            version = 1,
                            sesar_number = 14342,
                            public_data = 'Y',
                            date_precision = '1',
                            number = 'NL-67:2005-06290',
                            rock_type = rock_type,
                            description = 'Created by a test case',
                            location_error = 2000,
                            country = 'Brazil',
                            location_text = 'anfdaf',
                            location = 'POINT(-49.3400382995604971 \
                                              -16.5187797546387003)')
        credentials = self.get_credentials()
        resp = client.post('/tastyapi/v1/subsample/', data = subsample_data,
                           authentication = credentials, format = 'json')
        self.assertHttpCreated(resp)

    def test_user_can_delete_own_Subsample(self):
        credentials = self.get_credentials()
        subsample = self.deserialize(client.get('/tastyapi/v1/subsample/1/',
                                  authentication = credentials, format='json'))
        nt.assert_equal(Subsample.objects.count(), 1)
        resp = client.delete('/tastyapi/v1/subsample/1/',
                             authentication = credentials, format = 'json')
        self.assertHttpAccepted(resp)
        nt.assert_equal(Subsample.objects.count(), 0)

    def test_user_cannot_delete_unowned_sample(self):
        credentials = self.get_credentials(user_id = 2)
        subsample = self.deserialize(client.get('/tastyapi/v1/subsample/1/',
                                  authentication = credentials, format='json'))
        nt.assert_equal(Subsample.objects.count(), 1)
        resp = client.delete('/tastyapi/v1/subsample/1/',
                             authentication = credentials, format = 'json')
        self.assertHttpUnauthorized(resp)
        nt.assert_equal(Subsample.objects.count(), 1)

    def test_user_can_update_own_subsample(self):
        credentials = self.get_credentials()
        nt.assert_equal(Subsample.objects.count(), 1)
        subsample = self.deserialize(client.get('/tastyapi/v1/subsample/1/',
                                  authentication = credentials, format='json'))
        nt.assert_equal("Subby", subsample['name'])
        subsample['name'] = "Subby Wilson"

        resp = client.put('/tastyapi/v1/subsample/1/', data=subsample,
                           authentication=credentials, format='json')

        self.assertHttpAccepted(resp)
        subsample = self.deserialize(client.get('/tastyapi/v1/subsample/1/',
                                  authentication = credentials, format='json'))
        nt.assert_equal("Subby Wilson", subsample['name'])
        nt.assert_equal(Subsample.objects.count(), 1)

    def test_user_cannot_update_unowned_subsample(self):
        credentials = self.get_credentials()
        subsample = self.deserialize(client.get('/tastyapi/v1/subsample/1/',
                                  authentication = credentials, format='json'))
        nt.assert_equal("Subby", subsample['name'])
        subsample['name'] = "Updated by a test case"

        credentials = self.get_credentials(user_id = 2)
        resp = client.put('/tastyapi/v1/sample/1/', data=subsample,
                           authentication=credentials, format='json')

        self.assertHttpUnauthorized(resp)
>>>>>>> Stashed changes:tastyapi/tests.py

class SampleResourceReadTest(TestSetUp):
    fixtures = ['auth_users.json', 'users.json', 'rock_types.json']
    def setUp(self):
        super(SampleResourceReadTest, self).setUp()
        rock_type = RockType.objects.get(pk = 16)
        Sample.objects.create(user = self.user,
                              version = 1,
                              sesar_number = 14342,
                              public_data = 'Y',
                              date_precision = '1',
                              number = 'NL-67:2005-06290',
                              rock_type = rock_type,
                              description = 'Created by a test case',
                              location_error = 2000,
                              country = 'Brazil',
                              location_text = 'anfdaf',
                              location = 'POINT(-49.3400382995604971 \
                                                -16.5187797546387003)')

    def test_finds_an_existing_sample(self):
        credentials = self.get_credentials()
        resp = client.get('/tastyapi/v1/sample/1/',
                          authentication = credentials, format = 'json')
        self.assertHttpOK(resp)

    def test_does_not_find_a_non_existent_sample(self):
        credentials = self.get_credentials()
        resp = client.get('/tastyapi/v1/sample/1000/',
                          authentication = credentials, format = 'json')
        self.assertHttpNotFound(resp)

    def test_cannot_read_a_sample_without_an_apikey(self):
        resp = client.get('/tastyapi/v1/sample/1/', format = 'json')
        self.assertHttpUnauthorized(resp)


class SampleResourceCreateTest(TestSetUp):
    fixtures = ['auth_users.json', 'users.json', 'regions.json',
                'references.json', 'metamorphic_grades.json', 'minerals.json',
                'rock_types.json', 'metamorphic_regions.json']

    def test_authorized_user_can_create_a_sample(self):
        nt.assert_equal(Sample.objects.count(), 0)
        credentials = self.get_credentials()

        valid_post_data = {
            'user': '/tastyapi/v1/user/1/',
            'sesar_number': '14342',
            'public_data': 'Y',
            'date_precision': '1',
            'number': 'NL-67:2005-06290',
            'rock_type': '/tastyapi/v1/rock_type/16/',
            'regions': ['Pune', 'Mumbai', 'Pune', 'Hyderabad'],
            'references': ['2004-061314',
                           '2004-065494',
                           '2004-065494'],
            'metamorphic_grades': ['/tastyapi/v1/metamorphic_grade/1/',
                                   '/tastyapi/v1/metamorphic_grade/2/',
                                   '/tastyapi/v1/metamorphic_grade/3/',
                                   '/tastyapi/v1/metamorphic_grade/4/'],
            'metamorphic_regions': ['/tastyapi/v1/metamorphic_region/427/',
                                   '/tastyapi/v1/metamorphic_region/428/',
                                   '/tastyapi/v1/metamorphic_region/429/',
                                   '/tastyapi/v1/metamorphic_region/430/'],
            'minerals': ['/tastyapi/v1/mineral/1/',
                         '/tastyapi/v1/mineral/2/',
                         '/tastyapi/v1/mineral/3/',
                         '/tastyapi/v1/mineral/4/'],
            'description': 'Created by a test case',
            'location_error': '2000',
            'country': 'Brazil',
            'location_text': 'amfadf',
            'location': 'POINT (-49.3400382995604971 -16.5187797546387003)'
          }

        resp = client.post('/tastyapi/v1/sample/', data = valid_post_data,
                           authentication = credentials, format = 'json')
        self.assertHttpCreated(resp)

        nt.assert_equal(Sample.objects.count(), 1)

        sample = Sample.objects.get(pk=1)
        nt.assert_equal(sample.metamorphic_regions.all().count(), 4)
        nt.assert_equal(SampleMetamorphicRegion.objects.count(), 4)

        nt.assert_equal(SampleMetamorphicGrade.objects.count(), 4)
        nt.assert_equal(sample.metamorphic_grades.all().count(), 4)

        nt.assert_equal(SampleReference.objects.count(), 2)
        nt.assert_equal(sample.references.all().count(), 2)

        nt.assert_equal(SampleMineral.objects.count(), 4)
        nt.assert_equal(sample.minerals.all().count(), 4)

        nt.assert_equal(SampleRegion.objects.count(), 3)
        nt.assert_equal(sample.regions.all().count(), 3)


    def test_unauthorized_user_cannot_create_a_sample(self):
        nt.assert_equal(Sample.objects.count(), 0)
        credentials = self.get_credentials(user_id = 3)
        resp = client.post('/tastyapi/v1/sample/', data = valid_post_data,
                           authentication = credentials, format = 'json')
        self.assertHttpUnauthorized(resp)
        nt.assert_equal(Sample.objects.count(), 0)


class SampleResourceUpdateDeleteTest(TestSetUp):
    fixtures = ['auth_users.json', 'users.json', 'rock_types.json']
    def setUp(self):
        super(SampleResourceUpdateDeleteTest, self).setUp()
        rock_type = RockType.objects.get(pk = 16)
        Sample.objects.create(user = self.user,
                              version = 1,
                              sesar_number = 14342,
                              public_data = 'Y',
                              date_precision = '1',
                              number = 'NL-67:2005-06290',
                              rock_type = rock_type,
                              description = 'Created by a test case',
                              location_error = 2000,
                              country = 'Brazil',
                              location_text = 'anfdaf',
                              location = 'POINT(-49.3400382995604971 \
                                                -16.5187797546387003)')

    def test_user_can_delete_own_sample(self):
        credentials = self.get_credentials()
        sample = self.deserialize(client.get('/tastyapi/v1/sample/1/',
                                  authentication = credentials, format='json'))
        nt.assert_equal(Sample.objects.count(), 1)
        resp = client.delete('/tastyapi/v1/sample/1/',
                             authentication = credentials, format = 'json')
        self.assertHttpAccepted(resp)
        nt.assert_equal(Sample.objects.count(), 0)

    def test_user_cannot_delete_unowned_sample(self):
        credentials = self.get_credentials(user_id = 2)
        sample = self.deserialize(client.get('/tastyapi/v1/sample/1/',
                                  authentication = credentials, format='json'))
        nt.assert_equal(Sample.objects.count(), 1)
        resp = client.delete('/tastyapi/v1/sample/1/',
                             authentication = credentials, format = 'json')
        self.assertHttpUnauthorized(resp)
        nt.assert_equal(Sample.objects.count(), 1)


    def test_user_can_update_own_sample(self):
        credentials = self.get_credentials()
        nt.assert_equal(Sample.objects.count(), 1)
        sample = self.deserialize(client.get('/tastyapi/v1/sample/1/',
                                  authentication = credentials, format='json'))
        nt.assert_equal("Created by a test case", sample['description'])
        sample['description'] = "Updated by a test case"

        resp = client.put('/tastyapi/v1/sample/1/', data=sample,
                           authentication=credentials, format='json')

        self.assertHttpAccepted(resp)
        sample = self.deserialize(client.get('/tastyapi/v1/sample/1/',
                                  authentication = credentials, format='json'))
        nt.assert_equal("Updated by a test case", sample['description'])
        nt.assert_equal(Sample.objects.count(), 1)


    def test_user_cannot_update_unowned_sample(self):
        credentials = self.get_credentials()
        sample = self.deserialize(client.get('/tastyapi/v1/sample/1/',
                                  authentication = credentials, format='json'))
        nt.assert_equal("Created by a test case", sample['description'])
        sample['description'] = "Updated by a test case"

        credentials = self.get_credentials(user_id = 2)
        resp = client.put('/tastyapi/v1/sample/1/', data=sample,
                           authentication=credentials, format='json')

        self.assertHttpUnauthorized(resp)


# class RegionReadTest(TestSetUp):
#     fixtures = ['auth_users.json', 'users.json', 'regions.json']
#     def setUp(self):
#         super(RegionReadTest, self).setUp()

#     def test_reads_an_existing_region(self):
#         credentials = self.get_credentials()
#         resp = client.get('/tastyapi/v1/region/1/',
#                           authentication = credentials, format = 'json')
#         self.assertHttpOK(resp)

# class RegionCreateTest(TestSetUp):
#     fixtures = ['auth_users.json', 'users.json']
#     def test_creates_a_region(self):
#         post_data = {
#                   'region_id': '1',
#                   'name': 'Mineral 1'
#         }

#         credentials = self.get_credentials()
#         resp = client.post('/tastyapi/v1/region/', data = post_data,
#                             authentication = credentials, format = 'json')
#         self.assertHttpCreated(resp)
#         nt.assert_equal(Region.objects.count(), 1)



# class RockTypeResourceTest(TestSetUp):

#     def test_finds_an_existing_rock_type(self):
#         credentials = self.get_credentials()
#         resp = client.get('/tastyapi/v1/rock_type/1/',
#                           authentication=credentials, format='json')
#         self.assertHttpOK(resp)

#     def test_does_not_find_a_non_existant_rock_type(self):
#         credentials = self.get_credentials()
#         resp = client.get('/tastyapi/v1/rock_type/100/',
#                           authentication=credentials, format='json')
#         self.assertHttpNotFound(resp)


# class SubSampleTypeResourceTest(TestSetUp):

#     def test_finds_an_existing_sub_sample(self):
#         credentials = self.get_credentials()
#         resp = client.get('/tastyapi/v1/subsample_type/4/',
#                           authentication=credentials, format='json')
#         self.assertHttpOK(resp)

#     def test_does_not_find_a_non_existant_subsample_type(self):
#         credentials = self.get_credentials()
#         resp = client.get('/tastyapi/v1/subsample_type/100/',
#                           authentication=credentials, format='json')
#         self.assertHttpNotFound(resp)

# class SubSampleResourceTest(TestSetUp):

#     def test_finds_an_existing_sub_sample(self):
#         credentials = self.get_credentials()
#         resp = client.get('/tastyapi/v1/subsample/4/',
#                           authentication=credentials, format='json')
#         self.assertHttpOK(resp)

#     def test_does_not_find_a_non_existant_subsample(self):
#         credentials = self.get_credentials()
#         resp = client.get('/tastyapi/v1/subsample/100/',
#                           authentication=credentials, format='json')
#         self.assertHttpNotFound(resp)





# class RegionResourceTest(TestSetUp):

#     def test_finds_an_existing_region(self):
#         credentials = self.get_credentials()
#         resp = client.get('/tastyapi/v1/region/1/',
#                           authentication=credentials, format='json')
#         self.assertHttpOK(resp)

#     def test_does_not_find_an_non_existant_region(self):
#         credentials = self.get_credentials()
#         resp = client.get('/tastyapi/v1/region/100/',
#                           authentication=credentials, format='json')
#         self.assertHttpNotFound(resp)

    # def test_read_sample(self):
    #     from clientlib.single import read_sample
    #     resp = read_sample(6336)
    #     self.assertValidJSONResponse(resp)


# class TestModels(object):

#     def setup(self):
#         self.users = {
#             "tej": User(),
#             "cow": User()
#         }
#         self.users["tej"].first_name = "Tej"
#         self.users["tej"].email_address = "fail@example.com"

#     def test_name(self):
#         nt.assert_equal(self.users["tej"].first_name, "Tej")

#     def test_valid_registration(self):
#         self.users["tej"].send_email()
#         nt.assert_equal(len(self.users["tej"].groups.all()), 0)
#         self.users["tej"].auto_verify(self.confirmation_code)

#         nt.assert_equal(len(self.users["tej"].django_user.groups.all()), 1)
#         tej_group = self.users["tej"].django_user.groups.all()[0]
#         public_groups = get_public_groups()
#         nt.assert_in(tej_group, public_groups)


#     def test_invalid_registration(self):
#         pass

#     def teardown(self):
#       pass

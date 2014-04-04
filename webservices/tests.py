# from django_nose import FastFixtureTestCase

# class UtilTest(FastFixtureTestCase):
#     def __init__(self, arg):
#         import webservices.util as util
#         self.CustomJSONEncoder = util.CustomJSONEncoder
#         self.dictfetchall = util.dictfetchall
#         self.dictfetchone = util.dictfetchone

#         super(UtilTest, self).__init__(arg)


#     # testing functions

#     def test_CustomJSONEncoder(self):
#         import json

#         expected_string = '[{"a": "QQQ"}, {"b": 777}, {"1": "ZZZ"}]'

#         data = [
#             {"a": "QQQ"},
#             {"b": 777},
#             {1: "ZZZ"}
#         ]

#         self.assertEquals(expected_string, json.dumps(data, cls=self.CustomJSONEncoder))
       
#     def test_CustomJSONEncoder_datetime(self):
#         import json
#         import datetime

#         expected_string = '"2010-12-25T00:00:00"'

#         data = datetime.datetime(2010, 12, 25)

#         self.assertEquals(expected_string, json.dumps(data, cls=self.CustomJSONEncoder))


#     def test_dictfetchall_regions_dne(self):
#         expected_regions = []

#         cursor = self._query_regions({"sample_id": -1})
#         self.assertEqual(cursor.rowcount, 0)

#         regions = self.dictfetchall(cursor)

#         self.assertEqual(expected_regions, regions)


#     def test_dictfetchall_regions_1(self):
#         expected_regions = [
#             {"name": "region1"},
#             {"name": "region2"},
#             {"name": "region3"}
#         ]

#         cursor = self._query_regions({"sample_id": 1})
#         self.assertEqual(cursor.rowcount, 3)

#         regions = self.dictfetchall(cursor)

#         self.assertEqual(expected_regions, regions)


#     def test_dictfetchone_regions_dne(self):
#         expected_region = {"error": "DNE"}

#         cursor = self._query_regions({"sample_id": -1})
#         self.assertEqual(cursor.rowcount, 0)

#         region = self.dictfetchone(cursor)

#         self.assertEqual(expected_region, region)


#     def test_dictfetchone_regions_1(self):
#         expected_regions = [
#             {"name": "region1"},
#             {"name": "region2"},
#             {"name": "region3"}
#         ]

#         cursor = self._query_regions({"sample_id": 1})
#         self.assertEqual(cursor.rowcount, 3)

#         for i in range(cursor.rowcount):
#             region = self.dictfetchone(cursor)
#             self.assertIn(region, expected_regions)
#             expected_regions = [expected_region for expected_region in expected_regions if expected_region != region]

#     # helper functions

#     def _query_regions(self, conditions):
#         from django.db import connection as con

#         query = (
#             "SELECT "
#                 "name "
#             "FROM "
#                 "regions, "
#                 "sample_regions "
#             "WHERE "
#                 "regions.region_id = sample_regions.region_id AND "
#                 "sample_regions.sample_id = %(sample_id)s"
#             "ORDER BY "
#                 "name"
#         )

#         cursor = con.cursor()
#         cursor.execute(query, conditions)

#         return cursor


# class SampleTest(FastFixtureTestCase):
#     def __init__(self, arg):
#         from webservices.sample import SampleObject
#         self.SampleObject = SampleObject

#         super(SampleTest, self).__init__(arg)

#     def test_sample_exists(self):
#         sample = self.SampleObject()
#         self.assertFalse(sample.exists())

#         sample = self.SampleObject(-1)
#         self.assertFalse(sample.exists())

#         sample = self.SampleObject()
#         sample.get(-1)
#         self.assertFalse(sample.exists())

#         sample.get("1")
#         self.assertTrue(sample.exists())

#     def test_sample_attributes_1(self):
#         import datetime

#         sample = self.SampleObject()

#         self.assertTrue(sample.get("1"))

#         expected_sample_attributes = {
#             "id": 1L,
#             "number": u"A",
#             "owner_name": u"B",
#             "description": u"D1",
#             "collector_name": u"A",
#             "collection_date": datetime.datetime(1984, 10, 27, 0, 0),
#             "location_text": u"A",
#             "longitude": 5.0,
#             "latitude": 10.0,
#             "country": u"A",
#             "public_data": True,
#             "subsamples_count": 3L,
#             "rock_type_name": u"Rock1",
#             "minerals": [
#                 {"name": u"mineral"}
#             ],
#             "images": [
#                 {
#                     'image_type': u'ONE',
#                     'checksum_64x64': u'A                                                 ',
#                     'height': 10,
#                     'width': 5,
#                     'checksum_half': u'A                                                 ',
#                     'filename': u'fileA'
#                 }
#             ],
#             "metamorphic_grades": [
#                 {"name": u"mg1"},
#                 {"name": u"mg4"}
#             ],
#             "metamorphic_regions": [
#                 {"name": u"mr1"},
#                 {"name": u"mr4"}
#             ],
#             "regions": [
#                 {"name": u"region1"},
#                 {"name": u"region2"},
#                 {"name": u"region3"}
#             ],
#             "references": [
#                 {"name": u"R1"}
#             ],
#             "aliases": [
#                 {"name": u"aliasA"}
#             ]
#         }
#         self.assertEquals(expected_sample_attributes, sample.attributes)
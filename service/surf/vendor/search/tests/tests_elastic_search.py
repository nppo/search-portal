from unittest import skipIf
from unittest.mock import patch
from dateutil.parser import parse
from datetime import datetime

from django.conf import settings

from project.configuration import create_elastic_search_index_configuration
from surf.vendor.elasticsearch.api import ElasticSearchApiClient
from surf.vendor.elasticsearch.serializers import EdusourcesSearchResultSerializer, NPPOSearchResultSerializer
from e2e_tests.base import BaseElasticSearchTestCase
from e2e_tests.elasticsearch_fixtures.elasticsearch import generate_nl_material


class TestsElasticSearch(BaseElasticSearchTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        math_and_education_disciplines = [
            "7afbb7a6-c29b-425c-9c59-6f79c845f5f0",  # math
            "0861c43d-1874-4788-b522-df8be575677f"  # onderwijskunde
        ]
        biology_disciplines = [
            "2b363227-8633-4652-ad57-c61f1efc02c8"
        ]
        biology_and_education_disciplines = biology_disciplines + [
            "0861c43d-1874-4788-b522-df8be575677f"
        ]

        cls.instance = ElasticSearchApiClient()
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["HBO"], source="surfsharekit",
                                      disciplines=math_and_education_disciplines),
        )
        cls.elastic.index(
            id="abc",
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["HBO"], source="surfsharekit",
                                      disciplines=math_and_education_disciplines, external_id="abc",
                                      title="De wiskunde van Jezus", description="Groots zijn zijn getallen")
        )
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["HBO"], source="surfsharekit",
                                      copyright="cc-by-40", topic="biology", publisher_date="2018-04-16T22:35:09+02:00",
                                      disciplines=biology_and_education_disciplines),
        )
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["HBO"], source="surfsharekit",
                                      topic="biology", publisher_date="2019-04-16T22:35:09+02:00",
                                      disciplines=biology_and_education_disciplines),
        )
        cls.elastic.index(
            index=settings.ELASTICSEARCH_NL_INDEX,
            body=generate_nl_material(educational_levels=["HBO"], technical_type="video", source="surfsharekit",
                                      topic="biology", disciplines=biology_disciplines),
            refresh=True  # always put refresh on the last material
        )

    def get_value_from_record(self, record, key):
        if settings.PROJECT == "edusources" and key != "publish_datetime":
            value = record[key]
        elif settings.PROJECT == "edusources" and key == "publish_datetime":
            value = parse(record[key], ignoretz=True)
        elif key == "authors":
            value = record["relations"]["authors"]
        elif key == "publishers":
            value = record["relations"]["parties"]
        elif key == "keywords":
            value = record["relations"]["keywords"]
        elif key == "technical_type":
            value = record["type"]
        elif key == "publish_datetime":
            value = parse(record["published_at"], ignoretz=True)
        else:
            raise ValueError(f"No translation for key '{key}' in NPPO project")
        return value

    def assert_value_from_record(self, record, key, expectation, assertion=None, message=None):
        assertion = assertion or self.assertEqual
        if settings.PROJECT == "edusources":
            pass
        elif key == "publishers":
            expectation = [
                {"name": name}
                for name in expectation
            ]
        elif key == "keywords":
            expectation = [
                {"label": label}
                for label in expectation
            ]
        elif key == "disciplines":
            return  # silently skipping this assertion, because NPPO doesn't support disciplines
        value = self.get_value_from_record(record, key)
        assertion(value, expectation, message)

    def test_basic_search(self):
        search_result = self.instance.search('')
        search_result_filter = self.instance.search(
            '', filters=[{"external_id": "lom.technical.format", "items": ["video"]}])
        # did we get _anything_ from search?
        self.assertIsNotNone(search_result)
        self.assertIsNotNone(search_result_filter)
        self.assertGreater(search_result['recordcount'], search_result_filter['recordcount'])
        self.assertEqual(set(search_result.keys()), {"recordcount", "records", "drilldowns", "did_you_mean"})
        # check if record count is an actual number
        # Edurep returns everything and Elastic nothing with an empty search
        self.assertIsInstance(search_result['recordcount'], int)
        # does an empty search return a list of records?
        self.assertIsInstance(search_result['records'], list)
        # are there no drilldowns for an empty search?
        self.assertIsInstance(search_result['drilldowns'], list)
        self.assertEqual(len(search_result['drilldowns']), 0)

        # basic search
        search_biologie = self.instance.search("biologie")
        self.assertIsNotNone(search_biologie)
        self.assertTrue(search_biologie["records"])
        self.assertIsNot(search_result, search_biologie)
        self.assertNotEqual(search_result['recordcount'], search_biologie['recordcount'])

        # basic search pagination
        search_page_1 = self.instance.search("", page_size=1)
        self.assertIsNotNone(search_page_1)
        self.assertNotEqual(search_page_1, search_result)
        search_page_2 = self.instance.search("", page=2, page_size=1)
        self.assertIsNotNone(search_page_2)
        self.assertNotEqual(search_page_2, search_page_1)

    def test_filter_search(self):
        # search with single filter applied
        search_biologie_video = self.instance.search(
            "biologie",
            filters=[{"external_id": "lom.technical.format", "items": ["video"]}]
        )
        self.assertTrue(search_biologie_video["records"])
        for record in search_biologie_video["records"]:
            self.assert_value_from_record(record, "technical_type", "video")
        search_biologie_video_and_docs = self.instance.search(
            "biologie",
            filters=[{"external_id": "lom.technical.format", "items": ["video", "document"]}]
        )
        self.assertGreater(len(search_biologie_video_and_docs["records"]), len(search_biologie_video["records"]))
        for record in search_biologie_video_and_docs["records"]:
            self.assert_value_from_record(record, "technical_type", ["video", "document"], self.assertIn)

        # search with multiple filters applied
        search_biologie_text_and_cc_by = self.instance.search(
            "biologie",
            filters=[
                {"external_id": "lom.technical.format", "items": ["document"]},
                {"external_id": "lom.rights.copyrightandotherrestrictions", "items": ["cc-by-40"]}
            ]
        )
        self.assertTrue(search_biologie_text_and_cc_by["records"])
        for record in search_biologie_text_and_cc_by["records"]:
            self.assert_value_from_record(record, "technical_type", "document")
            self.assertEqual(record["copyright"], "cc-by-40")

        # AND search with multiple filters applied
        search_biologie_and_didactiek = self.instance.search("biologie didactiek")
        search_biologie_and_didactiek_with_filters = self.instance.search(
            "biologie didactiek",
            filters=[
                {"external_id": "lom.technical.format", "items": ["document"]},
                {"external_id": "lom.rights.copyrightandotherrestrictions", "items": ["cc-by-40"]}
            ])

        self.assertIsNotNone(search_biologie_and_didactiek)
        self.assertTrue(search_biologie_and_didactiek["records"])
        self.assertIsNot(search_biologie_and_didactiek, search_biologie_and_didactiek_with_filters)
        self.assertTrue(search_biologie_and_didactiek_with_filters["records"])
        self.assertNotEqual(
            search_biologie_and_didactiek['recordcount'],
            search_biologie_and_didactiek_with_filters['recordcount']
        )

        # search with publish date filter applied
        search_biologie_upper_date = self.instance.search("biologie", filters=[
            {"external_id": "lom.lifecycle.contribute.publisherdate", "items": [None, "2018-12-31"]}
        ])
        self.assertTrue(search_biologie_upper_date["records"])
        for record in search_biologie_upper_date["records"]:
            self.assert_value_from_record(
                record,
                "publish_datetime",
                datetime(year=2018, month=12, day=31),
                self.assertLessEqual
            )
        search_biologie_lower_date = self.instance.search("biologie", filters=[
            {"external_id": "lom.lifecycle.contribute.publisherdate", "items": ["2018-01-01", None]}
        ])
        self.assertTrue(search_biologie_lower_date["records"])
        for record in search_biologie_lower_date["records"]:
            self.assert_value_from_record(
                record,
                "publish_datetime",
                datetime.strptime("2018-01-01", "%Y-%m-%d"),
                self.assertGreaterEqual
            )
        search_biologie_between_date = self.instance.search("biologie", filters=[
            {"external_id": "lom.lifecycle.contribute.publisherdate", "items": ["2018-01-01", "2018-12-31"]}
        ])
        self.assertTrue(search_biologie_between_date["records"])
        for record in search_biologie_between_date["records"]:
            self.assert_value_from_record(
                record,
                "publish_datetime",
                datetime.strptime("2018-12-31", "%Y-%m-%d"),
                self.assertLessEqual
            )
            self.assert_value_from_record(
                record,
                "publish_datetime",
                datetime.strptime("2018-01-01", "%Y-%m-%d"),
                self.assertGreaterEqual
            )

        # search with None, None as date filter. This search should give the same result as not filtering at all.
        search_biologie_none_date = self.instance.search("biologie", filters=[
            {"external_id": "lom.lifecycle.contribute.publisherdate", "items": [None, None]}
        ])
        search_biologie = self.instance.search("biologie")
        self.assertEqual(search_biologie_none_date, search_biologie)

    @skipIf(settings.PROJECT == "nppo", "Disciplines not supported by NPPO")
    def test_search_disciplines(self):
        search_result = self.instance.search('')
        search_result_filter_1 = self.instance.search(
            '',
            filters=[{
                "external_id": "lom.classification.obk.discipline.id",
                "items": ['0861c43d-1874-4788-b522-df8be575677f']
            }]
        )
        search_result_filter_2 = self.instance.search(
            '',
            filters=[{
                "external_id": "lom.classification.obk.discipline.id",
                "items": ['2b363227-8633-4652-ad57-c61f1efc02c8']
            }]
        )
        search_result_filter_3 = self.instance.search(
            '',
            filters=[{
                "external_id": "lom.classification.obk.discipline.id",
                "items": ['0861c43d-1874-4788-b522-df8be575677f', '2b363227-8633-4652-ad57-c61f1efc02c8']
            }]
        )
        self.assertNotEqual(search_result, search_result_filter_1)
        self.assertNotEqual(search_result, search_result_filter_2)
        self.assertNotEqual(search_result_filter_1, search_result_filter_2)
        self.assertGreater(search_result['recordcount'], 0)
        self.assertGreater(search_result_filter_1['recordcount'], 0)
        self.assertGreater(search_result_filter_2['recordcount'], 0)
        self.assertGreater(
            search_result_filter_1['recordcount'] + search_result_filter_2['recordcount'],
            search_result_filter_3['recordcount'],
            "Expected at least 1 material to appear in both search_result_filter_1 and search_result_filter_2, "
            "which would make the sum of those results larger than filtering on both disciplines together"
        )

    def test_drilldown_search(self):
        search_biologie = self.instance.search("biologie", drilldown_names=["lom.technical.format"])
        self.assertIsNotNone(search_biologie)
        self.assertTrue(search_biologie['drilldowns'])
        self.assertTrue(search_biologie['drilldowns'][0]['items'])
        for item in search_biologie['drilldowns'][0]['items']:
            self.assertTrue(item['external_id'])
            self.assertIsNotNone(item['count'])

    @skipIf(settings.PROJECT == "nppo", "Disciplines not supported by NPPO")
    def test_drilldown_search_disciplines(self):
        search_with_theme_drilldown = self.instance.search(
            '',
            drilldown_names=["lom.classification.obk.discipline.id"]
        )
        self.assertIsNotNone(search_with_theme_drilldown)
        self.assertTrue(search_with_theme_drilldown['drilldowns'])
        self.assertEqual(
            [drilldown["external_id"] for drilldown in search_with_theme_drilldown['drilldowns']],
            ["lom.classification.obk.discipline.id"]
        )
        for drilldown in search_with_theme_drilldown['drilldowns']:
            self.assertTrue(drilldown["items"])
            for item in drilldown['items']:
                self.assertTrue(item['external_id'])
                self.assertIsNotNone(item['count'])

    def test_drilldown_with_filters(self):
        search = self.instance.search(
            "biologie",
            filters=[
                {"external_id": "lom.technical.format", "items": ["text"]}
            ],
            drilldown_names=['about.repository', 'lom.technical.format']
        )

        drilldowns = search['drilldowns']
        drilldowns_for_format = next((d for d in drilldowns if d['external_id'] == 'lom.technical.format'), None)
        drilldowns_for_repo = next((d for d in drilldowns if d['external_id'] == 'about.repository'), None)

        total_for_format = sum(item['count'] for item in drilldowns_for_format['items'])
        total_for_repo = sum(item['count'] for item in drilldowns_for_repo['items'])

        # The counts for format do not include the filter (as it is applied to format)
        # The counts for repo DO include the format filter, so it returns less results
        self.assertGreater(total_for_format, total_for_repo)

    def test_ordering_search(self):
        # make a bunch of queries with different ordering
        search_biologie = self.instance.search("biologie")
        self.assertIsNotNone(search_biologie)
        self.assertTrue(search_biologie["records"])
        search_biologie_dates = [
            self.get_value_from_record(record, "publish_datetime")
            for record in search_biologie["records"]
        ]
        search_biologie_asc = self.instance.search("biologie", ordering="lom.lifecycle.contribute.publisherdate")
        self.assertIsNotNone(search_biologie_asc)
        self.assertTrue(search_biologie_asc["records"])
        search_biologie_asc_dates = [
            self.get_value_from_record(record, "publish_datetime")
            for record in search_biologie_asc["records"]
        ]
        search_biologie_desc = self.instance.search("biologie", ordering="lom.lifecycle.contribute.publisherdate")
        self.assertIsNotNone(search_biologie_desc)
        self.assertTrue(search_biologie_asc["records"])
        search_biologie_desc_dates = [
            self.get_value_from_record(record, "publish_datetime")
            for record in search_biologie_desc["records"]
        ]
        # make sure that a default ordering is different than a date ordering
        self.assertNotEqual(search_biologie_dates, search_biologie_asc_dates)
        self.assertNotEqual(search_biologie_dates, search_biologie_desc_dates)
        # make sure that the dates of results are indeed in expected order
        self.assertEqual(search_biologie_asc_dates, sorted(search_biologie_asc_dates))
        self.assertEqual(search_biologie_desc_dates, sorted(search_biologie_desc_dates, reverse=False))

    def test_autocomplete(self):
        empty_autocomplete = self.instance.autocomplete(query='')
        self.assertEqual(len(empty_autocomplete), 0)
        biologie_autocomplete = self.instance.autocomplete(query='bio')
        self.assertGreater(len(biologie_autocomplete), 0)
        self.assertIsNot(empty_autocomplete, biologie_autocomplete)
        self.assertIsInstance(biologie_autocomplete, list)
        for item in biologie_autocomplete:
            self.assertIsInstance(item, str)
            self.assertTrue('biologie' in item)

    def test_drilldowns(self):
        empty_drilldowns = self.instance.drilldowns(drilldown_names=[])
        self.assertGreater(empty_drilldowns['recordcount'], 0)
        self.assertFalse(empty_drilldowns['records'])
        self.assertFalse(empty_drilldowns['drilldowns'])

        biologie_drilldowns = self.instance.drilldowns([], search_text="biologie")
        self.assertGreater(biologie_drilldowns['recordcount'], 0)
        self.assertGreater(empty_drilldowns['recordcount'], biologie_drilldowns['recordcount'])
        self.assertFalse(biologie_drilldowns['records'])
        self.assertFalse(biologie_drilldowns['drilldowns'])

        repo_drilldowns = self.instance.drilldowns(['about.repository'])
        self.assertTrue(repo_drilldowns['drilldowns'])
        self.assertTrue(repo_drilldowns['drilldowns'][0]['items'])
        for item in repo_drilldowns['drilldowns'][0]['items']:
            self.assertTrue(item['external_id'])
            self.assertIsNotNone(item['count'])

        repo_and_format_drilldowns = self.instance.drilldowns(['about.repository', 'lom.technical.format'])
        self.assertTrue(repo_and_format_drilldowns['drilldowns'])
        for drilldown in repo_and_format_drilldowns['drilldowns']:
            self.assertTrue(drilldown['items'])
            for item in drilldown['items']:
                self.assertTrue(item['external_id'])
                self.assertIsNotNone(item['count'])

    def test_get_materials_by_id(self):
        # Sharekit material
        test_id = '3522b79c-928c-4249-a7f7-d2bcb3077f10'
        result = self.instance.get_materials_by_id(external_ids=[test_id])
        self.assertIsNotNone(result)
        self.assertEqual(result['recordcount'], 1, "Expected one result when searching for one id")
        material = result['records'][0]

        self.assertEqual(material['title'], 'Didactiek van wiskundig denken')
        self.assertEqual(
            material['url'],
            "https://maken.wikiwijs.nl/91192/Wiskundedidactiek_en_ICT"
        )
        self.assertEqual(material['external_id'], "3522b79c-928c-4249-a7f7-d2bcb3077f10")
        self.assert_value_from_record(material, 'publishers', ["Wikiwijs Maken"])
        self.assert_value_from_record(
            material,
            'publish_datetime',
            datetime(year=2017, month=4, day=16, hour=22, minute=35, second=9)
        )
        self.assert_value_from_record(material, 'authors', [
            {"name": "Michel van Ast"},
            {"name": "Theo van den Bogaart"},
            {"name": "Marc de Graaf"},
        ])
        self.assert_value_from_record(material, 'keywords', ["nerds"])
        self.assert_value_from_record(material, 'disciplines', [
            "7afbb7a6-c29b-425c-9c59-6f79c845f5f0",  # math
            "0861c43d-1874-4788-b522-df8be575677f"  # onderwijskunde
        ])
        self.assertEqual(material['language'], 'nl')
        self.assert_value_from_record(material, 'technical_type', 'document')

        # Sharekit (legacy id format)
        test_id = 'surfsharekit:oai:surfsharekit.nl:3522b79c-928c-4249-a7f7-d2bcb3077f10'
        result = self.instance.get_materials_by_id(external_ids=[test_id])
        self.assertIsNotNone(result)
        self.assertEqual(result['recordcount'], 1, "Expected one result when searching for one id")
        material = result['records'][0]
        self.assertEqual(material['external_id'], "3522b79c-928c-4249-a7f7-d2bcb3077f10")

        # Edurep material
        test_id = 'wikiwijs:123'
        result = self.instance.get_materials_by_id(external_ids=[test_id])
        self.assertIsNotNone(result)
        self.assertEqual(result['recordcount'], 1, "Expected one result when searching for one id")
        material = result['records'][0]
        self.assertEqual(material['external_id'], "wikiwijs:123")

    def test_search_by_author(self):
        author = "Michel van Ast"
        expected_record_count = 5
        self.check_author_search(author, expected_record_count)

        author2 = "Theo van den Bogaart"
        expected_record_count2 = 2
        self.check_author_search(author2, expected_record_count2)

    def check_author_search(self, author, expected_record_count):
        search_author = self.instance.search(
            '',
            filters=[{"external_id": "lom.lifecycle.contribute.author", "items": [author]}]
        )
        for record in search_author['records']:
            authors = [author["name"] for author in self.get_value_from_record(record, 'authors')]
            self.assertIn(author, authors)
        self.assertEqual(search_author['recordcount'], expected_record_count)

    def test_search_did_you_mean(self):
        spelling_mistake = self.instance.search('didaktiek')
        self.assertIn("did_you_mean", spelling_mistake)
        self.assertEqual(spelling_mistake["did_you_mean"]["original"], "didaktiek")
        self.assertEqual(spelling_mistake["did_you_mean"]["suggestion"], "didactiek")
        no_result_spelling_mistake = self.instance.search('didaktiek is fantastiek')
        self.assertEqual(no_result_spelling_mistake["did_you_mean"], {})
        no_mistake = self.instance.search('biologie')
        self.assertEqual(no_mistake["did_you_mean"], {})
        unknown_mistake = self.instance.search('sdfkhjsdgaqegkjwfgklsd')
        self.assertEqual(unknown_mistake["did_you_mean"], {})

    def test_composed_word_search(self):
        # Github Actions does not support mounting docker volumes
        # So it is impossible to mount a decompound dictionary and truly test this
        # Instead we test that indices will get created correctly and composed word search should function
        dutch_index = create_elastic_search_index_configuration("nl", "dutch", "dutch-decompound-words.txt")
        self.assertIn("dutch_dictionary_decompound", dutch_index["settings"]["analysis"]["analyzer"])
        decompound_analyser = dutch_index["settings"]["analysis"]["analyzer"]["dutch_dictionary_decompound"]
        self.assertEqual(decompound_analyser, {
            'type': 'custom',
            'tokenizer': 'standard',
            'filter': [
                'lowercase',
                'dutch_stop',
                'dictionary_decompound'
            ]
        })
        self.assertIn("dictionary_decompound", dutch_index["settings"]["analysis"]["filter"])
        decompound_filter = dutch_index["settings"]["analysis"]["filter"]["dictionary_decompound"]
        self.assertEqual(decompound_filter, {
            'type': 'dictionary_decompounder',
            'word_list_path': 'dutch-decompound-words.txt',
            'updateable': True
        })
        for text_field in ["title", "text", "description"]:
            self.assertEqual(dutch_index["mappings"]["properties"][text_field]['fields']['analyzed']["analyzer"],
                             "dutch")
            self.assertEqual(dutch_index["mappings"]["properties"][text_field]['fields']['analyzed']["search_analyzer"],
                             "dutch_dictionary_decompound")

        english_index = create_elastic_search_index_configuration("en", "english")
        self.assertNotIn("dutch_dictionary_decompound", english_index["settings"]["analysis"]["analyzer"])
        self.assertNotIn("dictionary_decompound", english_index["settings"]["analysis"]["filter"])
        for text_field in ["title", "text", "description"]:
            self.assertEqual(
                english_index["mappings"]["properties"][text_field]['fields']['analyzed']["analyzer"],
                "english"
            )
            self.assertEqual(
                english_index["mappings"]["properties"][text_field]['fields']['analyzed']["search_analyzer"],
                "english"
            )

    def test_more_like_this(self):
        more_like_this = self.instance.more_like_this("abc", "nl")
        self.assertEqual(more_like_this["records_total"], 4)
        self.assertEqual(more_like_this["results"][0]["title"], "Didactiek van wiskundig denken")
        none_like_this = self.instance.more_like_this("does-not-exist", "nl")
        self.assertEqual(none_like_this["records_total"], 0)
        self.assertEqual(none_like_this["results"], [])

    def test_author_suggestions(self):
        suggestions = self.instance.author_suggestions("Theo")
        author_expectation = "Theo van den Bogaart"
        self.assertEqual(suggestions["records_total"], 3)
        for result in suggestions["results"]:
            author_names = [author["name"] for author in self.get_value_from_record(result, "authors")]
            self.assertNotIn(author_expectation, author_names)
            self.assertIn(author_expectation, result["description"])

    def test_parse_elastic_hit(self):
        authors = [{"name": "author"}]
        themes = ["theme"]
        hit = {
            "_source": {
                "title": "title",
                "description": "description",
                "authors": authors,
                "themes": themes,
                "research_themes": themes
            }
        }
        with patch("surf.vendor.elasticsearch.api.SearchResultSerializer", EdusourcesSearchResultSerializer):
            record = self.instance.parse_elastic_hit(hit)
            self.assertIn("authors", record, "Expected authors to be part of main record for Edusources")
            self.assertIn("themes", record, "Expected themes to be part of main record for Edusources")
            self.assertEqual(record["title"], "title")
            self.assertEqual(record["description"], "description")
            self.assertEqual(record["authors"], authors)
            self.assertEqual(record["themes"], themes)
            self.assertNotIn("keywords", record, "Expected data not given in Edusources to not be included")
            self.assertNotIn("is_part_of", record, "Expected data not given in Edusources to not be included")
            self.assertNotIn("has_parts", record, "Expected data not given in Edusources to not be included")
        with patch("surf.vendor.elasticsearch.api.SearchResultSerializer", NPPOSearchResultSerializer):
            record = self.instance.parse_elastic_hit(hit)
            self.assertIn("relations", record, "Expected NPPO record to have a relations key")
            self.assertNotIn("authors", record, "Expected authors to be absent in main record for NPPO")
            self.assertNotIn("themes", record, "Expected themes to be absent in main record for NPPO")
            self.assertIn("authors", record["relations"], "Expected authors to be part of relations for NPPO")
            self.assertIn("themes", record["relations"], "Expected themes to be part of relations for NPPO")
            self.assertEqual(record["title"], "title")
            self.assertEqual(record["description"], "description")
            self.assertEqual(record["relations"]["authors"], authors)
            self.assertEqual(record["relations"]["themes"], [{"label": "theme"}])
            self.assertEqual(record["relations"]["keywords"], [], "Expected data not given in NPPO to have a default")
            self.assertEqual(record["relations"]["parents"], [], "Expected data not given in NPPO to have a default")
            self.assertEqual(record["relations"]["children"], [], "Expected data not given in NPPO to have a default")

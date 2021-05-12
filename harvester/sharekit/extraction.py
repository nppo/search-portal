import re

from datagrowth.utils import reach

from core.constants import HIGHER_EDUCATION_LEVELS, RESTRICTED_MATERIAL_SETS


class SharekitMetadataExtraction(object):

    youtube_regex = re.compile(r".*(youtube\.com|youtu\.be).*", re.IGNORECASE)

    @classmethod
    def get_record_state(cls, node):
        return "active"

    #############################
    # GENERIC
    #############################

    @classmethod
    def get_files(cls, node):
        files = node["attributes"]["files"] or []
        links = node["attributes"]["links"] or []
        output = [
            [file["resourceMimeType"], file["url"]]
            for file in files if file["resourceMimeType"] and file["url"]
        ]
        output += [
            ["text/html", link["url"]]
            for link in links
        ]
        return output

    @classmethod
    def get_url(cls, node):
        files = cls.get_files(node)
        if not files:
            return
        return files[0][1]

    @classmethod
    def get_mime_type(cls, node):
        files = cls.get_files(node)
        if not files:
            return
        return files[0][0]

    @classmethod
    def get_copyright(cls, node):
        return node["attributes"]["termsOfUse"]

    @classmethod
    def get_from_youtube(cls, node):
        url = cls.get_url(node)
        if not url:
            return False
        return cls.youtube_regex.match(url) is not None

    @classmethod
    def get_authors(cls, node):
        authors = node["attributes"]["authors"] or []
        return [
            author["person"]["name"]
            for author in authors
        ]

    @classmethod
    def get_publishers(cls, node):
        publisher = node["attributes"]["publishers"]
        if not publisher:
            return []
        return [publisher]

    @classmethod
    def get_lom_educational_levels(cls, node):
        educational_levels = node["attributes"]["educationalLevels"]
        if not educational_levels:
            return []
        return list(set([
            educational_level["value"] for educational_level in educational_levels
            if educational_level["value"]
        ]))

    @classmethod
    def get_lowest_educational_level(cls, node):
        educational_levels = cls.get_lom_educational_levels(node)
        current_numeric_level = 3 if len(educational_levels) else -1
        for education_level in educational_levels:
            for higher_education_level, numeric_level in HIGHER_EDUCATION_LEVELS.items():
                if not education_level.startswith(higher_education_level):
                    continue
                # One of the records education levels matches a higher education level.
                # We re-assign current level and stop processing this education level,
                # as it shouldn't match multiple higher education levels
                current_numeric_level = min(current_numeric_level, numeric_level)
                break
            else:
                # No higher education level found inside current education level.
                # Dealing with an "other" means a lower education level than we're interested in.
                # So this record has the lowest possible level. We're done processing this seed.
                current_numeric_level = 0
                break
        return current_numeric_level

    @classmethod
    def get_disciplines(cls, node):
        return []

    @classmethod
    def get_ideas(cls, node):
        compound_ideas = [vocabulary["value"] for vocabulary in node["attributes"]["vocabularies"]]
        if not compound_ideas:
            return []
        ideas = []
        for compound_idea in compound_ideas:
            ideas += compound_idea.split(" - ")
        return list(set(ideas))

    @classmethod
    def get_is_restricted(cls, data):
        link = data["links"]["self"]
        for restricted_set in RESTRICTED_MATERIAL_SETS:
            if restricted_set in link:
                return True
        return False

    @classmethod
    def get_analysis_allowed(cls, node):
        # We disallow analysis for non-derivative materials as we'll create derivatives in that process
        # NB: any material that is_restricted will also have analysis_allowed set to False
        copyright = SharekitMetadataExtraction.get_copyright(node)
        return (copyright is not None and "nd" not in copyright) and copyright != "yes"

    @classmethod
    def get_is_part_of(cls, node):
        return reach("$.attributes.partOf.0", node)


SHAREKIT_EXTRACTION_OBJECTIVE = {
    "url": SharekitMetadataExtraction.get_url,
    "files": SharekitMetadataExtraction.get_files,
    "title": "$.attributes.title",
    "language": "$.attributes.language",
    "keywords": "$.attributes.keywords",
    "description": "$.attributes.abstract",
    "mime_type": SharekitMetadataExtraction.get_mime_type,
    "copyright": SharekitMetadataExtraction.get_copyright,
    "aggregation_level": "$.attributes.aggregationlevel",
    "authors": SharekitMetadataExtraction.get_authors,
    "publishers": SharekitMetadataExtraction.get_publishers,
    "publisher_date": "$.attributes.publishedAt",
    "lom_educational_levels": SharekitMetadataExtraction.get_lom_educational_levels,
    "lowest_educational_level": SharekitMetadataExtraction.get_lowest_educational_level,
    "disciplines": SharekitMetadataExtraction.get_disciplines,
    "ideas": SharekitMetadataExtraction.get_ideas,
    "from_youtube": SharekitMetadataExtraction.get_from_youtube,
    "#is_restricted": SharekitMetadataExtraction.get_is_restricted,
    "analysis_allowed": SharekitMetadataExtraction.get_analysis_allowed,
    "is_part_of": SharekitMetadataExtraction.get_is_part_of,
    "has_parts": "$.attributes.hasParts"
}
import re
from ..schema import ImageSchema
from .model import PatentImage
from yankee.xml import fields as f
from yankee.util import clean_whitespace, unzip_records

from patent_client.uspto.fulltext.util import text_section_xpath, TextField
from patent_client.uspto.fulltext.schema import Schema, RegexSchema
from patent_client.util.format import clean_appl_id


class ApplicantSchema(Schema):
    name = f.Str(".//td[1]")
    city = f.Str(".//td[2]")
    state = f.Str(".//td[3]")
    country = f.Str(".//td[4]")
    type = f.Str(".//td[5]")


class USReferenceSchema(Schema):
    publication_number = f.Str(".//td[1]")
    date = f.Date(".//td[2]")
    first_named_inventor = f.Str(".//td[3]")


class ForeignReferenceSchema(Schema):
    publication_number = f.Str(".//td[2]")
    date = f.Date(".//td[4]")
    country_code = f.Str(".//td[6]")


class RelatedPatentDocumentSchema(Schema):
    appl_id = f.Str(".//td[2]")
    filing_date = f.Date(".//td[3]")
    patent_number = f.Str(".//td[4]")


class InventorSchema(RegexSchema):
    last_name = f.Str(".//last_name")
    first_name = f.Str(".//first_name")
    city = f.Str(".//city")
    region = f.Str(".//region")

    __regex__ = r"(?P<last_name>[^;]+); (?P<first_name>[^;]+);? \((?P<city>[^,]+), (?P<region>[^)]+)\)"

    def load(self, obj):
        return super().load(obj)


class ExaminerSchema(RegexSchema):
    last_name = f.Str(".//last_name")
    first_name = f.Str(".//first_name")
    __regex__ = r"(?P<last_name>[^;]+); (?P<first_name>.+)"


class AssigneeSchema(RegexSchema):
    name = f.Str(".//name")
    city = f.Str(".//city")
    region = f.Str(".//region")

    __regex__ = r"(?P<name>[^;]+) \((?P<city>[^,]+), (?P<region>[^)]+)\)"


class FieldOfSearchField(f.String):
    def post_load(self, obj):
        if obj is None:
            return None
        groups = obj.strip(";").split(" ;")
        output = list()
        for group in groups:
            cl, *subcls = re.split("[,/]", group)
            output += [f"{cl}/{subcl}" for subcl in subcls]
        return output

class USClassField(f.String):
    def post_load(self, obj):
        if obj is None:
            return None
        return obj.strip(";").split("; ")


class CpcClassField(f.String):
    cpc_re = re.compile(r"(?P<class>[A-Z]\d{2}[A-Z] \d{1,}/\d{2,}) \(?(?P<version>\d{8})?\)?")

    def post_load(self, obj):
        if obj is None:
            return None
        obj = obj.replace("&nbsp", " ")
        try:
            return [self.cpc_re.search(c).groupdict() for c in obj.split(";")]
        except AttributeError:  # Design Patent
            return [
                {"class": obj, "version": None},
            ]


class KindCode(Schema):
    kind_code_label = f.Str(".//hr[1]/following::table[1]//tr[2]/td[1]")
    kind_code = f.Str(".//hr[1]/following::table[1]//tr[2]/td[2]")
    pub_number = f.Str(
        './/b[contains(text(), "Prior Publication Data")]/parent::center/following-sibling::table//tr[3]/td[2]'
    )

    def post_load(self, obj):
        if obj["kind_code_label"] == "Kind Code":
            return obj["kind_code"]
        elif "pub_number" in obj:
            return "B2"
        return "B1"


class ForeignPriorityDateSchema(RegexSchema):
    date = f.Date("./date")
    country_code = f.Str("./country_code")
    __regex__ = r"(?P<date>[^\[]+)\[(?P<country_code>[^\]]+)\]"


class ForeignPrioritySchema(Schema):
    left_col = ForeignPriorityDateSchema(".//td[1]", flatten=True)
    number = f.Str(".//td[4]")

class TailField(f.Field):
    """Field to retreive tail text"""
    def load(self, obj):
        return super().load(obj)

    def deserialize(self, obj):
        return clean_whitespace(super().deserialize(obj).tail)

class ZipSchema(Schema):
    name = TailField('//td[1]/b/br')
    city = TailField('.//td[2]/br')
    state = TailField('.//td[3]/br')
    country = TailField('.//td[4]/br')

    def bind(self, name=None, parent=None):
        super().bind(name, parent)
        new_fields = dict()
        for name, field in self.fields.items():
            new_fields[name] = f.List(field.__class__, getattr(field.accessor, "data_key", None))
        self.fields = new_fields

    def deserialize(self, obj) -> "Dict":
        result = unzip_records(super().deserialize(obj))
        return result

class PatentSchema(Schema):
    publication_number = f.Str(".//hr[1]/following::table[1]//tr[1]/td[2]", formatter=lambda s: s.replace(",", ""))
    publication_date = f.Date(
        './/b[contains(text(), "Issue Date:")]/ancestor::tr/td[2]',
        formatter=lambda s: s.replace("*", "").strip(),
    )
    kind_code = KindCode()
    title = f.Str(".//hr[2]/following::font")
    appl_id = f.Str(
        './/*[contains(text(), "Appl. No.")]/following-sibling::td',
        formatter=clean_appl_id,
    )

    abstract = f.Str('.//b[contains(text(), "Abstract")]/parent::center/following-sibling::p')
    inventors = f.DelimitedString(
        InventorSchema,
        data_key='.//th[contains(text(), "Inventors:")]//following-sibling::td',
        delimeter=re.compile(r"(?<=\))\s*[,;]\s*"),
    )
    applicants = ZipSchema('.//th[contains(text(), "Applicant")]//following::table[1]//tr[2]')
    assignees = f.List(
        AssigneeSchema,
        data_key='.//th[contains(text(), "Assignee:")]/following-sibling::td',
    )
    family_id = f.Str(data_key='.//*[contains(text(), "Family ID:")]/following-sibling::td')
    filing_date = f.Date(data_key='.//*[contains(text(), "Filed:")]/following-sibling::td')
    app_early_pub_number = f.Str(
        './/b[contains(text(), "Prior Publication Data")]/parent::center/following-sibling::table//tr[3]/td[2]'
    )
    app_early_pub_date = f.Date(
        './/b[contains(text(), "Prior Publication Data")]/parent::center/following-sibling::table//tr[3]/td[3]'
    )
    us_classes = USClassField('.//b[contains(text(), "Current U.S. Class")]/ancestor::tr/td[2]')
    cpc_classes = CpcClassField('.//b[contains(text(), "Current CPC Class")]/ancestor::tr/td[2]')
    intl_classes = CpcClassField('.//b[contains(text(), "Current International Class")]/ancestor::tr/td[2]')
    field_of_search = FieldOfSearchField('.//b[contains(text(), "Field of Search")]/ancestor::tr/td[2]')
    us_references = f.List(
        USReferenceSchema,
        './/center/b[text()="U.S. Patent Documents"]/parent::center/following-sibling::table[1]//tr',
    )
    foreign_references = f.List(
        ForeignReferenceSchema,
        './/center/b[contains(text(), "Foreign Patent Documents")]/parent::center/following-sibling::table[1]//tr',
    )
    npl_references = f.List(
        TailField,
        './/center/b[contains(text(), "Other References")]/following::td//br',
    )
    primary_examiner = ExaminerSchema('//i[contains(text(), "Primary Examiner")]/following-sibling::text()')
    assistant_examiner = ExaminerSchema('//i[contains(text(), "Assistant Examiner")]/following-sibling::text()')
    agent = f.Str('//i[contains(text(), "Attorney")]/following-sibling::coma/text()')
    claims = TextField(data_key=text_section_xpath("Claims"))
    description = TextField(data_key=text_section_xpath("Description"))
    parent_case_text = TextField(data_key=text_section_xpath("Parent Case Text"))
    related_us_applications = f.List(
        RelatedPatentDocumentSchema,
        './/*[contains(text(), "Related U.S. Patent Documents")]/ancestor::center/following::table[1]//tr[position() > 2]',
    )
    foreign_priority = f.List(
        ForeignPrioritySchema,
        data_key='.//b[text()="Foreign Application Priority Data"]/following::table[1]//tr',
    )
    pdf_url = f.Str('.//img[@alt="[Image]"]/parent::a/@href')

    def deserialize(self, obj) -> "Dict":
        return super().deserialize(obj)


class PatentImageSchema(ImageSchema):
    __model__ = PatentImage


class PatentResultSchema(Schema):
    seq = f.Int(".//td[1]")
    publication_number = f.Str(".//td[2]", formatter=lambda s: s.replace(",", ""))
    title = f.Str(".//td[4]")


class ResultMetaSchema(RegexSchema):
    __regex__ = r"Hits (?P<start>\d+) through (?P<end>\d+) out of (?P<num_results>\d+)"
    start = f.Int(".//start")
    end = f.Int(".//end")
    num_results = f.Int(".//num_results")


class PatentResultPageSchema(Schema):
    query = f.Str('.//span[@id="srchtext"]')
    result = ResultMetaSchema('.//span[@id="srchtext"]/following::i', flatten=True)
    results = f.List(PatentResultSchema, "((.//table)[2]//tr)[position()>1]")

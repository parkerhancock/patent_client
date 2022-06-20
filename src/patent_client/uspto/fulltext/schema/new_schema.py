from yankee.xml import Schema, RegexSchema, fields as f
from yankee.util import clean_whitespace
import re
import lxml.html as ETH
from patent_client.util.schema_mixin import PatentSchemaMixin

class BaseSchema(PatentSchemaMixin, Schema):
    pass

class BaseRegexSchema(PatentSchemaMixin, RegexSchema):
    pass

non_digit_re = re.compile(r"[^\d]+")

def clean_number(string):
    return non_digit_re.sub("", string)

def clean_appl_id(string):
    return string.replace(",", "").replace("/", "").replace("D", "29").strip()


class ApplicantSchema(BaseSchema):
    name = f.Str(".//td[1]")
    city = f.Str(".//td[2]")
    state = f.Str(".//td[3]")
    country = f.Str(".//td[4]")
    type = f.Str(".//td[5]")
    
class USReferenceSchema(BaseSchema):
    publication_number = f.Str(".//td[1]")
    date = f.Date(".//td[2]")
    first_named_inventor = f.Str(".//td[3]")
    
class ForeignReferenceSchema(BaseSchema):
    publication_number = f.Str(".//td[2]")
    date = f.Date(".//td[4]")
    country_code = f.Str(".//td[6]")

class RelatedPatentDocumentSchema(BaseSchema):
    appl_id = f.Str(".//td[2]")
    filing_date = f.Date(".//td[3]")
    patent_number = f.Str(".//td[4]")
      

class InventorSchema(BaseRegexSchema):
    last_name = f.Str(".//last_name")
    first_name = f.Str(".//first_name")
    city = f.Str(".//city")
    region = f.Str(".//region")
    
    __regex__ = r"(?P<last_name>[^;]+); (?P<first_name>[^;]+);? \((?P<city>[^,]+), (?P<region>[^)]+)\)"

    def load(self, obj):
        return super().load(obj)
    
class ExaminerSchema(BaseRegexSchema):
    last_name = f.Str(".//last_name")
    first_name = f.Str(".//first_name")
    __regex__ = r"(?P<last_name>[^;]+); (?P<first_name>.+)"
    
    
class AssigneeSchema(BaseRegexSchema):
    name = f.Str(".//name")
    city = f.Str(".//city")
    region = f.Str(".//region")

    __regex__ = r"(?P<name>[^;]+) \((?P<city>[^,]+), (?P<region>[^)]+)\)"
    
class TextField(f.List):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, item_schema = f.Field(), **kwargs)
    
    def load(self, obj):
        result = super().load(obj)
        text = "\n".join(result).strip()
        return "\n\n".join([clean_whitespace(p) for p in text.split("\n\n")])
    
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

def xpath_intersection(ns1, ns2):
    return f"{ns1}[count(.|{ns2})=count({ns2})]"

def xpath_difference(ns1, ns2):
    return f"{ns1}[count({ns1}) != count({ns2})]"
        
def text_section_xpath(heading):
    ns1 = f'//i[contains(text(), "{heading}")]/ancestor::center/following::hr[1]/following::text()'
    ns2 = f'//i[contains(text(), "{heading}")]/ancestor::center/following::hr[2]/preceding::text()'
    return xpath_intersection(ns1, ns2)

class KindCode(Schema):
    kind_code_label = f.Str(".//hr[1]/following::table[1]//tr[2]/td[1]")
    kind_code = f.Str(".//hr[1]/following::table[1]//tr[2]/td[2]")
    pub_number = f.Str('.//b[contains(text(), "Prior Publication Data")]/parent::center/following-sibling::table//tr[3]/td[2]')

    def post_load(self, obj):
        if obj['kind_code_label'] == "Kind Code":
            return obj['kind_code']
        elif 'pub_number' in obj:
            return "B2"
        return "B1"

class ForeignPriorityDateSchema(RegexSchema):
    date = f.Date("./date")
    country_code = f.Str("./country_code")
    __regex__ = r'(?P<date>[^\[]+)\[(?P<country_code>[^\]]+)\]'

class ForeignPrioritySchema(BaseSchema):
    left_col = ForeignPriorityDateSchema(".//td[1]", flatten=True)
    number = f.Str(".//td[4]")


class PublicationSchema(BaseSchema):
    publication_number = f.Str(".//hr[1]/following::table[1]//tr[1]/td[2]")
    publication_date = f.Date(".//hr[1]/following::table[1]//tr[last()]/td[2]", formatter=lambda s: s.replace("*", "").strip())
    kind_code = KindCode()
    title = f.Str(".//hr[2]/following::font")
    appl_id = f.Str('.//*[contains(text(), "Appl. No.")]/following-sibling::td',formatter=clean_appl_id)
    
    abstract = f.Str('.//b[contains(text(), "Abstract")]/parent::center/following-sibling::p')
    inventors = f.DelimitedString(InventorSchema, data_key='.//th[contains(text(), "Inventors:")]//following-sibling::td', delimeter=re.compile(r"(?<=\))[,;]\s*"))
    applicants = f.List(ApplicantSchema, './/th[contains(text(), "Applicant:")]/following-sibling::td//tr[position()>1]', many=True)
    assignees = f.List(AssigneeSchema, data_key='.//th[contains(text(), "Assignee:")]/following-sibling::td')
    family_id = f.Str(data_key='.//*[contains(text(), "Family ID:")]/following-sibling::td')
    filing_date = f.Date(data_key='.//*[contains(text(), "Filed:")]/following-sibling::td')
    app_early_pub_number = f.Str('.//b[contains(text(), "Prior Publication Data")]/parent::center/following-sibling::table//tr[3]/td[2]')
    app_early_pub_date = f.Date('.//b[contains(text(), "Prior Publication Data")]/parent::center/following-sibling::table//tr[3]/td[3]')
    us_classes = USClassField('.//b[contains(text(), "Current U.S. Class")]/ancestor::tr/td[2]')
    cpc_classes = CpcClassField('.//b[contains(text(), "Current CPC Class")]/ancestor::tr/td[2]')
    intl_classes = CpcClassField('.//b[contains(text(), "Current International Class")]/ancestor::tr/td[2]')
    field_of_search = FieldOfSearchField('.//b[contains(text(), "Field of Search")]/ancestor::tr/td[2]')
    us_references = f.List(USReferenceSchema, './/center/b[text()="U.S. Patent Documents"]/parent::center/following-sibling::table[1]//tr')
    foreign_references = f.List(ForeignReferenceSchema, './/center/b[contains(text(), "Foreign Patent Documents")]/parent::center/following-sibling::table[1]//tr')
    npl_references = f.List(f.Field(), './/center/b[contains(text(), "Other References")]/ancestor::table//br/following-sibling::text()') 
    primary_examiner = ExaminerSchema('//i[contains(text(), "Primary Examiner")]/following-sibling::text()')
    assistant_examiner = ExaminerSchema('//i[contains(text(), "Assistant Examiner")]/following-sibling::text()')
    agent = f.Str('//i[contains(text(), "Attorney")]/following-sibling::coma/text()')
    claims = TextField(data_key=text_section_xpath("Claims"))
    description = TextField(data_key=text_section_xpath("Description"))
    parent_case_text = TextField(data_key=text_section_xpath("Parent Case Text"))
    related_us_applications = f.List(RelatedPatentDocumentSchema, './/*[contains(text(), "Related U.S. Patent Documents")]/ancestor::center/following::table[1]//tr[position() > 2]')
    foreign_priority = f.List(ForeignPrioritySchema, data_key='.//b[text()="Foreign Application Priority Data"]/following::table[1]//tr')
    pdf_url = f.Str('.//img[@alt="[Image]"]/parent::a/@href')

    def pre_load(self, obj):
        return ETH.fromstring(obj.encode("utf-8"))

import re
pdf_id_re = re.compile("(\d+/\d+\d+/\d+)/1.pdf")
def pdf_url_id_formatter(text):
    match = pdf_id_re.search(text)
    if match is None:
        return None
    return match.group(1)

class ImageHtmlSchema(Schema):
    pdf_url_id = f.Str(".//embed/@src", formatter=pdf_url_id_formatter)
    start_page = f.Str("//comment()[1]", formatter=lambda s: int(s.split("=")[1]))
    num_pages = f.Str("//comment()[2]", formatter=lambda s: int(s.split("=")[1]))
    sections = f.Dict(
        './/img[@src="/templates/redball.gif"]/parent::a',
        key=f.Str(),
        value=f.Str(".//@href"),
    )

    def pre_load(self, obj):
        return ETH.fromstring(obj.encode("utf-8"))
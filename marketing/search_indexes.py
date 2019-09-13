from haystack import indexes
from marketing.models import Contact


class MarketingContactIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
        document=True, use_template=True, template_name='search/contact_emails.txt')
    # title = indexes.CharField(model_attr='title')
    # authors = indexes.CharField()
    id = indexes.CharField(model_attr='id')
    email = indexes.CharField(model_attr='email')
    name = indexes.CharField(model_attr='name')
    company_name = indexes.CharField(model_attr='company_name')
    created_on = indexes.CharField(model_attr='created_on')
    created_on_arrow = indexes.CharField(model_attr='created_on_arrow')
    created_by = indexes.CharField(model_attr='created_by')
    contact_list = indexes.MultiValueField()
    contact_list_count = indexes.CharField()

    def get_model(self):
        return Contact

    def prepare_contact_list(self, obj):
        return [contact_list.name for contact_list in obj.contact_list.all()]

    def prepare_contact_list_count(self, obj):
        return obj.contact_list.count()

    # def prepare_contact_id(self, obj):
    #     return obj.id

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

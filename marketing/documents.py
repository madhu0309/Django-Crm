from django_elasticsearch_dsl import DocType, Index
from marketing.models import Contact

emails = Index('emails')

@posts.doc_type
class PostDocument(DocType):
    class Meta:
        model = Contact

        fields = [
            'name',
            'email',
        ]
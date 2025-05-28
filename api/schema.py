import graphene
from graphene_django import DjangoObjectType
from .models import TopProducts, News

class TopProductType(DjangoObjectType):
    class Meta:
        model = TopProducts
        fields = ('id', 'name', 'category', 'author', 'price', 'checked')

class NewsType(DjangoObjectType):
    class Meta:
        model = News
        fields = ('id', 'name', 'author', 'category', 'checked')

class Query(graphene.ObjectType):
    all_top_products = graphene.List(TopProductType)
    all_news = graphene.List(NewsType)

    def resolve_all_top_products(root, info):
        return TopProducts.objects.filter(checked=True)

    def resolve_all_news(root, info):
        return News.objects.filter(checked=True)

schema = graphene.Schema(query=Query)

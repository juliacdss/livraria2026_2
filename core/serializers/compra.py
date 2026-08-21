from django.db import transaction
from rest_framework.serializers import CharField, DecimalField, ModelSerializer, SerializerMethodField

from core.models import Compra, ItensCompra


#  Itens Compra
class ItensCompraCreateUpdateSerializer(ModelSerializer):
    class Meta:
        model = ItensCompra
        fields = ('livro', 'quantidade')


class ItensCompraSerializer(ModelSerializer):
    titulo = CharField(source='livro.titulo', read_only=True)
    editora = CharField(source='livro.editora.nome', read_only=True)
    preco = DecimalField(
        source='livro.preco',
        max_digits=7,
        decimal_places=2,
        read_only=True
        )
    capa = CharField(source='livro.capa.url', read_only=True)

    total = SerializerMethodField()

    def get_total(self, item):
        return item.livro.preco * item.quantidade

    class Meta:
        model = ItensCompra
        fields = ('livro', 'quantidade', 'total')
        depth = 1

# Compra


class CompraSerializer(ModelSerializer):
    usuario = CharField(source='usuario.email', read_only=True)
    status = CharField(source='get_status_display', read_only=True)
    itens = ItensCompraSerializer(many=True, read_only=True)

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'status', 'total', 'itens')


class CompraCreateUpdateSerializer(ModelSerializer):
    itens = ItensCompraCreateUpdateSerializer(many=True)

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'itens')

    @transaction.atomic
    def create(self, validated_data):
        itens_data = validated_data.pop('itens')
        compra = Compra.objects.create(**validated_data)
        for item_data in itens_data:
            ItensCompra.objects.create(compra=compra, **item_data)
        compra.save()
        return compra

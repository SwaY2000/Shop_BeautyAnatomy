import sys

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone

from PIL import Image

from io import BytesIO

from CONFIG.NAME_EXCEPTION import MinResolutionErrorException, MaxResolutionErrorException

from django.urls import reverse

User = get_user_model()

def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})

def get_models_for_count(*models_name):
    return [models.Count(model_name) for model_name in models_name]

class LastestProductsManager:

    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        print(*args)
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            print(ct_model)
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)

        if with_respect_to:
            ct_model = ContentType.objects.filter(model__in=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(
                        products, key=lambda x: x.__class__.meta.model_name.startwith(with_respect_to), reverse=True
                    )
        return products

class LatestProducts:

    objects = LastestProductsManager()

class CategoryManager(models.Manager):

    CATEGORY_NAME_FOR_COUNT = { #Must be real name category
        "Philip Martin's": 'philipmartins__count',
        "American Crew": 'americancrew__count'
    }

    def get_queryset(self):
        return super().get_queryset()

    def get_categories_for_left_sidebar(self):
        models = get_models_for_count('philipmartins', 'americancrew') #which category
        qs = list(self.get_queryset().annotate(*models))
        print(qs)
        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAME_FOR_COUNT[c.name]))
            for c in qs
        ]
        return data

class Category(models.Model):

    name = models.CharField(max_length=255, verbose_name='Имя категории')
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

class Product(models.Model):

    VALID_RESOLUTION = {'min': 400, 'max': 2000}

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Наименование')
    mini_description = models.TextField(max_length=255, verbose_name='Краткое описание', null=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение товара')
    description = models.TextField(verbose_name='Описание', null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')
    country = models.CharField(max_length=255, verbose_name='Страна производитель')
    type_product = models.CharField(max_length=255, verbose_name='Тип продукции') #like shampoo, creme
    volume = models.CharField(max_length=255, verbose_name='Объем')
    availibility = models.CharField(max_length=20, verbose_name='Наличие', null=True)

    def __str__(self):
        return self.title

    def get_model_name(self):
        return self.__class__.__name__.lower()

class AmericanCrew(Product):
    # Abstract method for American Crew`s goods
    gender = models.CharField(max_length=15, verbose_name='Гендер')

    def __str__(self):
        return '{} : {}'.format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'single-product')

class PhilipMartins(Product):

    gender = models.CharField(max_length=15, verbose_name='Гендер')

    def __str__(self):
        return '{} : {}'.format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'single-product')

class CartProduct(models.Model):

    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
    #Microframework contenttype, it looks all models
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    #
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')

    def __str__(self):
        return 'Продукт {} (для корзины)'.format(self.content_object.title)

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)

class Cart(models.Model):

    owner = models.ForeignKey('Customer', null=True, verbose_name='Владелец корзины', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=28, verbose_name='Номер телефона', null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name='Адрес', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Заказы покупателя', related_name='related_customer')

    def __str__(self):
        return 'Покупатель: {} {}'.format(self.user.first_name, self.user.last_name)

class Order(models.Model):

    STATUS_NEW = 'new'
    STATUS_IN_PROCESS = 'in_process'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROCESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ выполнен')
    )

    BUYING_TYPE_SELF = 'self'
    BUYNG_TYPE_DELEVERY = 'delivery'
    BUYNG_TYPE_COURIER = 'courier'

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYNG_TYPE_DELEVERY, 'Почта'),
        (BUYNG_TYPE_COURIER, 'Курьер')
    )

    PAYMENT_ON_DELIVERY = 'payment_delivery'
    FULL_PAYMENT_ON_CARD = 'full_payment'

    PAYMENT_TYPE_CHOICES = (
        (PAYMENT_ON_DELIVERY, 'Наложенный платеж'),
        (FULL_PAYMENT_ON_CARD, 'Полная предоплата')
    )

    customer = models.ForeignKey(Customer, verbose_name='Покупатель', related_name='related_orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone_number = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.CharField(max_length=1024, verbose_name='Адресс', null=True, blank=True)
    status = models.CharField(max_length=100, verbose_name='Статус заказа', choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(max_length=100, verbose_name='Тип доставки', choices=BUYING_TYPE_CHOICES, default=BUYING_TYPE_SELF)
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')
    order_date = models.DateField(verbose_name='Дата получения заказа', default=timezone.now)
    payment_type = models.CharField(max_length=100, verbose_name='Способ оплаты', choices=PAYMENT_TYPE_CHOICES, default=PAYMENT_ON_DELIVERY)
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.id)


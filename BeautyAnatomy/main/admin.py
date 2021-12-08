from django.contrib import admin
from django import forms
from django.forms import ModelChoiceField, ModelForm
from django.utils.safestring import mark_safe

from .models import *

from PIL import Image

from CONFIG.NAME_EXCEPTION import MinResolutionErrorException, MaxResolutionErrorException

from CONFIG.CONFIG_FOR_SITE import VALID_RESOLUTION


class AmericanCrewCategoryChoiceField(forms.ModelChoiceField):
    pass

class AmericanCrewAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='AmericanCrew'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class PhilipMartinsCategoryChoiceField(forms.ModelChoiceField):
    pass


class PhilipMartinsAdminForm(ModelForm):
    # VALID_RESOLUTION = {'min': 400, 'max': 2000}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].help_text = mark_safe('<span style="color:red">*Минимальный размер изображения {}x{}/' \
                                         'Максимальный размер изображения {}x{}</span>'.format(
            VALID_RESOLUTION.get('min'),
            VALID_RESOLUTION.get('min'),
            VALID_RESOLUTION.get('max'),
            VALID_RESOLUTION.get('max')
        ))

    # def clean_image(self):
    #     image = self.cleaned_data['image']
    #     img = Image.open(image)
    #     if img.width < self.VALID_RESOLUTION.get('min') or img.height < self.VALID_RESOLUTION.get('min'):
    #         raise MinResolutionErrorException('Разрешение меньше минимального')
    #     elif img.width > self.VALID_RESOLUTION.get('max') or img.height > self.VALID_RESOLUTION.get('max'):
    #         raise MaxResolutionErrorException('Разрешение больше максимального')
    #     return image


class PhilipMartinsAdmin(admin.ModelAdmin):

    form = PhilipMartinsAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='PhilipMartins'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)




admin.site.register(Category)
admin.site.register(AmericanCrew, AmericanCrewAdmin)
admin.site.register(PhilipMartins, PhilipMartinsAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(Order)

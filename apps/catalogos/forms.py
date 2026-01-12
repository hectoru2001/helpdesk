from django import forms
from apps.ordenes.models import Aplicaciones, Clasificaciones, Marcas, Colores

ESTATUS_CHOICES = (
    (1, 'Activo'),
    (0, 'Inactivo'),
)


class AplicacionForm(forms.ModelForm):
    estatus = forms.ChoiceField(
        choices=ESTATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    class Meta:
        model = Aplicaciones
        fields = ['descripcion', 'estatus']
        widgets = {
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la aplicación'
            }),
        }


class ClasificacionForm(forms.ModelForm):
    estatus = forms.ChoiceField(
        choices=ESTATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    class Meta:
        model = Clasificaciones
        fields = ['descripcion', 'estatus']
        widgets = {
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la clasificación'
            }),
        }

class MarcaForm(forms.ModelForm):
    estatus = forms.ChoiceField(
        choices=ESTATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    class Meta:
        model = Marcas
        fields = ['marca', 'estatus']
        widgets = {
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de la marca'
            }),
        }

class ColorForm(forms.ModelForm):
    estatus = forms.ChoiceField(
        choices=ESTATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    class Meta:
        model = Colores
        fields = ['color', 'estatus']
        widgets = {
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del color'
            }),
        }
from django import forms
from apps.ordenes.models import Aplicaciones, Clasificaciones


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

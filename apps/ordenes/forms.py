from .models import *
from django import forms
from django.contrib.auth.models import User

class BootstrapMixin:    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })
            if field.widget.__class__.__name__ == 'CheckboxInput':
                field.widget.attrs['class'] = 'form-check-input'
            elif field.widget.__class__.__name__ == 'RadioSelect':
                field.widget.attrs['class'] = 'form-check-input'


class OrdenForm(BootstrapMixin, forms.ModelForm):
    usuarios_asignados = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by('username'),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',   
            'size': '6',              
        }),
        required=False,
        label="Asignar a usuarios"
    )



    class Meta:
        model = Orden
        fields = '__all__'
        widgets = {
            'prioridad': forms.Select(choices=[
                ('minima', 'Minima'),
                ('normal', 'Normal'),
                ('programada', 'Programada'),
                ('urgente', 'Urgente'),
                ('inmediata', 'Inmediata'),
            ]),
            'descripcion': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['aplicacion'].queryset = Aplicaciones.objects.order_by('descripcion')
        self.fields['problema'].queryset = Problemas.objects.order_by('descripcion')
        self.fields['clasificacion'].queryset = Clasificaciones.objects.order_by('descripcion')

class EquipoXOrdenForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = EquipoXOrden
        exclude = ['orden'] 
        fields = '__all__'

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            self.fields['marca'].queryset = Marcas.objects.order_by('marca')
            self.fields['color'].queryset = Colores.objects.order_by('color')
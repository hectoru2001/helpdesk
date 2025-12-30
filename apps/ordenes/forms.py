from .models import *
from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory

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

class UsuarioActivoMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, u):
        tipo = u.extra.get_tipo_display() if hasattr(u, "extra") else "N/A"
        nombre = f"{u.first_name} {u.last_name}".strip()
        return f"{nombre} - [{tipo}]"

class OrdenForm(BootstrapMixin, forms.ModelForm):

    usuarios_asignados = UsuarioActivoMultipleChoiceField(
        queryset=User.objects.none(),  
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
        self.fields['clasificacion'].queryset = Clasificaciones.objects.order_by('descripcion')

        self.fields['usuarios_asignados'].queryset = (
            User.objects.filter(extra__estatus="A")
            .order_by("first_name", "last_name")
        )

    def clean_usuarios_asignados(self):
        usuarios = self.cleaned_data.get("usuarios_asignados")

        if not usuarios:
            raise forms.ValidationError("Debes seleccionar al menos un usuario.")

        return usuarios

class OrdenxArchivoForm(forms.ModelForm):
    class Meta:
        model = OrdenxArchivo
        fields = ['archivo', 'descripcion']
        widgets = {
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EquipoXOrdenForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = EquipoXOrden
        exclude = ['orden'] 
        fields = '__all__'

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
            self.fields['marca'].queryset = Marcas.objects.order_by('marca')
            self.fields['color'].queryset = Colores.objects.order_by('color')

class UsuariosxOrdenForm(forms.Form):
    usuarios_asignados = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by("first_name"),
        widget=forms.SelectMultiple(attrs={
            "class": "form-select",
            "size": "6",
        }),
        required=False,
        label="Asignar a usuarios"
    )

class OrdenArchivoForm(forms.ModelForm):
    class Meta:
        model = OrdenxArchivo
        fields = ['archivo']

class SolicitantexOrdenForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = SolicitantexOrden
        exclude = ['orden']
        fields = '__all__'

class EditarOrdenForm(forms.ModelForm):
    class Meta:
        model = Orden
        fields = [
            'oficio',
            'telefono',
            'aplicacion',
            'clasificacion',
            'descripcion',
            'solucion',
            'prioridad',
            'equipo',
            'captura',
            'estatus',
            'capacitacion',
            'capacitacion_descripcion',
            'fecha_inicio',
            'fecha_terminado'
        ]
        
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Descripción detallada del problema'
            }),
            'solucion': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Solución aplicada'
            }),
            'capacitacion_descripcion': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control'
            }),
            'fecha_inicio': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'format': '%Y-%m-%dT%H:%M'
            }),
            'fecha_terminado': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'format': '%Y-%m-%dT%H:%M'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
            }),
            'oficio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de oficio'
            }),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'estatus': forms.Select(attrs={'class': 'form-control'}),
            'capacitacion': forms.TextInput(attrs={'class': 'form-control'}),
            'captura': forms.NumberInput(attrs={'class': 'form-control'}),
            'equipo': forms.CheckboxInput(attrs={'class': 'form-check-input', 'checked':True}),
            'aplicacion': forms.Select(attrs={'class': 'form-control'}),
            'clasificacion': forms.Select(attrs={'class': 'form-control'}),
            'usuario_solicita': forms.NumberInput(attrs={'class': 'form-control'}),
            'usuario_beneficiado': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
        labels = {
            'usuario_solicita': 'ID Usuario Solicita',
            'usuario_beneficiado': 'ID Usuario Beneficiado',
            'captura': 'ID Captura',
            'capacitacion_descripcion': 'Descripción de Capacitación',
        }

class UsuariosxOrdenForm(forms.ModelForm):
    class Meta:
        model = UsuariosxOrden
        fields = '__all__'
        widgets = {
            'comentarios': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'inicia': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'termina': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'realiza': forms.Select(attrs={'class': 'form-control'}),
            'asigna': forms.Select(attrs={'class': 'form-control'}),
            'estatus_orden': forms.Select(attrs={'class': 'form-control'}),
            'estatus': forms.Select(attrs={'class': 'form-control'}),
            'causa': forms.TextInput(attrs={'class': 'form-control'}),
            'etiquetas': forms.TextInput(attrs={'class': 'form-control'}),
        }
        exclude = ['orden']  # El foreign key se maneja automáticamente

class EquipoXOrdenForm(forms.ModelForm):
    class Meta:
        model = EquipoXOrden
        fields = '__all__'
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'equipo': forms.TextInput(attrs={'class': 'form-control'}),
            'patrimonio': forms.TextInput(attrs={'class': 'form-control'}),
            'serie': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.Select(attrs={'class': 'form-control'}),
            'entregado_foraneo': forms.Select(attrs={'class': 'form-control'}),
        }
        exclude = ['orden', 'observaciones', 'salida', 'nombre_resguardante', 'area_resguardante']

class SolicitantexOrdenForm(forms.ModelForm):
    class Meta:
        model = SolicitantexOrden
        fields = '__all__'
        widgets = {
            'nombre_beneficiado': forms.TextInput(attrs={'class': 'form-control'}),
            'puesto_beneficiado': forms.TextInput(attrs={'class': 'form-control'}),
            'dependencia_beneficiado': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_beneficiado': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono_beneficiado': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_solicitante': forms.TextInput(attrs={'class': 'form-control'}),
            'puesto_solicitante': forms.TextInput(attrs={'class': 'form-control'}),
            'dependencia_solicitante': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_solicitante': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono_solicitante': forms.TextInput(attrs={'class': 'form-control'}),
        }
        exclude = ['orden']

# Crear los formsets
SolicitantexOrdenFormSet = inlineformset_factory(
    Orden,
    SolicitantexOrden,
    form=SolicitantexOrdenForm,
    can_delete=True,
    can_delete_extra=True
)

EquipoXOrdenFormSet = inlineformset_factory(
    Orden,
    EquipoXOrden,
    form=EquipoXOrdenForm,
    extra=0,
    can_delete=True,
    can_delete_extra=True
)

UsuariosxOrdenFormSet = inlineformset_factory(
    Orden,
    UsuariosxOrden,
    form=UsuariosxOrdenForm,
    can_delete=True,
    can_delete_extra=True
)
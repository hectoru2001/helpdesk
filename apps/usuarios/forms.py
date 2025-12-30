from django import forms
from django.contrib.auth.models import User
from .models import ExtraUsuarios
from apps.ordenes.forms import BootstrapMixin

class UsuarioCompletoForm(BootstrapMixin, forms.ModelForm):

    TIPO_CHOICES = [
        ('P', 'Programador'),
        ('T', 'Técnico'),
        ('A', 'Administrador'),
    ]

    tipo = forms.ChoiceField(choices=TIPO_CHOICES, widget=forms.Select())
    empleado = forms.IntegerField()
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def __init__(self, *args, **kwargs):
        self.extra = kwargs.pop('extrausuario', None)
        super().__init__(*args, **kwargs)

        if self.extra:
            self.fields['empleado'].initial = self.extra.empleado
            self.fields['tipo'].initial = self.extra.tipo

    def clean_empleado(self):
        empleado = self.cleaned_data['empleado']
        qs = ExtraUsuarios.objects.filter(empleado=empleado)
        if self.extra:
            qs = qs.exclude(pk=self.extra.pk)

        if qs.exists():
            raise forms.ValidationError("Este número de empleado ya existe.")

        return empleado

    def save(self, commit=True):
        user = super().save(commit=False)

        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user

    def save_extra(self):
        extra = self.extra or ExtraUsuarios(usuario=self.instance)
        extra.empleado = self.cleaned_data['empleado']
        extra.tipo = self.cleaned_data['tipo']
        extra.save()
        return extra

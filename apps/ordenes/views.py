import json
import os
from datetime import datetime

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q, Prefetch
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.utils.decorators import method_decorator
from io import BytesIO
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy

from .models import Orden, UsuariosxOrden
from .forms import *
from core.decorators.permisos import administrador_required
from apps.calificaciones.views import generar_url_comentario
from apps.calificaciones.models import TokenComentario

from apps.usuarios.models import ExtraUsuarios
from apps.notificaciones.views import Notificar, notificaciones_activadas, obtener_correos_orden, obtener_correo_usuario
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

@method_decorator(administrador_required(False), name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class OrdenCreateTicket(CreateView):
    model = Orden
    form_class = OrdenForm
    template_name = 'nueva_orden.html'
    success_url = '/inicio/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_equipo'] = EquipoXOrdenForm()
        context['form_solicitante'] = SolicitantexOrdenForm()
        return context

    def post(self, request, *args, **kwargs):
        form_orden = OrdenForm(request.POST)
        form_equipo = EquipoXOrdenForm(request.POST)
        form_solici = SolicitantexOrdenForm(request.POST)
        archivos = request.FILES.getlist('archivos')

        # === VALIDAR ORDEN ===
        if not form_orden.is_valid():
            for campo, errores in form_orden.errors.items():
                for err in errores:
                    messages.error(request, f"{campo}: {err}")
            return self.render_to_response(self.get_context_data())

        orden = form_orden.save()

        # === SOLICITANTE ===
        if form_solici.is_valid():
            sol = form_solici.save(commit=False)
            sol.orden = orden
            sol.save()

        # === EQUIPO ===
        if form_equipo.is_valid():
            equipo = form_equipo.save(commit=False)
            equipo.orden = orden
            equipo.save()

        for a in archivos:
            OrdenxArchivo.objects.create(
                orden=orden,
                archivo=a,
                descripcion="",
            )

        usuarios = form_orden.cleaned_data.get("usuarios_asignados", [])

        for user in usuarios:
            try:
                UsuariosxOrden.objects.create(
                    orden=orden,
                    asigna=request.user,
                    realiza=user,
                    estatus="A",
                    estatus_orden="A",
                )

                if notificaciones_activadas(user.id):
                    Notificar.crear(
                        usuario=user,
                        mensaje=f"Has sido asignado a la orden #{orden.orden}.",
                        tipo="task"
                    )

                    Notificar.correo_html(
                        obtener_correo_usuario(user.id),
                        "Has sido asignado a una nueva orden",
                        "correos/orden_asignada.html",
                        contexto={
                            "usuario": user.get_full_name(),
                            "orden_id": orden.orden,
                            "resumen": orden.descripcion,
                            "url": request.build_absolute_uri(f"/ordenes/ordenes/"),
                        }
                    )

                email_user = obtener_correos_orden(orden.orden)
                print(f"Emails para nueva orden: {email_user}")
                contexto_email = {
                    "orden_id": orden.orden,
                    "nombre_usuario": (
                        form_solici.cleaned_data.get("nombre_beneficiado", "Usuario")
                        if form_solici.is_valid()
                        else "Usuario"
                    ),
                    "resumen": orden.descripcion,
                    "fecha_creacion": orden.fecha_captura,
                }

                Notificar.correo_html(
                    email_user,
                    "Nueva orden creada",
                    "correos/orden_nueva.html",
                    contexto_email
                )

            except Exception as e:
                print(f"Error asignando {user.username}: {e}")
                messages.error(request, f"No se pudo asignar a {user.username}")

        messages.success(request, "La orden se creó correctamente.")
        return redirect(self.success_url)

@method_decorator(administrador_required(True), name='dispatch')
class ListaOrdenes(ListView):
    model = Orden
    template_name = 'lista_ordenes.html'
    context_object_name = 'ordenes'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()

        q = self.request.GET.get('q')
        tipo = self.request.GET.get('tipo', 'orden')
        estatus = self.request.GET.get('estatus')
        prioridad = self.request.GET.get('prioridad')

        if q:
            if tipo == 'oficio':
                qs = qs.filter(oficio__icontains=q)
            elif tipo == 'dependencia':
                qs = qs.filter(solicitantes__dependencia_solicitante__icontains=q)
            else:
                qs = qs.filter(orden__icontains=q)

        if estatus:
            qs = qs.filter(estatus=estatus)

        if prioridad:
            qs = qs.filter(prioridad=prioridad)

        return qs.order_by('-fecha_captura')

@method_decorator(administrador_required(False), name='dispatch')
class DetallesOrdenes(DetailView):
    model = Orden
    template_name = 'detalle_orden.html'
    context_object_name = 'orden'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orden = self.get_object()

        # 🔹 Comentario
        comentario = TokenComentario.objects.filter(
            orden=orden,
            usado=True
        ).order_by('-creado').first()

        context['comentario'] = comentario

        if comentario and comentario.calificacion:
            estrellas = "★" * comentario.calificacion + "☆" * (5 - comentario.calificacion)
            context['estrellas'] = estrellas
        else:
            context['estrellas'] = None

        archivos_validos = []
        for a in orden.archivos.all():
            try:
                if a.archivo and os.path.exists(a.archivo.path):
                    archivos_validos.append(a)
            except Exception:
                continue

        context['archivos_validos'] = archivos_validos
        context['archivos_count'] = len(archivos_validos)

        return context

@method_decorator(administrador_required(True), name='dispatch')
class EditarOrden(UpdateView):
    model = Orden
    form_class = EditarOrdenForm  # Usamos el nuevo formulario
    template_name = 'editar_orden.html'
    
    def get_success_url(self):
        return reverse_lazy('lista_ordenes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orden = self.object
        
        # Configurar prefijos únicos para cada formset
        if self.request.POST:
            context['solicitantes_formset'] = SolicitantexOrdenFormSet(
                self.request.POST, 
                instance=orden,
                prefix='solicitantes'
            )
            context['equipos_formset'] = EquipoXOrdenFormSet(
                self.request.POST,
                instance=orden,
                prefix='equipos'
            )
        else:
            context['solicitantes_formset'] = SolicitantexOrdenFormSet(
                instance=orden,
                prefix='solicitantes'
            )
            context['equipos_formset'] = EquipoXOrdenFormSet(
                instance=orden,
                prefix='equipos'
            )
        
        # Información adicional para el template
        context['titulo'] = f'Editar Orden #{orden.orden}'
        context['orden'] = orden
        
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        solicitantes_fs = context['solicitantes_formset']
        equipos_fs = context['equipos_formset']

        if (
            solicitantes_fs.is_valid() and
            equipos_fs.is_valid()
        ):
            self.object = form.save(commit=False)
            self.object.equipo = True
            self.object.save()

            solicitantes_fs.instance = self.object
            solicitantes_fs.save()

            equipos_fs.instance = self.object
            equipos_fs.save()

            messages.success(self.request, 'Orden actualizada correctamente.')
            return super().form_valid(form)


        return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data()

        print('--- FORM ORDEN ---')
        print(form.errors)

        print('--- EQUIPOS NON FORM ERRORS ---')
        print(context['equipos_formset'].non_form_errors())

        print('--- EQUIPOS ERRORS ---')
        for i, f in enumerate(context['equipos_formset'].forms):
            print(i, f.errors)

        print('--- POST KEYS ---')
        for k in sorted(self.request.POST.keys()):
            print(k)

        return super().form_invalid(form)

@method_decorator(administrador_required(True), name='dispatch')
class DuplicarOrden(View):

    template_name = "duplicar_orden.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        numero_orden = request.POST.get("orden")

        if not numero_orden:
            messages.error(request, "Debes ingresar un número de orden.")
            return render(request, self.template_name)

        orden = Orden.objects.filter(orden=numero_orden).first()

        if not orden:
            messages.error(request, "La orden no existe.")
            return render(request, self.template_name)

        nueva_orden = duplicar_orden(orden)

        messages.success(
            request,
            f"Orden duplicada correctamente. Nueva orden #{nueva_orden.orden}"
        )

        return redirect("lista_ordenes")

@method_decorator(administrador_required(True), name='dispatch')
class Agregar_Equipo(CreateView):
    model = EquipoXOrden
    form_class = EquipoXOrdenForm  # Asegúrate de usar el Form, no el Model
    template_name = 'editar/editar_equipos.html'

    def get_success_url(self):
        return reverse_lazy('editar_orden', kwargs={'pk': self.kwargs['orden_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orden_id = self.kwargs.get('orden_id')
        context['orden'] = Orden.objects.get(pk=orden_id)
        return context

    def form_valid(self, form):
        orden_id = self.kwargs.get('orden_id')
        orden = Orden.objects.get(pk=orden_id)
        form.instance.orden = orden
        return super().form_valid(form)

@method_decorator(administrador_required(True), name='dispatch')
class Agregar_Archivos(CreateView):
    model = OrdenxArchivo
    form_class = OrdenxArchivoForm
    template_name = 'editar/editar_archivos.html'

    def dispatch(self, request, *args, **kwargs):
        self.orden = get_object_or_404(Orden, pk=kwargs['orden_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.orden = self.orden
        messages.success(self.request, 'Archivo agregado correctamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('agregar_archivos', kwargs={'orden_id': self.orden.orden})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orden'] = self.orden
        context['archivos'] = self.orden.archivos.all()
        return context

@method_decorator(administrador_required(True), name='dispatch')
class EliminarArchivoOrden(View):

    def post(self, request, pk):
        archivo = get_object_or_404(OrdenxArchivo, pk=pk)
        orden_id = archivo.orden.orden

        # borrar archivo físico
        if archivo.archivo and os.path.isfile(archivo.archivo.path):
            os.remove(archivo.archivo.path)

        archivo.delete()
        messages.success(request, 'Archivo eliminado correctamente.')

        return redirect('agregar_archivos', orden_id=orden_id)

@method_decorator(administrador_required(False), name='dispatch')
class OrdenesView(TemplateView):
    template_name = "asignar_ordenes.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        try:
            extra = ExtraUsuarios.objects.get(usuario_id=user)
            tipo_usuario = extra.tipo
        except ExtraUsuarios.DoesNotExist:
            tipo_usuario = "T"

        # 🔹 NUEVO: filtro para mostrar terminadas
        mostrar_terminadas = self.request.GET.get('estatus', 'no')

        # 🔹 Base: nunca mostrar canceladas
        ordenes = Orden.objects.exclude(estatus='C')

        # 🔹 Solo excluir terminadas si el usuario dice NO
        if mostrar_terminadas == 'no':
            ordenes = ordenes.exclude(estatus='T')

        ordenes = ordenes.order_by('-fecha_captura')

        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')

        if fecha_inicio and fecha_fin:
            ordenes = ordenes.filter(
                fecha_captura__date__range=[fecha_inicio, fecha_fin]
            )

        mostrar_todas = self.request.GET.get('todas')

        ordenes_a_mostrar = ordenes.filter(
            usuarios_orden__realiza=user
        ).distinct()

        if mostrar_todas == 'no':
            ordenes_a_mostrar = ordenes

        paginator = Paginator(ordenes_a_mostrar, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context["ordenes"] = page_obj
        context["page_obj"] = page_obj
        context["paginator"] = paginator
        context["is_paginated"] = page_obj.has_other_pages()

        context['fecha_inicio'] = fecha_inicio
        context['fecha_fin'] = fecha_fin
        context['mostrar_todas'] = mostrar_todas
        context['mostrar_terminadas'] = mostrar_terminadas

        return context

@method_decorator(administrador_required(True), name='dispatch')
class EstadoUsuariosView(TemplateView):
    template_name = 'estados/estado_usuarios.html'

    def get_context_data(self, user_id=None, **kwargs):
        context = super().get_context_data(**kwargs)

        request = self.request

        q = request.GET.get("q", "").strip()
        tipo = request.GET.get("tipo", "").strip()

        fecha_inicio = request.GET.get("fecha_inicio")
        fecha_fin = request.GET.get("fecha_fin")
        estatus_orden = request.GET.get("estatus")

        usuarios = (
            User.objects
            .select_related("extra")
            .prefetch_related("usuariosxorden_set__orden")
            .filter(extra__estatus="A")
        )

        if user_id:
            usuarios = usuarios.filter(id=user_id)

        if q:
            usuarios = usuarios.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(username__icontains=q) |
                Q(extra__empleado__icontains=q)
            )

        if tipo:
            usuarios = usuarios.filter(extra__tipo=tipo)

        if not usuarios.exists():
            context["usuarios"] = []
            return context

        contexto_usuarios = []

        for u in usuarios:
            asignaciones = u.usuariosxorden_set.select_related("orden")

            # Filtros de órdenes
            if estatus_orden:
                asignaciones = asignaciones.filter(orden__estatus=estatus_orden)

            if fecha_inicio:
                asignaciones = asignaciones.filter(orden__fecha__date__gte=fecha_inicio)

            if fecha_fin:
                asignaciones = asignaciones.filter(orden__fecha__date__lte=fecha_fin)

            pendientes = asignaciones.filter(orden__estatus="A").count()
            iniciadas = asignaciones.filter(orden__estatus="E").count()
            terminadas = asignaciones.filter(orden__estatus="T").count()

            contexto_usuarios.append({
                "usuario": u,
                "tipo": u.extra.get_tipo_display(),
                "total": asignaciones.count(),
                "pendientes": pendientes,
                "iniciadas": iniciadas,
                "terminadas": terminadas,
                "ordenes": asignaciones.filter(
                    orden__estatus__in=["A", "E", "T"]
                ).order_by("-orden__fecha_captura"),
            })

        context["usuarios"] = contexto_usuarios

        context["filtros"] = {
            "q": q,
            "tipo": tipo,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "estatus": estatus_orden,
        }

        return context

@method_decorator(administrador_required(False), name='dispatch')
class OrdenesPorUsuarioView(ListView):
    model = Orden
    template_name = "ordenes_por_usuario.html"
    context_object_name = "ordenes"

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return Orden.objects.filter(
            usuarios_orden__realiza_id=user_id
        ).order_by("-fecha_captura")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["usuario_obj"] = User.objects.get(id=self.kwargs["user_id"])
        return context

# === Endpionts === #
@administrador_required(True)
def eliminar_orden(request, pk):
    orden = get_object_or_404(Orden, orden=pk)

    if orden.estatus == 'T':
        messages.warning(
            request,
            f'La orden #{pk} está terminada y no puede ser eliminada.'
        )
        return redirect('lista_ordenes')

    try:
        with transaction.atomic():
            orden.solicitantes.all().delete()
            orden.equipos.all().delete()
            orden.usuarios_orden.all().delete()
            orden.delete()

        messages.success(
            request,
            f'La orden #{pk} ha sido eliminada correctamente.'
        )

    except IntegrityError:
        messages.error(
            request,
            f'No se pudo eliminar la orden #{pk}.'
        )
    except Exception as e:
        messages.error(
            request,
            f'Error inesperado: {str(e)}'
        )

    return redirect('lista_ordenes')

def detalle_orden_api(request, pk):
    orden = get_object_or_404(Orden, pk=pk)

    solicitante = orden.solicitantes.first()
    equipo = orden.equipos.first()
    comentario = orden.comentario.first()

    usuario_orden = UsuariosxOrden.objects.filter(
        orden=orden,
        realiza=request.user,
    ).first()


    # 🔹 CAMBIO: Obtener todos los usuarios asignados a esta orden
    asignaciones = UsuariosxOrden.objects.filter(orden=orden).select_related('realiza')

    # Creamos una lista con los detalles de cada solución/técnico
    soluciones_detalladas = []
    for asig in asignaciones:
        soluciones_detalladas.append({
            "usuario": asig.realiza.get_full_name() or asig.realiza.username,
            "estatus": asig.estatus,
            "solucion": asig.solucion if asig.solucion else "",
            "comentarie": asig.comentarios if hasattr(asig, 'comentarios') else ""
        })

    data = {
        "orden": orden.orden,
        "oficio": getattr(orden, "oficio", ""),
        "prioridad": orden.prioridad.capitalize(),
        "aplicacion": str(orden.aplicacion) if hasattr(orden, "aplicacion") else "",
        "clasificacion": str(orden.clasificacion) if hasattr(orden, "clasificacion") else "",
        "descripcion": orden.descripcion,
        "estatus": orden.get_estatus_display(),
        "solucion_general": orden.solucion if orden.solucion else "",

        # 🔹 NUEVA ESTRUCTURA: Lista de soluciones de todos los usuarios
        "todas_las_soluciones": soluciones_detalladas,
        "estatus_usuario": usuario_orden.estatus if usuario_orden else None,
        "equipo": "true" if equipo else "false",
        "detalle_equipo": {
            "equipo": equipo.equipo if equipo else "",
            "marca": str(equipo.marca) if equipo else "",
            "color": str(equipo.color) if equipo else "",
            "serie": equipo.serie if equipo else "",
            "descripcion": equipo.descripcion if equipo else "",
            "patrimonio": equipo.patrimonio if equipo else "",
        },
        "solicitante": {
            "nombre": solicitante.nombre_solicitante if solicitante else "",
            "puesto": solicitante.puesto_solicitante if solicitante else "",
            "dependencia": solicitante.dependencia_solicitante if solicitante else "",
            "correo": solicitante.correo_solicitante if solicitante else "",
            "telefono": solicitante.telefono_solicitante if solicitante else "",
        },
        "beneficiado": {
            "nombre": solicitante.nombre_beneficiado if solicitante else "",
            "puesto": solicitante.puesto_beneficiado if solicitante else "",
            "dependencia": solicitante.dependencia_beneficiado if solicitante else "",
            "correo": solicitante.correo_beneficiado if solicitante else "",
            "telefono": solicitante.telefono_beneficiado if solicitante else "",
        },
        "comentario": {
            "calificacion": comentario.calificacion if comentario else "",
            "comentario": comentario.comentario if comentario else "",
        }
    }

    return JsonResponse(data)

def actualizar_estatus_api(request):
    orden_id = request.POST.get("orden_id")
    estatus = request.POST.get("estatus")
    solucion = request.POST.get("solucion", "").strip()

    if not orden_id or not estatus:
        return JsonResponse({"success": False, "error": "Datos incompletos"})

    try:
        orden = Orden.objects.get(orden=orden_id)
    except Orden.DoesNotExist:
        return JsonResponse({"success": False, "error": "Orden no encontrada"})

    usuario_orden = (
        UsuariosxOrden.objects
        .filter(
            orden=orden,
            realiza=request.user
        )
        .order_by('-inicia')   # el más reciente
        .first()
    )

    if not usuario_orden:
        return JsonResponse({
            "success": False,
            "error": "No estás asignado activo a esta orden"
        })

    # =======================
    # INICIAR
    # =======================
    if estatus == "E":
        usuario_orden.inicia = timezone.now()
        usuario_orden.estatus = "E"
        usuario_orden.save(update_fields=['inicia', 'estatus'])

        orden.estatus = "E"
        orden.save(update_fields=['estatus'])

        return JsonResponse({"success": True, "estatus": "E"})

    # =======================
    # TERMINAR
    # =======================
    if estatus == "T":
        if not solucion:
            return JsonResponse({
                "success": False,
                "error": "Debes escribir la solución para terminar la orden"
            })

        usuario_orden.termina = timezone.now()
        usuario_orden.estatus = "T"
        usuario_orden.solucion = solucion
        usuario_orden.save(update_fields=['termina', 'estatus', 'solucion'])

        # ---- VALIDACIÓN GLOBAL ----
        total_asignados = UsuariosxOrden.objects.filter(
            orden=orden, estatus='A'
        ).count()

        total_terminados = UsuariosxOrden.objects.filter(
            orden=orden,
            estatus='A',
            estatus_orden="T"
        ).count()

        if total_asignados == total_terminados:
            orden.estatus = "T"
            orden.solucion = solucion
            orden.fecha_terminado = timezone.now()
            orden.save()

            correos = obtener_correos_orden(orden_id)
            url_comentario = generar_url_comentario(request, orden)

            Notificar.enviar_notificacion_orden(
                orden_id,
                correos,
                "terminada",
                contexto={
                    "orden_id": orden_id,
                    "fecha_terminado": orden.fecha_terminado,
                    "solucion": solucion,
                    "url": url_comentario
                }
            )

            return JsonResponse({
                "success": True,
                "estatus": "T",
                "msg": "Orden finalizada por todos"
            })

        return JsonResponse({
            "success": True,
            "estatus": "PT",
            "msg": "Tú terminaste, otros usuarios siguen"
        })

    return JsonResponse({"success": False, "error": "Estatus no válido"})

def formatear(fecha):
    if not fecha:
        return ""
    return fecha.strftime("%d/%m/%Y %H:%M")

def draw_text_in_box(p, text, x, y, width, height, font="Helvetica", size=9, leading=11):
    p.setFont(font, size)
    lines = simpleSplit(text or "", font, size, width)

    max_lines = int(height / leading)
    lines = lines[:max_lines]

    text_obj = p.beginText(x, y)
    text_obj.setLeading(leading)

    for line in lines:
        text_obj.textLine(line)

    p.drawText(text_obj)

def imprimir_orden(request, orden_id):
    orden = get_object_or_404(Orden, orden=orden_id)
    num_emp = getattr(request.user.extra, "empleado", "N/A")
    username_usuario = request.user.username
    nombre_usuario = request.user.get_full_name()
    soluciones_tecnicos = UsuariosxOrden.objects.filter(orden=orden).select_related('realiza')

    # --- funciones auxiliares ---
    def draw_label_value(p, x, y, label, value, max_width=None):
        p.setFont("Helvetica-Bold", 9)
        label_width = p.stringWidth(label, "Helvetica-Bold", 9)
        p.drawString(x, y, label)
        p.setFont("Helvetica", 9)
        
        if max_width:
            available_width = max_width - label_width - 10
            lines = []
            words = str(value).split()
            current_line = []
            current_width = 0
            
            for word in words:
                word_width = p.stringWidth(word + " ", "Helvetica", 9)
                if current_width + word_width <= available_width:
                    current_line.append(word)
                    current_width += word_width
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                    current_width = word_width
            if current_line:
                lines.append(" ".join(current_line))
            
            for i, line in enumerate(lines):
                p.drawString(x + label_width + 5, y - (i * 12), line)
            return len(lines)
        else:
            p.drawString(x + label_width + 5, y, str(value))
            return 1

    def draw_text_wrapped(p, text, x, y, width, height):
        p.setFont("Helvetica", 9)
        words = str(text).split()
        lines = []
        current_line = []
        for word in words:
            if p.stringWidth(" ".join(current_line + [word]), "Helvetica", 9) < width:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))
        
        for i, line in enumerate(lines):
            if y - (i * 12) > 40:
                p.drawString(x, y - (i * 12), line)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=orden_{orden.orden}.pdf'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter 

    # --- BLOQUE DE LOGO REINTEGRADO ---
    logo_path = os.path.join(settings.STATICFILES_DIRS[0], "img", "logo_dgic.png")
    print(f"Buscando imagen en: {logo_path}")
    
    if os.path.exists(logo_path):
        try:
            logo_width = 135 
            logo_height = (837 * logo_width) / 1007
            x_pos = 40
            y_pos = height
            
            p.drawImage(
                logo_path,
                x_pos,
                y_pos - logo_height, 
                width=logo_width,
                height=logo_height,
                preserveAspectRatio=True,
                mask='auto'
            )
        except Exception as e:
            print(f"Error al dibujar logo: {e}")
            p.setFillColorRGB(0.9, 0.9, 0.9)
            p.rect(40, height - 80, 80, 67, fill=1, stroke=0)
            p.setFillColorRGB(0.5, 0.5, 0.5)
            p.setFont("Helvetica", 8)
            p.drawCentredString(80, height - 115, "LOGO")
    else:
        p.setFillColorRGB(0.9, 0.9, 0.9)
        p.rect(40, height - 80, 80, 67, fill=1, stroke=0)
        p.setFillColorRGB(0.5, 0.5, 0.5)
        p.setFont("Helvetica", 8)
        p.drawCentredString(80, height - 115, "LOGO")
    
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width/2, height - 50, "DIRECCIÓN DE INFORMÁTICA")
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(width/2, height - 70, "ORDEN DE TRABAJO")
    
    p.setStrokeColorRGB(0, 0, 0)
    p.line(40, height - 85, width - 40, height - 85)
    
    y = height - 105  

    # --- Información General ---
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "INFORMACIÓN GENERAL")
    y -= 20
    
    datos_izquierda = [
        ("No. ORDEN:", str(orden.orden)),
        ("No. OFICIO:", str(orden.oficio)),
        ("CAPTURA:", str(formatear(orden.fecha_captura) or "")),
        ("RESPONSABLE:", f"({num_emp}) {username_usuario}"),
        ("CLASIFICACIÓN:", orden.clasificacion),
    ]
    datos_derecha = [
        ("PRIORIDAD:", orden.prioridad.capitalize()),
        ("ESTADO:", orden.get_estatus_display()),
        ("F. RECEPCIÓN:", str(formatear(orden.fecha_captura))),
        ("F. INICIO:", str(formatear(orden.fecha_inicio) or "Pendiente")),
        ("F. TÉRMINO:", str(formatear(orden.fecha_terminado) or "Pendiente")),
    ]
    
    y_base = y
    lineas = []
    for i in range(max(len(datos_izquierda), len(datos_derecha))):
        h1 = draw_label_value(p, 40, y_base - (i * 16), datos_izquierda[i][0], datos_izquierda[i][1], 300) if i < len(datos_izquierda) else 1
        h2 = draw_label_value(p, width/2 + 43, y_base - (i * 16), datos_derecha[i][0], datos_derecha[i][1], 200) if i < len(datos_derecha) else 1
        lineas.append(max(h1, h2))

    y = y_base - (sum(lineas) * 12) - 20

    # --- Datos Solicitante ---
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "DATOS DEL SOLICITANTE")
    p.drawString(350, y, "DATOS DEL SERVICIO")
    y -= 20
    sol = orden.solicitantes.first()

    datos_izq_sol = [
        ("SOLICITA:", f"({getattr(orden,'usuario_solicita','')}) {sol.nombre_solicitante}"),
        ("BENEFICIADO:", f"({getattr(orden,'usuario_beneficiado','')}) {sol.nombre_beneficiado}"),
        ("DEPENDENCIA:", sol.dependencia_beneficiado),
        ("PUESTO:", sol.puesto_beneficiado),
        ("TELÉFONO:", sol.telefono_beneficiado),
    ]
    datos_der_ser = [
        ("APLICACIÓN:", orden.aplicacion),
        ("TIPO SERVICIO:", getattr(orden, 'tipo_servicio', 'N/A')),
        ("UBICACIÓN:", getattr(orden, 'ubicacion', 'N/A')),
        ("EQUIPO:", "Sí" if orden.equipo else "No"),
    ]

    y_start = y
    for i in range(max(len(datos_izq_sol), len(datos_der_ser))):
        if i < len(datos_izq_sol):
            draw_label_value(p, 40, y_start - (i * 18), datos_izq_sol[i][0], datos_izq_sol[i][1], 300)
        if i < len(datos_der_ser):
            draw_label_value(p, 350, y_start - (i * 18), datos_der_ser[i][0], datos_der_ser[i][1], 250)

    # --- SECCIÓN: DESCRIPCIÓN (FILA PROPIA) ---
    y = y_start - 100
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "DESCRIPCIÓN DEL PROBLEMA")
    y -= 15
    alto_desc = 60
    p.setStrokeColorRGB(0.8, 0.8, 0.8)
    p.rect(40, y - alto_desc, width - 80, alto_desc, stroke=1, fill=0)
    draw_text_wrapped(p, orden.descripcion, 45, y - 12, width - 90, alto_desc)
    
    y -= (alto_desc + 20)

    # --- SECCIÓN: SOLUCIONES POR TÉCNICO (FILAS PROPIAS) ---
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "SOLUCIONES / OBSERVACIONES POR TÉCNICO")
    y -= 15
    alto_fila_tec = 40

    for asig in soluciones_tecnicos:
        if y < 150:
            p.showPage()
            y = height - 70
        
        p.setStrokeColorRGB(0.8, 0.8, 0.8)
        p.rect(40, y - alto_fila_tec, width - 80, alto_fila_tec, stroke=1, fill=0)
        
        nombre = asig.realiza.get_full_name() or asig.realiza.username
        texto = f"{nombre}: {asig.solucion if asig.solucion else 'Sin reporte.'}"
        draw_text_wrapped(p, texto, 45, y - 12, width - 90, alto_fila_tec)
        y -= (alto_fila_tec + 5)

    # --- Firmas y Pie ---
    firma_y = 100
    p.setStrokeColorRGB(0, 0, 0)
    p.line(60, firma_y, 260, firma_y)
    p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(160, firma_y - 15, "FIRMA DE CONFORMIDAD")
    p.line(330, firma_y, 530, firma_y)
    p.drawCentredString(430, firma_y - 15, "FIRMA DEL RESPONSABLE")
    p.setFont("Helvetica", 8)
    p.drawCentredString(430, firma_y - 30, f"({num_emp}) {nombre_usuario}")
    
    from datetime import datetime
    p.setFont("Helvetica-Oblique", 7)
    p.drawRightString(width - 40, 30, f"Impreso el: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    p.drawRightString(width - 40, 20, f"Usuario: {username_usuario}")

    p.showPage()
    p.save()
    return response

def usuarios_disponibles(request, orden_id):
    extras = ExtraUsuarios.objects.filter(estatus='A').order_by('tipo')

    lista = []
    for extra in extras:
        user = extra.usuario
        asignadas = UsuariosxOrden.objects.filter(realiza=user, estatus='A').count()
        lista.append({
            'id': user.id,
            'nombre': user.get_full_name(),
            'empleado': getattr(extra, 'empleado', ''),
            'tipo': extra.tipo,
            'ordenes_asignadas': asignadas
        })

    # Ordenar por menos órdenes asignadas
    lista = sorted(lista, key=lambda x: x['ordenes_asignadas'])

    return JsonResponse({'usuarios': lista})

@require_POST
def reasignar_orden(request: HttpRequest):
    try:
        data = json.loads(request.body)

        orden_id = data.get('orden_id')
        usuarios_ids = data.get('usuarios_ids', [])
        comentario = data.get('comentario', '')

        if not orden_id or not usuarios_ids:
            return JsonResponse(
                {"error": "Se requiere orden_id y usuarios_ids."},
                status=400
            )

        try:
            usuarios_ids = [int(uid) for uid in usuarios_ids]
        except ValueError:
            return JsonResponse(
                {"error": "usuarios_ids contiene valores inválidos."},
                status=400
            )

        orden = get_object_or_404(Orden, pk=orden_id)
        usuario_que_asigna = request.user

        usuarios_nuevos = User.objects.filter(id__in=usuarios_ids)

        if not usuarios_nuevos.exists():
            return JsonResponse(
                {"error": "No se encontraron usuarios válidos."},
                status=400
            )

        UsuariosxOrden.objects.filter(orden=orden).delete()
        timestamp = timezone.localtime().strftime('%d/%m/%Y %H:%M')
        registros = []
        for usuario in usuarios_nuevos:
            registros.append(
                UsuariosxOrden(
                    orden=orden,
                    realiza=usuario,
                    asigna=usuario_que_asigna,
                    estatus="A",
                    estatus_orden="A",
                    comentarios=(
                        f"[{timestamp}] Reasignación: {comentario}"
                        if comentario
                        else f"[{timestamp}] Reasignación"
                    )
                )
            )

        UsuariosxOrden.objects.bulk_create(registros)

        for usuario in usuarios_nuevos:

            if notificaciones_activadas(usuario.id):
                Notificar.crear(
                    usuario=usuario,
                    mensaje=f"Has sido reasignado a la orden #{orden.orden}.",
                    tipo="task"
                )

                Notificar.correo_html(
                    usuario.email,
                    "Has sido reasignado a una nueva orden",
                    "correos/orden_asignada.html",
                    contexto={
                        "usuario": usuario.get_full_name() or usuario.username,
                        "orden_id": orden.orden,
                        "resumen": orden.descripcion,
                        "url": request.build_absolute_uri(
                            f"/ordenes/ordenes/"
                        ),
                    }
                )

        return JsonResponse({
            "success": True,
            "message": f"Orden {orden.orden} reasignada correctamente.",
            "total_usuarios": usuarios_nuevos.count(),
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "JSON inválido."},
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {"error": f"Error interno: {str(e)}"},
            status=500
        )

@transaction.atomic
def duplicar_orden(orden):
    nueva_orden = Orden.objects.create(
        oficio=orden.oficio,
        usuario_solicita=orden.usuario_solicita,
        usuario_beneficiado=orden.usuario_beneficiado,
        telefono=orden.telefono,
        aplicacion=orden.aplicacion,
        clasificacion=orden.clasificacion,
        descripcion=orden.descripcion,
        prioridad=orden.prioridad,
        equipo=orden.equipo,
        captura=orden.captura,
        estatus='A',
        capacitacion=orden.capacitacion,
        capacitacion_descripcion=orden.capacitacion_descripcion,
    )

    # Solicitantes
    for s in orden.solicitantes.all():
        s.pk = None
        s.orden = nueva_orden
        s.save()

    # Equipos
    for e in orden.equipos.all():
        e.pk = None
        e.orden = nueva_orden
        e.save()

    # Usuarios asignados (opcional, tú decides)
    for u in orden.usuarios_orden.all():
        u.pk = None
        u.orden = nueva_orden
        u.save()

    # Archivos (NO duplica el archivo físico, solo la relación)
    for a in orden.archivos.all():
        a.pk = None
        a.orden = nueva_orden
        a.save()

    return nueva_orden

def entregar_equipo(request, equipo_id):
    equipo = get_object_or_404(EquipoXOrden, pk=equipo_id)
    equipo.entregado_foraneo = True
    equipo.fecha_entrega = timezone.now()
    equipo.save()

    messages.success(request, f'El equipo "{equipo.equipo}" ha sido marcado como entregado.')
    return redirect('detalle_orden', pk=equipo.orden.orden)

@require_POST
def guardar_comentario(request):
    data = json.loads(request.body)

    orden_id = data.get('orden')
    comentario = data.get('comentario', '').strip()

    if not comentario:
        return JsonResponse(
            {'ok': False, 'error': 'Comentario vacío'},
            status=400
        )

    uxo = UsuariosxOrden.objects.filter(
        orden_id=orden_id,
        realiza=request.user,
    ).first()

    if not uxo:
        return JsonResponse(
            {'ok': False, 'error': 'Registro no encontrado'},
            status=404
        )

    hora_local = timezone.localtime(timezone.now())
    
    if uxo.comentarios:
        uxo.comentarios += f'\n[{hora_local.strftime("%Y-%m-%d %H:%M")}] {comentario}'
    else:
        uxo.comentarios = comentario

    uxo.save(update_fields=['comentarios'])

    return JsonResponse({'ok': True})
        
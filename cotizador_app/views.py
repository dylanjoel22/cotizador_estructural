from django.shortcuts import render

# Create your views here.

def cotizacion(request):
    return render(request, 'coti_app/cotizacion.html')

def crear_cotizacion(request):
    return render(request, 'coti_app/crear_cotizacion.html')

def detalle_cotizacion(request):
    return render(request, 'coti_app/detalle_cotizacion.html')
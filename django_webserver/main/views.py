from django.shortcuts import render


def index(request):
    # Serve a simple page that mirrors the original NGINX index.html
    return render(request, 'index.html')

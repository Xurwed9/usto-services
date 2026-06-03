from django.shortcuts import render,redirect,get_object_or_404
from .models import Category,Service
from django.contrib.auth.decorators import login_required

# Create your views here.


def category_services(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    
    services = Service.objects.filter(category=category).order_by('-id')
    
    categories = Category.objects.all()
    
    context = {
        'category': category,
        'services': services,
        'categories': categories,
    }
    return render(request, 'services/category_services.html', context)


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'services/category_list.html', {'categories': categories})


def service_list(request):
    services = Service.objects.all().order_by('-id')
    categories = Category.objects.all()
    
    context = {
        'services': services,
        'categories': categories
    }
    return render(request, 'services/service_list.html', context)


def service_detail(request, id):
    service = get_object_or_404(Service, id=id)
    
    context = {
        'service': service,
    }
    return render(request, 'services/service_detail.html', context)

def create_service(request):
    if request.user.role!='master':
        return redirect('/')
    if request.method == 'POST':
        category_id = request.POST.get('category')
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price')
        image = request.FILES.get('image')

        if not category_id or not title or not description or not price:
            return render(request, 'services/service_form.html', {
                'error': 'Ҳамаи майдонҳоро пур кунед!',
                'title': 'Иловаи хизматрасонии нав'
            })
        category = Category.objects.filter(id=category_id).first()
        service = Service.objects.create(
            master=request.user,
            category=category,
            title=title,
            description=description,
            price=price,
            image=image
        )
        return redirect('profile')
    else:
        categories = Category.objects.all()
        return render(request, 'services/service_form.html', 
                      {'title': 'Иловаи хизматрасонии нав',
                       'categories': categories})
    


@login_required
def update_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if service.master != request.user:
        return redirect('/')
    if request.method == 'POST':
        service.title = request.POST.get('title')
        service.description = request.POST.get('description')
        service.price = request.POST.get('price')
        category_id = request.POST.get('category')
        if category_id:
            service.category = Category.objects.get(pk=category_id)
        new_image = request.FILES.get('image')
        if new_image:
            service.image = new_image
        service.save()
        return redirect('service_list')
    categories = Category.objects.all()
    return render(request, 'services/service_form.html', {
        'service': service,
        'categories': categories,
        'title': 'Таҳрири хизматрасонӣ'
    })
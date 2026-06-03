from django.shortcuts import render,redirect,get_object_or_404
from .models import Category,Service,Order
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# Create your views here.

@login_required
def category_services(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    
    services = Service.objects.filter(category=category).filter(is_active=True).order_by('-id')
    
    categories = Category.objects.all()
    
    context = {
        'category': category,
        'services': services,
        'categories': categories,
    }
    return render(request, 'services/category_services.html', context)

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'services/category_list.html', {'categories': categories})


def service_list(request):
    services = Service.objects.filter(is_active=True).order_by('-id')
    categories = Category.objects.all()
    
    context = {
        'services': services,
        'categories': categories
    }
    return render(request, 'services/service_list.html', context)

@login_required
def service_detail(request, id):
    service = get_object_or_404(Service, id=id)
    
    context = {
        'service': service,
    }
    return render(request, 'services/service_detail.html', context)

@login_required
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
        return redirect('service_list')
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

@login_required
def delete_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if service.master == request.user:
        service.delete()
    return redirect('service_list')


@login_required
def toggle_service_status(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if service.master == request.user:
        service.is_active = not service.is_active
        service.save()
    return redirect('profile') 


@login_required
def service_search(request):
    query = request.GET.get('q', '').strip()
    categories = Category.objects.all()
    services = Service.objects.filter(is_active=True).select_related('category', 'master')
    
    if query:
        services = services.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    
    context = {
        'services': services,
        'categories': categories,
        'query': query,
    }
    return render(request, 'services/service_list.html', context)



@login_required
def create_order(request, pk):
    service = get_object_or_404(Service, pk = pk, is_active=True)
    if service.master == request.user:
        return redirect('service_detail', id=pk)
    if request.method=='POST':
        description = request.POST.get('description', '').strip()
        address = request.POST.get('address', '').strip()

        if not description or not address:
            return render(request, 'services/order_form.html',
                          {'service': service,
                           'error': 'Лутфан, тавсиф ва суроғаро пур кунед!'})
        Order.objects.create(
            client=request.user,
            service=service,
            description=description,
            address=address
        )
        return redirect('my_orders')
        
    return render(request, 'services/order_form.html', {'service': service})

@login_required
def my_orders(request):
    my_requests = Order.objects.filter(client=request.user).select_related('service__master', 'service__category').order_by('-created_at')
    incoming_orders = Order.objects.filter(service__master=request.user).select_related('client','service').order_by('-created_at')
    return render(request, 'services/my_orders.html', {
        'my_requests': my_requests,
        'incoming_orders': incoming_orders,
    })


@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.client == request.user:
        if order.status == 'pending':
            order.status='cancel'
            order.save()
    return redirect('my_orders')


@login_required
def update_order_status(request, pk, status):
    order = get_object_or_404(Order, pk=pk)
    
    if order.service.master == request.user:
        if status in ['accepted', 'canceled', 'completed']:
            order.status = status
            
            service = order.service
            if status == 'accepted':
                service.is_active = False
                service.save()
            elif status == 'completed' or status == 'canceled':
                service.is_active = True
                service.save()
            
            order.save()
            
    return redirect('my_orders')
from django.shortcuts import render,redirect
from .models import Category,Service

# Create your views here.


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'services/category_list.html', {'categories': categories})


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
        return render(request, 'services/service_form.html', {'title': 'Иловаи хизматрасонии нав'})
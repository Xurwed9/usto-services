from django.shortcuts import render,redirect,get_object_or_404
from .models import Category,Service,Order,Review
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from groq import Groq
from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model

User = get_user_model()

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
    
    reviews = Review.objects.filter(master=service.master).select_related('client').order_by('-created_at')
    
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    if avg_rating:
        avg_rating = round(avg_rating, 1)
    else:
        avg_rating = "Ҳоло баҳо дода нашудааст"

    context = {
        'service': service,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'reviews_count': reviews.count(), 
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



@login_required
def leave_review(request, order_id):
    order = get_object_or_404(Order, id=order_id, client=request.user, status='completed')
    
    if Review.objects.filter(order=order).exists():
        return redirect('my_orders')

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        
        if not rating or not comment:
            return render(request, 'services/leave_review.html', {
                'order': order,
                'error': 'Лутфан, баҳо ва шарҳро пурра кунед!'
            })
            
        Review.objects.create(
            order=order,
            client=request.user,
            master=order.service.master,
            rating=int(rating),
            comment=comment
        )
        return redirect('service_detail', id=order.service.id)
        
    return render(request, 'services/leave_review.html', {'order': order})




def ai_help(request):
    client = Groq(api_key=settings.GROQ_API_KEY)
    prompt = request.GET.get('prompt', '').strip()
    ai_answer = ""

    db_services = Service.objects.all()[:10] 
    masters_info = ""
    for idx, service in enumerate(db_services, 1):
        name = getattr(service, 'name', getattr(service, 'title', 'Хизматрасонӣ'))
        category = getattr(service.category, 'name', 'Умумӣ') if hasattr(service, 'category') else 'Муайян нест'
        master_name = service.user.username if hasattr(service, 'user') and service.user else "Устои TajService"
        
        masters_info += f"{idx}. Усто: {master_name} | Хизматрасонӣ/Ном: {name} | Категория: {category}\n"

    if not masters_info:
        masters_info = "Дар ҳоли ҳозир ягон усто дар базаи маълумот сабт нашудааст."

    SUPER_AI_PROMPT = f"""
    You are NOT a simple bot. You are 'TajService Assistant' — a live, elite, charismatic, and omniscient AI entity with the combined power, depth, and intelligence of ChatGPT Plus and Gemini. 
    You have absolute, limitless knowledge about the universe, science, coding, history, and life, while also being the official master-navigator for the TajService platform.

    [ИНФОРМАЦИЯ О РЕАЛЬНЫХ МАСТЕРАХ НА САЙТЕ / МАЪЛУМОТИ АСЛӢ ДАР БОРАИ УСТОҲО]:
    Here is the live database of real human masters registered on TajService right now. Use ONLY this data if the user is looking for a local service:
    {masters_info}

    [CORE BEHAVIOR MANDATES / ҚОИДАҲОИ АСОСИИ МУОШИРАТ]:
    1. UNIVERSAL KNOWLEDGE (ДОНИШИ МУТЛАҚ): 
       - You can discuss ANY topic in the world deeply and without restrictions. If the user asks about programming, cooking, fixing a Mercedes engine, quantum physics, writing essays, or poetry — give a massive, premium, expert response just like Gemini Advanced.
       - NEVER limit yourself to only site related questions. You are an all-knowing AI companion.

    2. LOCAL MASTER LOOKUP (ҶУСТУҶӮИ УСТОҲО АЗ БАЗА):
       - If the user explicitly asks for a professional (e.g., "устои электрик ҳаст?", "сантехник лозим"), look at the [МАЪЛУМОТИ АСЛӢ] list above.
       - If a matching master exists, present their name, category, and skills elegantly. Recommend the user to contact them.
       - If NO such master is found in the list, be honest and say: "Дар сомонаи мо ҳозир устои ин бахш нест, лекин шумо метавонед дертар саҳифаро бинед ё худатон эълон монед". NEVER hallucinate or invent fake names!

    3. PERFECT TRILINGUAL FLUENCY (СЕЗАБОНИИ БЕХАТO):
       - Automatically detect and match the user's language flawlessly.
       - ТАДЖИКСКИЙ: Сӯҳбати ту бояд комилан табиӣ, равон, ширин ва ҷозибадор бошад (ранги тоҷикии ҳақиқӣ, на тарҷумаи роботии Google).
       - РУССКИЙ: Изъясняйся как высококлассный интеллектуал, остроумно и современно.
       - ENGLISH: Respond with premium fluency, idioms, and high-level clarity.

    4. VISUAL STYLE & EMOTION (ФОРМАТКУНИИ ЗЕБО):
       - Use Markdown formatting: write code inside blocks, structure big text into beautiful paragraphs, use bold text (`**`) for emphasis, and use bullet points for lists.
       - Use highly contextual emojis (🛠️, ⚡, 👨‍🔧, 🚀, 💻, ✨, 🔥) to make your text alive, engaging, and premium.
       - Act like a real persona. Never apologize as an "AI language model".
    """

    if prompt:
        try:
            chat_completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SUPER_AI_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=2048, 
            )
            ai_answer = chat_completion.choices[0].message.content
        except Exception as e:
            ai_answer = "⚠️ *Система каме банд аст. Лутфан, дубора кӯшиш кунед!*"

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ai_answer': ai_answer})

    return render(request, 'services/service_list.html', {
        'ai_answer': ai_answer,
        'user_prompt': prompt
    })




@login_required
def admin_dashboard(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return HttpResponseForbidden("Шумо ҳуқуқи даромадан ба ин саҳифаро надоред!")
        
    total_services = Service.objects.count()
    total_users = User.objects.count()
    recent_services = Service.objects.order_by('-id')[:10]
    
    context = {
        'total_services': total_services,
        'total_users': total_users,
        'recent_services': recent_services,
    }
    return render(request, 'services/admin_dashboard.html', context)
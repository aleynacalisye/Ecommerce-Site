import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q, F
from django.db.models.functions import Concat
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import translation
from home.forms import SearchForm
from home.models import Setting, ContactForm, ContactMessage, FAQ, SettingLang, Language
from project2 import settings
from products.models import Category, Product, Images, Comment, Variants, ProductLang, CategoryLang
from users.models import UserProfile


def index(request):
    # Varsayılan para birimini ayarla
    if not request.session.has_key('currency'):
        request.session['currency'] = settings.DEFAULT_CURRENCY

    # Site ayarlarını al
    setting = Setting.objects.get(pk=1)

    # Son eklenen 4 ürünü al
    products_latest = Product.objects.all().order_by('-id')[:4]

    # Dil ayarlarını al
    default_lang = settings.LANGUAGE_CODE[0:2]
    current_lang = request.LANGUAGE_CODE[0:2]

    # Dil farklı ise dil ayarlarını güncelle
    if default_lang != current_lang:
        setting = SettingLang.objects.get(lang=current_lang)
        products_latest = Product.objects.raw(
            'SELECT p.id, p.price, l.title, l.description, l.slug '
            'FROM product_product as p '
            'LEFT JOIN product_productlang as l '
            'ON p.id = l.product_id '
            'WHERE l.lang=%s ORDER BY p.id DESC LIMIT 4', [current_lang])

    # Slider için ilk 4 ürünü al
    products_slider = Product.objects.all().order_by('id')[:4]

    # Rastgele seçilen 4 ürünü al
    products_picked = Product.objects.all().order_by('?')[:4]

    # Sayfa adını belirle
    page = "home"

    # Context oluştur
    context = {
        'setting': setting,
        'page': page,
        'products_slider': products_slider,
        'products_latest': products_latest,
        'products_picked': products_picked,
    }

    # İndex sayfasını renderla ve context'i gönder
    return render(request, 'index.html', context)





def aboutus(request):
    # Site ayarlarını ve dil ayarlarını al
    default_lang = settings.LANGUAGE_CODE[0:2]
    current_lang = request.LANGUAGE_CODE[0:2]
    setting = Setting.objects.get(pk=1)

    # Dil farklı ise dil ayarlarını güncelle
    if default_lang != current_lang:
        setting = SettingLang.objects.get(lang=current_lang)

    # Context oluştur
    context = {'setting': setting}

    # Hakkımızda sayfasını renderla ve context'i gönder
    return render(request, 'about.html', context)


def contactus(request):
    # Site ayarlarını ve dil ayarlarını al
    current_lang = request.LANGUAGE_CODE[0:2]
    setting = Setting.objects.get(pk=1)

    # Dil farklı ise dil ayarlarını güncelle
    if settings.LANGUAGE_CODE[0:2] != current_lang:
        setting = SettingLang.objects.get(lang=current_lang)

    # Formu işle
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data = ContactMessage(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
                ip=request.META.get('REMOTE_ADDR')
            )
            data.save()
            messages.success(request, "Your message has been sent. Thank you for your message.")
            return HttpResponseRedirect('/contact')

    # Formu oluştur
    form = ContactForm()

    # Context oluştur
    context = {'setting': setting, 'form': form}

    # İletişim sayfasını renderla ve context'i gönder
    return render(request, 'contactus.html', context)


def category_products(request, id, slug):
    # Site ayarlarını ve dil ayarlarını al
    current_lang = request.LANGUAGE_CODE[0:2]
    catdata = Category.objects.get(pk=id)
    products = Product.objects.filter(category_id=id)

    # Dil farklı ise dil ayarlarını güncelle
    if settings.LANGUAGE_CODE[0:2] != current_lang:
        try:
            products = Product.objects.raw(
                'SELECT p.id, p.price, p.amount, p.image, p.variant, l.title, l.keywords, l.description, l.slug, l.detail '
                'FROM product_product as p '
                'LEFT JOIN product_productlang as l '
                'ON p.id = l.product_id '
                'WHERE p.category_id=%s AND l.lang=%s', [id, current_lang])
        except:
            pass
        catdata = CategoryLang.objects.get(category_id=id, lang=current_lang)

    # Context oluştur
    context = {'products': products, 'catdata': catdata}

    # Kategori ürünlerini renderla ve context'i gönder
    return render(request, 'category_products.html', context)


def search(request):
    # Arama formunu işle
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            catid = form.cleaned_data['catid']
            if catid == 0:
                products = Product.objects.filter(title__icontains=query)
            else:
                products = Product.objects.filter(title__icontains=query, category_id=catid)

            # Context oluştur
            context = {'products': products, 'query': query, 'category': Category.objects.all()}

            # Arama sonuçlarını renderla ve context'i gönder
            return render(request, 'search_products.html', context)

    return HttpResponseRedirect('/')


def search_auto(request):
    # Otomatik arama işlemi
    if request.is_ajax():
        q = request.GET.get('term', '')
        products = Product.objects.filter(title__icontains=q)
        results = [rs.title + " > " + rs.category.title for rs in products]
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def product_detail(request, id, slug):
    # Ürün detayını işle
    query = request.GET.get('q')
    category = Category.objects.all()
    product = Product.objects.get(pk=id)

    # Dil farklı ise dil ayarlarını güncelle
    if settings.LANGUAGE_CODE[0:2] != request.LANGUAGE_CODE[0:2]:
        try:
            prolang = Product.objects.raw(
                'SELECT p.id, p.price, p.amount, p.image, p.variant, l.title, l.keywords, l.description, l.slug, l.detail '
                'FROM product_product as p '
                'INNER JOIN product_productlang as l '
                'ON p.id = l.product_id '
                'WHERE p.id=%s AND l.lang=%s', [id, request.LANGUAGE_CODE[0:2]])
            product = prolang[0]
        except:
            pass

    images = Images.objects.filter(product_id=id)
    comments = Comment.objects.filter(product_id=id, status='True')
    context = {'product': product, 'category': category, 'images': images, 'comments': comments}

    if product.variant != "None":
        if request.method == 'POST':
            variant_id = request.POST.get('variantid')
            variant = Variants.objects.get(id=variant_id)
            colors = Variants.objects.filter(product_id=id, size_id=variant.size_id)
            sizes = Variants.objects.raw(
                'SELECT * FROM product_variants WHERE product_id=%s GROUP BY size_id', [id])
            query += variant.title + ' Size:' + str(variant.size) + ' Color:' + str(variant.color)
        else:
            variants = Variants.objects.filter(product_id=id)
            colors = Variants.objects.filter(product_id=id, size_id=variants[0].size_id)
            sizes = Variants.objects.raw(
                'SELECT * FROM product_variants WHERE product_id=%s GROUP BY size_id', [id])
            variant = Variants.objects.get(id=variants[0].id)

        context.update({'sizes': sizes, 'colors': colors, 'variant': variant, 'query': query})

    # Ürün detayını renderla ve context'i gönder
    return render(request, 'product_detail.html', context)


def ajaxcolor(request):
    # Renk seçimi için AJAX işle
    data = {}
    if request.POST.get('action') == 'post':
        size_id = request.POST.get('size')
        product_id = request.POST.get('productid')
        colors = Variants.objects.filter(product_id=product_id, size_id=size_id)
        context = {
            'size_id': size_id,
            'productid': product_id,
            'colors': colors,
        }
        data = {'rendered_table': render_to_string('color_list.html', context=context)}
        return JsonResponse(data)
    return JsonResponse(data)


def faq(request):
    # SSS sayfasını işle
    current_lang = request.LANGUAGE_CODE[0:2]
    if settings.LANGUAGE_CODE[0:2] == current_lang:
        faq = FAQ.objects.filter(status="True", lang=current_lang).order_by("ordernumber")
    else:
        faq = FAQ.objects.filter(status="True", lang=current_lang).order_by("ordernumber")

    # Context oluştur
    context = {'faq': faq}

    # SSS sayfasını renderla ve context'i gönder
    return render(request, 'faq.html', context)


def selectcurrency(request):
    # Para birimi seçimini işle
    last_url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        request.session['currency'] = request.POST['currency']
    return HttpResponseRedirect(last_url)



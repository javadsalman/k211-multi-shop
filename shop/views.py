from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import Campaign, Category, Product, Color, Size
from customer.models import Review
from django.db.models import Count, Avg
from django.core.paginator import Paginator
from django.contrib.postgres.search import TrigramSimilarity, SearchQuery, SearchRank, SearchVector
from .filters import ProductFilter
from django.views.decorators.cache import cache_page

# Create your views here.


def product_list(request):
    products = Product.objects.all().annotate(avg_star=Avg('reviews__star_count'), review_count=Count('reviews'))
    
    search_input = request.GET.get('search')
    if search_input:
        # products = products.filter(title=search_input)
        # products = products.filter(title__iexact=search_input)
        # products = products.filter(title__icontains=search_input)
        # products = products.annotate(similarity=TrigramSimilarity('title', search_input)).filter(similarity__gt=0.3).order_by('-similarity')
        vector = SearchVector("title", weight="A") + SearchVector("description", weight="B") + SearchVector("categories__title", weight="C")
        query = SearchQuery(search_input)
        products = products.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.1).order_by('-rank')
    
    product_filter = ProductFilter(request.GET, products)
    products = product_filter.qs
    
    sorting_input = request.GET.get('sorting')
    if sorting_input:
        if sorting_input == '-avg_star':
            products = products.order_by('-avg_star', '-review_count')
        else:
            products = products.order_by(sorting_input)
    
    page_by_input = int(request.GET.get('page_by', 6))
    page_input = int(request.GET.get('page', 1))
    paginator = Paginator(products, page_by_input)
    page = paginator.page(page_input)
    products = page.object_list
    
    colors = Color.objects.all().annotate(product_count=Count('products'))
    sizes = Size.objects.all().annotate(product_count=Count('products'))
    
    return render(request, 'product-list.html', {
        'products': products,
        'paginator': paginator,
        'page': page,
        'sizes': sizes,
        'colors': colors,
    })

# @cache_page(15)
def home(request):
    slide_campaigns = Campaign.objects.filter(is_slide=True)[:3]
    nonslide_campaigns = Campaign.objects.filter(is_slide=False)[:4]
    categories = Category.objects.annotate(product_count = Count('products'))
    featured_products = Product.objects.filter(featured=True)[:8]
    recent_products = Product.objects.all().order_by('-created')[:8]
    
    return render(request, 'home.html', {
        'slide_campaigns': slide_campaigns,
        'nonslide_campaigns': nonslide_campaigns,
        'categories': categories,
        'featured_products': featured_products,
        'recent_products': recent_products,
    })


def product_detail(request, pk, slug):
    product = get_object_or_404(Product, pk=pk)
    # other_products = Product.objects.filter(categories__in=product.categories.all()).annotate(common_product_count=Count('pk')).exclude(pk=product.pk).order_by('-common_product_count')[:5]
    other_products = Product.objects.exclude(pk=product.pk).order_by('?')[:5]
    # product_info = Product.objects.aggregate(avg_star=Avg('reviews__star_count'))
    
    user_review = request.user.is_authenticated and Review.objects.filter(customer=request.user.customer, product=product).first()
    reviews = product.reviews.exclude(customer=request.user.is_authenticated and request.user.customer)
    return render(request, 'product-detail.html', {
        'product': product,
        'other_products': other_products,
        'user_review': user_review,
        'reviews': reviews,
        # 'product_info': product_info
    })
    
    
def review(request, pk):
    if request.method == 'POST':
        customer = request.user.customer
        product = get_object_or_404(Product, pk=pk)
        if Review.objects.filter(customer=customer, product=product).exists():
            HttpResponse(status=403)
        star_count = int(request.POST.get('star_count'))
        comment = request.POST.get('comment')
        review = Review.objects.create(
            customer=customer, product=product,
            comment=comment, star_count=star_count
        )
        return redirect('shop:product-detail', pk=pk)
    return redirect('shop:home')
    
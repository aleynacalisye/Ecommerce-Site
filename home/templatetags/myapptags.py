from django import template
from django.urls import reverse
from project2 import settings
from products.models import Category

register = template.Library()

@register.simple_tag
def categoryTree(id, menu):
    default_lang = settings.LANGUAGE_CODE[0:2]
    menu = ''

    if id <= 0:  # Ana kategoriler
        query = Category.objects.filter(parent_id__isnull=True).order_by("id")
    else:  # Alt kategoriler
        query = Category.objects.filter(parent_id=id)

    if query:
        for rs in query:
            sub_count = Category.objects.filter(parent_id=rs.id).count()
            if sub_count > 0:
                menu += '\t<li class="dropdown side-dropdown">\n'
                menu += '\t<a class="dropdown-toggle" data-toggle="dropdown" aria-expanded="true">' + rs.title + '<i class="fa fa-angle-right"></i></a>\n'
                menu += '\t\t<div class="custom-menu">\n'
                menu += '\t\t\t<ul class="list-links">\n'
                menu = categoryTree(int(rs.id), menu)
                menu += '\t\t\t</ul>\n'
                menu += '\t\t</div>\n'
                menu += "\t</li>\n\n"
            else:
                menu += '\t\t\t\t<li><a href="' + reverse('category_products', args=(rs.id, rs.slug)) + '">' + rs.title + '</a></li>\n'
    return menu

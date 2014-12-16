from django import template
from django.template import loader, Context
from django.template.base import Template

from djara.django.menus.models import GlobalMenu

register = template.Library()


def show_global_menu(context, menu_template='djara/django/menus/simple_menu.html'):
    """
    """

    request = context['request']

    template_context = Context({
        'menu_items': GlobalMenu.instance().items,
        'current_view': request.resolver_match.view_name,
        'user': context['user'],
    })

    template = loader.get_template(menu_template)

    rendered = template.render(template_context)

    return rendered

register.simple_tag(takes_context=True)(show_global_menu)


def show_active_sub_menu(context, menu_template='djara/django/menus/simple_menu.html'):
    """
    """

    request = context['request']
    current_view = request.resolver_match.view_name

    def get_active_menu(menu_tree):
        active_item = None

        for item in menu_tree.items:
            if item.is_current_item(current_view):
                active_item = item
                break

        return active_item

    active_menu_item = get_active_menu(GlobalMenu.instance())

    return render_menu_children(context, active_menu_item, menu_template)

register.simple_tag(takes_context=True)(show_active_sub_menu)


def render_menu_children(context, active_menu_item, menu_template='djara/django/menus/simple_menu.html'):
    """
    """

    request = context['request']

    if active_menu_item is None:
        children = []
    else:
        children = active_menu_item.children

    template_context = Context({
        'menu_items': children,
        'current_view': request.resolver_match.view_name,
        'user': context['user'],
    })

    template = loader.get_template(menu_template)

    rendered = template.render(template_context)

    return rendered


class ShowPermittedMenuEntryNode(template.Node):

    def __init__(self, nodelist_empty, menu_item_variable):
        self.nodelist_empty = nodelist_empty
        self.menu_item_variable = menu_item_variable

    def render(self, context):
        ''' If a variable is passed, it is found as string, so first we use render to convert that
            variable to a string, and then we render that string. '''
        if self.nodelist_empty is None:
            return ''
        else:
            user_variable = template.Variable('user').resolve(context)
            resolved_menu_item = template.Variable(self.menu_item_variable).resolve(context)

            if resolved_menu_item.permission_method(user_variable) is True:
                template_string = ''

                # Set if is current view
                current_view = context['current_view']
                if resolved_menu_item.is_current_item(current_view) or resolved_menu_item.has_child(current_view):
                    resolved_menu_item.active = True

                # Render template
                for node in self.nodelist_empty:
                    template_string += node.render(context)
                rendered = Template(template_string).render(context)

                # Unset current view
                resolved_menu_item.active = False

                return rendered
            else:
                return ''


def show_permitted_menu_entry(parser, token):
    """
    """

    try:
        menu_item_variable = token.split_contents()[1]
        nodelist_loop = parser.parse(('empty', 'endshow_permitted_menu_entry',))
        token = parser.next_token()
        if token.contents == 'empty':
            nodelist_empty = parser.parse(('endshow_permitted_menu_entry',))
            parser.delete_first_token()
        else:
            nodelist_empty = None
    except Exception:
        raise template.TemplateSyntaxError('Syntax for show_permitted_menu_entry tag is wrong.')
    return ShowPermittedMenuEntryNode(nodelist_loop, menu_item_variable)

register.tag('show_permitted_menu_entry', show_permitted_menu_entry)
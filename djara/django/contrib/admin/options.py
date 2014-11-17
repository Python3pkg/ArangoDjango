from django.contrib.admin.options import ModelAdmin


class CollectionAdmin(ModelAdmin):

    def __init__(self, model, admin_site):

        super(CollectionAdmin, self).__init__(model, admin_site)
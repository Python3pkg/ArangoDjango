class MenuTree(object):

    def __init__(self):
        """
        """

        self.items = []

    def get_item(self, key):
        """
        """

        for item_obj in self.items:
            if item_obj.name == key or item_obj.view == key:
                return item_obj

        raise Exception('No item found')


class MenuTreeItem(object):

    def __init__(self, key, display_name, view, permission_method, **kwargs):
        """
        """

        # To which view it is mapped
        self.view = view

        self.key = key
        self.display_name = display_name

        self.items = []

        self.permission_method = permission_method

        # Temporary variable
        self.active = False

        # Children
        self.children = kwargs.pop('children', [])

    def add_child(self, child):
        """
        """

        self.children.append(child)


class GlobalMenu(MenuTree):

    _instance = None

    def __init__(self):
        super(GlobalMenu, self).__init__()

    @classmethod
    def init(cls):
        """
        """

        if cls._instance is None:
            cls._instance = cls()

    @classmethod
    def instance(cls):
        """
        """

        cls.init()
        return cls._instance

    @classmethod
    def add_menu_item(cls, item, parent_key=None):
        """
        """

        if parent_key is None:
            cls.instance().items.append(item)
        else:
            items = cls.instance().items

            # Iterate over all items and search the parent
            for parent_item in items:
                if parent_item.key == parent_key:
                    parent_item.add_child(item)
                    break

    @classmethod
    def item(cls, key):
        """
        """

        return cls.instance().get_item(key=key)
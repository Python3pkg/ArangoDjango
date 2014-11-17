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

    def __init__(self, key, display_name, view, permission_method):
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
    def add_menu_item(cls, item):
        """
        """

        cls.instance().items.append(item)

    @classmethod
    def item(cls, key):
        """
        """

        return cls.instance().get_item(key=key)
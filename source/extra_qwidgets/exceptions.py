class CategoryNotImplemented(Exception):
    def __init__(self, category: str):
        super().__init__(f"Category '{category}' is not implemented yet.")


class FavoriteNotImplemented(CategoryNotImplemented):
    def __init__(self):
        super().__init__("Favorite")


class RecentNotImplemented(CategoryNotImplemented):
    def __init__(self):
        super().__init__("Recent")


class EmojiAlreadyExists(Exception):
    def __init__(self, emoji: str):
        super().__init__(f"Emoji '{emoji}' already exists in the category.")
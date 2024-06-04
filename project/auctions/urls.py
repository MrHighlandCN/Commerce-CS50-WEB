from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("auction/<int:auction_id>", views.view_page, name="viewpage"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("add_remove_watchlist/<int:auction_id>", views.add_remove_watchlist, name="add_remove_watchlist"),
    path("bid/<int:auction_id>", views.bid, name="bid"),
    path("close/<int:auction_id>", views.close, name="close"),
    path("comment/<int:auction_id>", views.comment, name="comment"),
    path("category", views.category, name="category")
]

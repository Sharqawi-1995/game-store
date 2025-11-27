from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views.logout, name='logout'),
    path('home/', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('cart/', views.cart, name='cart'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:game_id>/',
         views.add_to_wishlist, name='add_to_wishlist'),
    path('cart/add/<int:game_id>/', views.add_to_cart, name='add_to_cart'),
    path('profile/become-developer/',
         views.become_developer, name='become_developer'),
    path('add-game/', views.add_game, name='add_game'),
    path('wishlist/remove/<int:game_id>/',
         views.remove_from_wishlist, name='remove_from_wishlist'),
    path('remove-from-cart/<int:game_id>/',
         views.remove_from_cart, name='remove_from_cart'),
    path('cart/buy/<int:game_id>/', views.buy_game, name='buy_game'),
    path('wishlist/move-to-cart/<int:game_id>/',
         views.move_to_cart, name='move_to_cart'),
    path('search-games/', views.search_games, name='search_games'),
    path("game/<int:game_id>/edit/", views.edit_game, name="edit_game"),
    path("game/<int:game_id>/delete/", views.delete_game, name="delete_game"),
    path("game/<int:game_id>/", views.game_detail, name="game_detail"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from .models import Game, Reviews, Purchase, User  # make sure User is imported
from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
import re
import stripe
from datetime import date
from .utils import verify_email
from django.conf import settings
from django.http import JsonResponse
from django.template.loader import render_to_string

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.


def index(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'register':
            data = request.POST
            files = request.FILES
            uname = data.get('username')
            fname = data.get('firstname')
            lname = data.get('lastname')
            email = data.get("email")
            phonenumber = data.get('phone_number')
            dob = data.get('date_of_birth')
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            avatar = files.get('avatar')

            errors = []

            if not dob and not email and not fname and not lname and not uname and not password and not confirm_password:
                errors.append("All fields are required")
            if not email:
                errors.append("Email is required.")
            else:
                if not verify_email(email):
                    errors.append("Invalid or undeliverable email address.")
            if User.objects.filter(username=uname).exists():
                errors.append("Username already taken.")
            if not (3 < len(uname) <= 10):
                errors.append(
                    "Username must be between 4 and 10 characters long.")
            if User.objects.filter(email=email).exists():
                errors.append("Email already registered.")
            if password != confirm_password:
                errors.append("Passwords do not match.")
            if len(password) < 6:
                errors.append("Password must be at least 6 characters long.")
            if not dob:
                errors.append("Date of Birth is required.")
            try:
                birth_year = int(dob.split('-')[0])
                if date.today().year - birth_year < 18:
                    errors.append("User must be at least 18 years old.")
            except:
                errors.append("Invalid date of birth format.")
            if not fname or not lname:
                errors.append("First and Last names are required.")
            if phonenumber and not re.match(r"^\+?\d{7,15}$", phonenumber):
                errors.append("Phone number is invalid.")
            if not uname:
                errors.append("Username is required.")
            if not password:
                errors.append("Password is required.")
            if not confirm_password:
                errors.append("Confirm Password is required.")
            if not errors:
                new_user = User(
                    username=uname,
                    firstname=fname,
                    lastname=lname,
                    email=email,
                    phone_number=phonenumber,
                    date_of_birth=dob,
                    avatar=avatar
                )
                new_user.set_password(password)
                new_user.save()
                messages.success(
                    request, "Registration successful. Please log in.")
                return redirect('index')
            else:
                for error in errors:
                    messages.error(request, error)
                return render(request, 'index.html')

        elif action == 'login':
            email = request.POST.get('login_email')
            password = request.POST.get('login_password')
            user = User.objects.filter(email=email).first()

            if user and user.check_password(password):
                request.session['user_id'] = user.id
                messages.success(request, "Login successful.")
                return redirect('home')
            else:
                messages.error(request, "Invalid email or password.")
                return render(request, 'index.html')

    return render(request, 'index.html')


def logout(request):
    request.session.flush()
    messages.success(request, "You have been logged out.")
    return redirect('index')


def home(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to access the home page.")
        return redirect('index')

    user = User.objects.filter(id=user_id).first()
    games = Game.objects.all()

    if not user:
        messages.error(request, "User not found. Please log in again.")
        return redirect('index')

    context = {'user': user, 'games': games}
    return render(request, 'home.html', context)


def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to view your profile.")
        return redirect('index')

    user = User.objects.filter(id=user_id).first()

    if not user:
        messages.error(request, "User not found.")
        return redirect('index')

    if request.method == 'POST':
        user.firstname = request.POST.get('firstname', user.firstname)
        user.lastname = request.POST.get('lastname', user.lastname)
        user.email = request.POST.get('email', user.email)
        user.date_of_birth = request.POST.get(
            'date_of_birth', user.date_of_birth)
        user.phone_number = request.POST.get('phone_number', user.phone_number)

        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']

        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')

    owned_games = Purchase.objects.filter(user=user).select_related('game')
    created_games = Game.objects.filter(created_by=user)
    return render(request, 'profile.html', {
        'user': user,
        'owned_games': owned_games,
        'created_games': created_games,
    })


def edit_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to view your profile.")
        return redirect('index')
    user = User.objects.filter(id=user_id).first()
    if not user:
        messages.error(request, "User not found.")
        return redirect('index')
    return render(request, 'profile.html', {'user': user})


def become_developer(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in first.")
        return redirect('index')

    user = get_object_or_404(User, id=user_id)
    if not user.is_developer:
        user.is_developer = True
        user.save()
        messages.success(request, "You are now a developer!")
    else:
        messages.info(request, "You are already a developer.")

    return redirect('profile')


def add_game(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to add a game.")
        return redirect('index')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        genre = request.POST.get('genre')
        release_date = request.POST.get('release_date')
        description = request.POST.get('description')
        cover_image = request.FILES.get('cover_image')
        price = request.POST.get('price')
        try:
            price = float(price)
            if price < 0:
                messages.error(request, "Price must be free or above zero.")
                return redirect('add_game')
        except ValueError:
            messages.error(request, "Invalid price format.")
            return redirect('add_game')

        # Validation
        if not title or not genre or not release_date or not description or price is None or price == "" or not cover_image:
            messages.error(request, "All fields are required.")
            return redirect('add_game')

        # Mark user as developer
        if not user.is_developer:
            user.is_developer = True
            user.save()

        # Create game
        Game.objects.create(
            title=request.POST.get("title"),
            genre=request.POST.get("genre"),
            description=request.POST.get("description"),
            price=request.POST.get("price"),
            release_date=request.POST.get("release_date"),
            cover_image=request.FILES.get("cover_image"),
            created_by=user
        )

        messages.success(request, f"Game '{title}' added successfully!")
        return redirect('profile')

    return render(request, 'add_game.html', {'user': user, 'mode': 'add'})


def add_to_wishlist(request, game_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to add games to your wishlist.")
        return redirect('index')

    user = get_object_or_404(User, id=user_id)
    game = get_object_or_404(Game, id=game_id)

    # Prevent duplicates
    if Wishlist.objects.filter(user=user, game=game).exists():
        messages.info(request, f"{game.title} is already in your wishlist.")
    else:
        Wishlist.objects.create(user=user, game=game)
        messages.success(request, f"{game.title} added to your wishlist!")

    return redirect('home')


def wishlist(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to view your wishlist.")
        return redirect('index')

    user = get_object_or_404(User, id=user_id)
    sort_by = request.GET.get('sort', 'created_at')

    if sort_by == 'name':
        wishlist_items = Wishlist.objects.filter(
            user=user).order_by('game__title')
    else:  # default: sort by date added
        wishlist_items = Wishlist.objects.filter(
            user=user).order_by('-created_at')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('index')

    wishlist_items = Wishlist.objects.filter(user=user).select_related('game')

    return render(request, 'wishlist.html', {
        'user': user,
        'wishlist_items': wishlist_items,
    })


def remove_from_wishlist(request, game_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to manage your wishlist.")
        return redirect('index')

    user = get_object_or_404(User, id=user_id)
    game = get_object_or_404(Game, id=game_id)

    wishlist_item = Wishlist.objects.filter(user=user, game=game).first()
    if wishlist_item:
        wishlist_item.delete()
        messages.success(request, f"{game.title} removed from your wishlist.")
    else:
        messages.error(request, f"{game.title} is not in your wishlist.")

    return redirect('wishlist')


def add_to_cart(request, game_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to add games to your cart.")
        return redirect('index')

    user = get_object_or_404(User, id=user_id)
    game = get_object_or_404(Game, id=game_id)

    if Cart.objects.filter(user=user, game=game).exists():
        messages.info(request, f"{game.title} is already in your cart.")
    else:
        Cart.objects.create(user=user, game=game)
        messages.success(request, f"{game.title} added to your cart!")

    return redirect('home')


def remove_from_cart(request, game_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to manage your cart.")
        return redirect('index')

    user = get_object_or_404(User, id=user_id)
    game = get_object_or_404(Game, id=game_id)

    cart_item = Cart.objects.filter(user=user, game=game).first()
    if cart_item:
        cart_item.delete()
        messages.success(request, f"{game.title} removed from your cart.")
    else:
        messages.error(request, f"{game.title} is not in your cart.")

    return redirect('cart')


def cart(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to view your cart.")
        return redirect('index')

    user = get_object_or_404(User, id=user_id)
    cart_items = Cart.objects.filter(user=user).select_related('game')

    return render(request, 'cart.html', {
        'user': user,
        'cart_items': cart_items,
    })


def buy_game(request, game_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to buy games.")
        return redirect('index')

    user = get_object_or_404(User, id=user_id)
    game = get_object_or_404(Game, id=game_id)

    # Check if already owned
    if Purchase.objects.filter(user=user, game=game).exists():
        messages.info(request, f"You already own {game.title}.")
        Cart.objects.filter(user=user, game=game).delete()
        Wishlist.objects.filter(user=user, game=game).delete()
        return redirect('profile')

    if game.price == 0:
        # Free game → instantly add to purchases
        Purchase.objects.create(user=user, game=game)
        Wishlist.objects.filter(user=user, game=game).delete()
        # Remove from cart
        Cart.objects.filter(user=user, game=game).delete()
        messages.success(
            request, f"{game.title} added to your library for free!")
    else:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': game.title,
                    },
                    'unit_amount': int(game.price * 100),  # cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(
                '/payment-success?game_id=' + str(game.id)),
            cancel_url=request.build_absolute_uri('/cart'),
        )
        return redirect(session.url, code=303)

    return redirect('profile')  # redirect to owned games page


def move_to_cart(request, game_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to manage your wishlist.")
        return redirect('index')

    user = get_object_or_404(User, id=user_id)
    game = get_object_or_404(Game, id=game_id)

    # Remove from wishlist if exists
    Wishlist.objects.filter(user=user, game=game).delete()

    # Add to cart if not already there
    if not Cart.objects.filter(user=user, game=game).exists():
        Cart.objects.create(user=user, game=game)
        messages.success(request, f"{game.title} moved to your cart.")
    else:
        messages.info(request, f"{game.title} is already in your cart.")

    return redirect('wishlist')


def payment_success(request):
    game_id = request.GET.get('game_id')
    user_id = request.session.get('user_id')
    user = get_object_or_404(User, id=user_id)
    game = get_object_or_404(Game, id=game_id)

    # Double-check ownership
    if not Purchase.objects.filter(user=user, game=game).exists():
        Purchase.objects.create(user=user, game=game)
        Cart.objects.filter(user=user, game=game).delete()
        Wishlist.objects.filter(user=user, game=game).delete()

    messages.success(request, f"You bought {game.title} successfully!")
    return redirect('profile')


def search_games(request):
    query = request.GET.get('q', '').strip()
    qs = Game.objects.all()
    if query:
        qs = qs.filter(title__icontains=query)
    html = render_to_string('partials/game_cards.html', {'games': qs})
    return JsonResponse({'html': html})


def edit_game(request, game_id):
    user_id = request.session.get('user_id')
    user = get_object_or_404(User, id=user_id)
    game = get_object_or_404(Game, id=game_id, created_by=user)

    if not user_id:
        messages.error(request, "Please log in to add a game.")
        return redirect('index')

    if request.method == "POST":
        game.title = request.POST.get("title")
        game.genre = request.POST.get("genre")
        game.description = request.POST.get("description")
        game.price = request.POST.get("price")
        game.release_date = request.POST.get("release_date")
        if "cover_image" in request.FILES:
            game.cover_image = request.FILES["cover_image"]
        game.save()
        messages.success(request, "Game updated successfully!")
        return redirect("profile")

    return render(request, "add_game.html", {"mode": "edit", "game": game, "user": user})


def delete_game(request, game_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to delete your game.")
        return redirect('index')

    user = get_object_or_404(User, id=user_id)
    game = get_object_or_404(Game, id=game_id, created_by=user)

    if request.method == "POST":
        game.delete()
        messages.success(request, "Game deleted successfully!")
        return redirect("profile")


def game_detail(request, game_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please log in to see game details.")
        return redirect('index')

    user = get_object_or_404(User, id=user_id)
    game = get_object_or_404(Game, id=game_id)
    reviews = game.reviews.all()

    # Check ownership
    owns_game = Purchase.objects.filter(user=user, game=game).exists()

    # Check if user is the creator
    is_creator = (game.created_by == user)

    # Existing review
    existing_review = Reviews.objects.filter(user=user, game=game).first()

    if request.method == "POST" and owns_game and not is_creator:
        rate = request.POST.get("rate")
        comment = request.POST.get("comment")

        if rate:
            if existing_review:
                existing_review.rate = rate
                existing_review.comment = comment
                existing_review.save()
                messages.success(request, "Your review has been updated.")
            else:
                Reviews.objects.create(
                    user=user,
                    game=game,
                    rate=rate,
                    comment=comment
                )
                messages.success(request, "Your review has been submitted.")
        return redirect("game_detail", game_id=game_id)

    return render(request, "game_detail.html", {
        "game": game,
        "reviews": reviews,
        "owns_game": owns_game,
        "existing_review": existing_review,
        "is_creator": is_creator,
        "user": user,
    })

from django.db import models
import bcrypt
from django.core.validators import MinValueValidator

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=10, unique=True, null=False)
    firstname = models.CharField(max_length=50, null=False)
    lastname = models.CharField(max_length=50, null=False)
    email = models.EmailField(unique=True, null=False)
    date_of_birth = models.DateField(null=False)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    password = models.CharField(max_length=128, null=False)  # hashed password
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_developer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_password(self, raw_password):
        hashed = bcrypt.hashpw(raw_password.encode(
            'utf-8'), bcrypt.gensalt(rounds=16))
        self.password = hashed.decode('utf-8')

    def check_password(self, raw_password):
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))


class Game(models.Model):
    title = models.CharField(max_length=50, null=False, unique=True)
    genre = models.CharField(max_length=50, null=False)
    release_date = models.DateField(null=False)
    description = models.TextField(null=False)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="games")
    cover_image = models.ImageField(
        upload_to='game_covers/', null=False, blank=False)
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=False,
        validators=[MinValueValidator(0.0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def average_rating(self):
        return self.reviews.aggregate(models.Avg('rate'))['rate__avg'] or 0


class Reviews(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    game = models.ForeignKey(
        'Game', on_delete=models.CASCADE, related_name='reviews')
    rate = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'game')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'game']),
        ]


class Purchase(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'game')
        ordering = ['-purchase_date']
        indexes = [
            models.Index(fields=['user', 'game']),
        ]


class Wishlist(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'game')
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['user', 'game']),
        ]


class DeveloperProfile(models.Model):
    user = models.OneToOneField(
        'User', on_delete=models.CASCADE, related_name='developer_profile')
    studio_name = models.CharField(max_length=100, null=False)
    bio = models.TextField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    logo = models.ImageField(
        upload_to='developer_logos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Cart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cart_items")
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'game')  # prevent duplicates

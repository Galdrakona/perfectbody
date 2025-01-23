from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Model, DateTimeField, CharField, URLField, ForeignKey, SET_NULL, BooleanField, \
    IntegerField, EmailField, TextField, DateField, UniqueConstraint, CASCADE, Avg

from perfectbody.settings import AUTH_USER_MODEL

# from products.models import Product

class UserProfile(AbstractUser):
    PREFERRED_CHANNEL = [('PHONE', 'Telefón'), ('EMAIL', 'Email'), ('POST', 'Pošta')]
    ACCOUNT_TYPES = [('registered', 'Registrovaný uživatel'), ('guest', 'Neregistrovaný uživatel')]

    avatar = URLField(blank=True, null=True)  # url avataru
    phone = CharField(max_length=15, blank=True, null=True)  # telefon
    preferred_channel = CharField(max_length=10, choices=PREFERRED_CHANNEL, default='EMAIL')  # prefer. kom. kanal, vyber z PREFERRED_CHANNEL
    profile_picture = URLField(null=True, blank=True)
    pending_profile_picture = URLField(null=True, blank=True)
    trainer_short_description = TextField(blank=True, null=True)
    trainer_long_description = TextField(blank=True, null=True)
    pending_trainer_short_description = TextField(blank=True, null=True)
    pending_trainer_long_description = TextField(blank=True, null=True)
    date_of_birth = DateField(blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True) # datum vytvoreni uctu
    account_type = CharField(max_length=15, choices=ACCOUNT_TYPES, default='registered')

    def calculate_average_rating(self):
        reviews = self.trainer_reviews.all()
        if not reviews.exists():
            return 0.0
        average = reviews.aggregate(Avg('rating'))['rating__avg']
        return round(average, 2) if average is not None else 0.0

    class Meta:
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.username} - {self.first_name} {self.last_name}'

    def __repr__(self):
        return f'username={self.username},last_login={self.last_login}, is_superuser={self.is_superuser}, is_staff={self.is_staff}'

    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class Address(Model):

    user = ForeignKey(AUTH_USER_MODEL, on_delete=SET_NULL, null=True, blank=True, related_name='addresses')
    first_name = CharField(max_length=255, verbose_name='Jméno')
    last_name = CharField(max_length=255, verbose_name='Příjmení')
    street = CharField(max_length=255, verbose_name='Ulice')
    street_number = CharField(max_length=255, verbose_name='Číslo domu')
    city = CharField(max_length=255, verbose_name='Město')
    postal_code = CharField(max_length=255, verbose_name='PSČ')
    country = CharField(max_length=255, verbose_name='Země', default='Česká republika')
    email = EmailField(verbose_name='E-mail')

    class Meta:
        verbose_name_plural = "addresses"

    def __str__(self):
        return f'{self.first_name} {self.last_name}, {self.street}, {self.street_number}, {self.city}, {self.country}, {self.postal_code}, {self.email}'

    def __repr__(self):
        return f'user_id={self.user_id}, first_name={self.first_name}, last_name={self.last_name}, street={self.street}, city={self.city}, postal_code={self.postal_code}, country={self.country}, email={self.email}'


class TrainersServices(Model):
    trainer = ForeignKey("accounts.UserProfile", on_delete=CASCADE, related_name="services")
    service = ForeignKey("products.Product", on_delete=CASCADE, related_name="trainers")
    trainers_service_description = TextField(blank=False, null=False)
    pending_trainers_service_description = TextField(blank=True, null=True)
    is_approved = BooleanField(default=False)

    class Meta:
        constraints = [UniqueConstraint(fields=['trainer', 'service'], name='unique_trainer_service')]

    def __repr__(self):
        return f"Trainer(full_name={self.trainer.full_name()}, service={self.service.product_name}, is_approved={self.is_approved})"

    def __str__(self):
        return f"{self.trainer.full_name()} - {self.service.product_name} (Approved: {self.is_approved})"

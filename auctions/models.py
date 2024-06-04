from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


CATEGORY = [
    ("S", "Select"),
    ("D", "Deluxe"),
    ("P", "Premium"),
    ("E", " Exclusive"),
    ("U", "Ultra")
]


class Auction(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    imageURL = models.URLField(blank=True)
    category = models.CharField(max_length=1, choices=CATEGORY, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    num_of_bid = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='won_auctions', null=True, blank=True)
    class Meta:
        verbose_name = "Auction"
        verbose_name_plural = "Auctions"

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Bid"
        verbose_name_plural = "Bids"


class Comment(models.Model):
     auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="cmt")
     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cmt")
     content = models.TextField()
     timestamp = models.DateTimeField(auto_now_add=True)
     class Meta:
            verbose_name = "Comment"
            verbose_name_plural = "Comments"

class Watchlist(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="watchlist")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    class Meta:
        verbose_name = "watchlist"
        verbose_name_plural = "watchlists"
        # Forces to not have auction duplicates for one user
        unique_together = ["auction", "user"]

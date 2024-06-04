from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import *
from django import forms


class createForm(forms.Form):
    title = forms.CharField(
        label="Title", max_length=128,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'cols': 20, 'rows': 4})
    )

    starting_bid = forms.DecimalField(
        label="Starting bid",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    imageURL = forms.URLField(
        label="Image URL",
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )

    category = forms.ChoiceField(
        label="Category",
        choices=CATEGORY,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class bidForm(forms.Form):
    amount_of_bid = forms.DecimalField(
        label="Amount of bid",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )


class commentForm(forms.Form):
    content = forms.CharField(
        label="Comment",
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'cols': 10, 'rows': 3})
    )


def index(request):
    auctions = Auction.objects.all()
    return render(request, "auctions/index.html", {
        "auctions": auctions
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create(request):
    if request.method == "POST":
        form = createForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            starting_bid = form.cleaned_data['starting_bid']
            imageURL = form.cleaned_data['imageURL']
            category = form.cleaned_data['category']
            auction = Auction(title=title, description=description, starting_bid=starting_bid,
                              imageURL=imageURL, category=category, owner=request.user)
            auction.save()
            return HttpResponseRedirect(reverse(index))
        else:
            return render(request, 'auctions/create.html', {
                "form": form,
            })
    return render(request, 'auctions/create.html', {
        "form": createForm(),
    })


def view_page(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    user = request.user
    if user.is_authenticated:
        is_in_watchlist = Watchlist.objects.filter(
            auction=auction, user=user).exists()
        if user == auction.winner:
            return render(request, "auctions/view_page.html", {
                    "auction": auction,
                    "bid_form": bidForm(),
                    "comment_form": commentForm(),
                    "alert": "winner_alert",
                    "is_alert": True,
                    "comments": Comment.objects.all(),
                })

    else:
        is_in_watchlist = False
    return render(request, "auctions/view_page.html", {
        "auction": auction,
        "is_in_watchlist": is_in_watchlist,
        "bid_form": bidForm(),
        "comment_form": commentForm(),
        "is_alert": False,
        "comments": Comment.objects.all(),
    })


def watchlist(request):
    user = request.user
    # Lấy danh sách các phiên đấu giá trong watchlist của người dùng
    watchlist_auctions = Watchlist.objects.filter(
        user=user).values_list('auction', flat=True)

    # Lấy các đối tượng phiên đấu giá từ danh sách các ID trong watchlist
    auctions = Auction.objects.filter(id__in=watchlist_auctions)

    return render(request, "auctions/watchlist.html", {
        "auctions": auctions
    })


def add_remove_watchlist(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    user = request.user
    if request.method == "POST":
        button_clicked = request.POST.get("button")
        if button_clicked == "add":
            watchlist = Watchlist(auction=auction, user=user)
            watchlist.save()
        else:
            Watchlist.objects.filter(auction=auction, user=user).delete()

    return HttpResponseRedirect(reverse("viewpage", kwargs={
        "auction_id": auction_id
    }))


def bid(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    user = request.user
    if request.method == "POST":
        form = bidForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount_of_bid']
            if amount >= auction.starting_bid and amount > auction.current_bid:
                bid = Bid(auction=auction, user=user, amount=amount)
                bid.save()

                auction.current_bid = amount
                auction.num_of_bid += 1
                auction.save()
                return render(request, "auctions/view_page.html", {
                    "auction": auction,
                    "bid_form": bidForm(),
                    "comment_form": commentForm(),
                    "alert": "successful_bid",
                    "is_alert": True,
                    "comments": Comment.objects.all()
                })
            else:
                return render(request, "auctions/view_page.html", {
                    "auction": auction,
                    "bid_form": bidForm(),
                    "comment_form": commentForm(),
                    "alert": "failed_bid",
                    "is_alert": True,
                    "comments": Comment.objects.all()
                })
    return HttpResponseRedirect(reverse("viewpage", kwargs={
        "auction_id": auction_id
    }))


def close(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    if request.method == "POST":
        button_clicked = request.POST.get("button")
        if button_clicked == "close":
            best_bid = Bid.objects.filter(auction=auction).order_by("-amount").first()
            # Update auction and watchlist
            if best_bid:
                auction.winner = best_bid.user
                Watchlist.objects.filter(auction=auction).delete()
            auction.is_active = False
            auction.save()
            return render(request, "auctions/view_page.html", {
                "auction": auction,
                "bid_form": bidForm(),
                "comment_form": commentForm(),
                "alert": "successful_close",
                "is_alert": True,
                "comments": Comment.objects.all(),
            })
    return HttpResponseRedirect(reverse("viewpage", kwargs={
        "auction_id": auction_id
    }))

def comment(request, auction_id):
    if request.method == "POST":
        auction = get_object_or_404(Auction, id=auction_id)
        user = request.user
        comment = request.POST.get('comment')
        comment_object = Comment(auction=auction, user=user, content=comment)
        comment_object.save()
        return render(request, "auctions/view_page.html", {
                "auction": auction,
                "bid_form": bidForm(),
                "comment_form": commentForm(),
                "is_alert": False,
                "comments": Comment.objects.all()
            })
def category(request):
    if request.method == "POST":
        category = request.POST.get('category')
        category_name = next(item[1] for item in CATEGORY if item[0] == category)
        auctions = Auction.objects.filter(category=category)
        return render(request, "auctions/category.html",{
            "Category": category_name,
            "auctions": auctions,
            "is_display": True,
        })
    return render(request, "auctions/category.html",{
            "is_display": False,
        })

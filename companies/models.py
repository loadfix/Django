from django.db import models
from django.core.urlresolvers import reverse
import datetime

class Director(models.Model):
    name = models.CharField(max_length=100, null=True)
    age = models.IntegerField(null=True)
    sex = models.CharField(max_length=1, null=True)
    birthdate = models.DateField(null=True)
    last_updated = models.DateTimeField(null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('director:detail', kwargs={'pk': self.pk})


# Company
class Company(models.Model):
    name = models.CharField(max_length=100, null=True)
    founded = models.CharField(max_length=4, null=True)
    market_cap = models.FloatField(null=True)
    website = models.CharField(max_length=250, null=True)
    sector = models.CharField(max_length=100, null=True)
    industry = models.CharField(max_length=100, null=True)
    last_updated = models.DateTimeField(null=True)
    is_current = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('companies:detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


class Exchange(models.Model):
    symbol = models.CharField(max_length=10, null=True)
    reuters_symbol = models.CharField(max_length=10, null=True)
    market_watch_symbol = models.CharField(max_length=10, null=True)

    def __str__(self):
        return str(self.symbol)

class Listing(models.Model):
    company = models.ForeignKey(Company, related_name='tickers', on_delete=models.CASCADE)
    exchange = models.ForeignKey(Exchange, related_name='exchange', on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10, null=True)
    last_updated = models.DateTimeField(null=True)
    is_current = models.BooleanField(default=True)

    def __str__(self):
        return str(self.ticker)


class BoardMember(models.Model):
    company = models.ForeignKey(Company, related_name='board', on_delete=models.CASCADE, null=True)
    director = models.ForeignKey(Director, related_name='boards', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=250, null=True)
    start_date = models.DateField(null=True)
    is_current = models.BooleanField(default=True)
    is_independent = models.BooleanField(default=True)
    last_updated = models.DateTimeField(null=True)

    def __str__(self):
        return self.company.name

class Version(models.Model):
    last_update = models.DateTimeField(null=True)
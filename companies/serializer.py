from rest_framework import serializers
from datetime import datetime
from .models import Company, Listing, Director, BoardMember, Exchange


class CompanySerializer(serializers.ModelSerializer):

    tickers = serializers.StringRelatedField(many=True, required=False)

    # def create(self, validated_data):
    #     return Company.objects.create(validated_data)

    def update(self, company):
        """
        Update and return an existing `Company` instance, given the validated data.
        """

        company.name = self.data['name']
        company.founded = self.data['founded']
        company.market_cap = self.data['market_cap']
        company.website = self.data['website']
        company.sector = self.data['sector']
        company.industry = self.data['industry']
        company.is_current = bool(self.data['is_current'])
        company.last_updated = datetime.now()
        company.save()

        return company

    def delete(self, company):
        company.delete()
        return None

    class Meta:
        model = Company
        # fields = ['ticker', 'volume']
        fields = '__all__' # Returns all fields


class TickerSerializer(serializers.ModelSerializer):

    def update(self, listing):
        """
        Update and return an existing `Listing` instance, given the validated data.
        """
        listing.ticker = self.data['ticker']
        listing.company = Company.objects.filter(id=self.data['company'])[0]
        listing.exchange = self.data['exchange']
        listing.is_current = bool(self.data['is_current'])
        listing.last_updated = datetime.now()
        listing.save()

        return listing

    class Meta:
        model = Listing
        # fields = ['ticker', 'volume']
        fields = '__all__' # Returns all fields

class DirectorSerializer(serializers.ModelSerializer):

    boards = serializers.StringRelatedField(many=True, required=False)

    def update(self, director):
        """
        Update and return an existing `Director` instance, given the validated data.
        """
        director.name = self.data['name']
        director.age = self.data['age']
        director.sex = self.data['sex']
        director.last_updated = datetime.now()
        director.save()

        return director

    class Meta:
        model = Director
        # fields = ['ticker', 'volume']
        fields = '__all__' # Returns all fields

class BoardMemberSerializer(serializers.ModelSerializer):

    def update(self, boardmember):
        """
        Update and return an existing `BoardMember` instance, given the validated data.
        """
        boardmember.title = self.data['title']
        boardmember.start_date = self.data['start_date']
        boardmember.is_current = bool(self.data['is_current'])
        boardmember.is_independent = bool(self.data['is_independent'])
        boardmember.company = Company.objects.filter(id=self.data['company'])[0]
        boardmember.director = Director.objects.filter(id=self.data['director'])[0]
        boardmember.last_updated = datetime.now()
        boardmember.save()

        return boardmember

    class Meta:
        model = BoardMember
        fields = '__all__' # Returns all fields


class ExchangeSerializer(serializers.ModelSerializer):

    def update(self, exchange):
        """
        Update and return an existing `Exchange` instance, given the validated data.
        """
        exchange.name = self.data['name']
        exchange.symbol = self.data['symbol']
        exchange.website = self.data['website']
        exchange.reuters_symbol = self.data['reuters_symbol']
        exchange.market_watch_symbol = self.data['market_watch_symbol']
        exchange.last_updated = datetime.now()
        exchange.save()

        return exchange

    class Meta:
        model = Exchange
        fields = '__all__' # Returns all fields
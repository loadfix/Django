from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views import generic
from django.views.generic import View

from django.db.models import Count

from .models import Company, Director, Listing, Version, BoardMember, Exchange
from .forms import UserForm
from .serializer import CompanySerializer, TickerSerializer, DirectorSerializer, BoardMemberSerializer


# Bokeh
from django.shortcuts import render, render_to_response
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.charts import Histogram
import numpy
import scipy
from scipy import special


class BoardStatistics:
    mean = float
    median = float
    sd = float
    even = int
    odd = int

    def __init__(self, data_array):
        self.mean = numpy.mean(numpy.array(data_array))
        self.median =  numpy.median(numpy.array(data_array))
        self.sd = numpy.std(numpy.array(data_array))
        self.odd = sum((x%2 for x in data_array))
        self.even = sum((1-x%2 for x in data_array))


# Index Page
class IndexView(View):
    template_name = 'companies/index.html'
    context_object_name = 'all_companies'

    def get(self, request):
        nyse = Listing.objects.filter(exchange='2').count()
        nasdaq = Listing.objects.filter(exchange='3').count()
        amex = Listing.objects.filter(exchange='1').count()
        asx = Listing.objects.filter(exchange='4').count()


        exchanges = ["NYSE", "NASDAQ", "AMEX", "ASX"]
        values = [nyse, nasdaq, amex, asx  ]

        # Bar Chart
        plot = figure(plot_width=400,
                      plot_height=400,
                      x_range=exchanges,
                      title="Number of Listings")
        plot.vbar(x=exchanges,
                  width=0.5,
                  bottom=0,
                  top=values,
                  color="navy")

        script, div = components(plot)

        #average_board_size = BoardMember.objects.values_list('id', flat=True)
        #average_board_size = BoardMember.objects.all().values('id').query
        #average_board_size = list(BoardMember.objects.values_list('id', flat=True))

        board_sizes = list(BoardMember.objects.all().values('company').annotate(Count('director')).values_list('director__count', flat=True))
        board_statistics = BoardStatistics(board_sizes)

        director_ages = list(filter(None, Director.objects.all().values_list('age', flat=True)))
        director_statistics = BoardStatistics(director_ages)

        plot = Histogram(board_sizes)

        histogram_script, histogram_div = components(plot)

        return render(request, self.template_name, {
            'bokeh_script': script,
            'bokeh_div': div,
            'bokeh_histogram_div': histogram_div,
            'bokeh_histogram_script': histogram_script,
            'total_companies': Company.objects.count(),
            'total_directors': Director.objects.count(),
            'last_update': str(Version.last_update),
            'total_listings': Listing.objects.count(),
            'board_statistics': board_statistics,
            'director_statistics': director_statistics
        })

# Company List
class CompanyView(generic.ListView):
    template_name = 'companies/companies.html'
    context_object_name = 'all_companies'
    paginate_by = 50

    def get_queryset(self):
        return Company.objects.all()


# Search Results
class SearchResults(generic.ListView):
    template_name = 'companies/companies.html'
    paginate_by = 50
    context_object_name = 'all_companies'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return Company.objects.filter(name__icontains=query)



# Director List
class DirectorView(generic.ListView):
    template_name = 'companies/directors.html'
    context_object_name = 'all_directors'
    paginate_by = 50

    def get_queryset(self):
        return Director.objects.all()


# Ticker List
class ListingView(generic.ListView):
    template_name = 'companies/listings.html'
    context_object_name = 'all_listings'
    paginate_by = 50

    def get_queryset(self):
        return Listing.objects.all()


#
# List all companies (get) or create a new one (post)
#
class CompanyList(APIView):

    def get(self, request):

        company_name = self.request.query_params.get('name', None)
        company_search = self.request.query_params.get('search', None)
        company_id = self.request.query_params.get('id', None)
        company_ticker = self.request.query_params.get('ticker', None)
        company_exchange = self.request.query_params.get('exchange', None)

        companies = Company.objects.all()
        tickers = Listing.objects.all()

        if company_exchange is not None:
            tickers = tickers.filter(exchange=company_exchange)
            companies = companies.filter(id__in=tickers.values('company'))

        if company_ticker is not None:
            tickers = tickers.filter(ticker=company_ticker)
            companies = companies.filter(id__in=tickers.values('company'))

        if company_search is not None:
            companies = companies.filter(name__contains=company_search)

        if company_name is not None:
            companies = companies.filter(name=company_name)

        if company_id is not None:
            companies = companies.filter(id=company_id)

        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        serializer = CompanySerializer(data=request.data)
        company_id = request.data['id']
        try:
            instance = Company.objects.filter(id=company_id)[0]
            if serializer.is_valid():
                serializer.update(instance)
            return Response(instance, status=status.HTTP_200_OK)
        except Exception as e:
            # Not found
            return Response(None, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        serializer = CompanySerializer(data=request.data)
        company_id = self.request.query_params.get('id', None)
        try:
            instance = Company.objects.filter(id=company_id)[0]
            if serializer.is_valid():
                serializer.delete(instance)
            return Response(None, status=status.HTTP_200_OK)
        except Exception as e:
            # Not found
            return Response(None, status=status.HTTP_404_NOT_FOUND)


class TickerList(APIView):

    def get(self, request):
        ticker_name = self.request.query_params.get('ticker', None)
        ticker_id = self.request.query_params.get('id', None)
        ticker_exchange = self.request.query_params.get('exchange', None)
        ticker_company = self.request.query_params.get('company_id', None)

        tickers = Listing.objects.all()

        if ticker_name is not None:
            tickers = tickers.filter(ticker=ticker_name)

        if ticker_id is not None:
            tickers = tickers.filter(id=ticker_id)

        if ticker_exchange is not None:
            tickers = tickers.filter(exchange=ticker_exchange)

        if ticker_company is not None:
            tickers = tickers.filter(company=ticker_company)

        serializer = TickerSerializer(tickers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TickerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        serializer = TickerSerializer(data=request.data)
        ticker_id = request.data['id']
        try:
            instance = Listing.objects.filter(id=ticker_id)[0]
            if serializer.is_valid():
                serializer.update(instance)
            return Response(instance, status=status.HTTP_200_OK)
        except Exception as e:
            # Not found
            print(str(e))
            return Response(None, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        ticker_id = self.request.query_params.get('id', None)

        if ticker_id is not None:
            ticker = Listing.objects.filter(id=ticker_id)[0]
            try:
                ticker.delete()
                return Response(None, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(None, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(None, status=status.HTTP_404_NOT_FOUND)


class DirectorList(APIView):
    def get(self, request):
        director_name = self.request.query_params.get('name', None)
        director_search = self.request.query_params.get('search', None)
        director_id = self.request.query_params.get('id', None)
        director_age = self.request.query_params.get('age', None)
        director_sex = self.request.query_params.get('sex', None)

        directors = Director.objects.all()

        if director_name is not None:
            print("Setting director_name to: " + director_name)
            directors = directors.filter(name=director_name)

        if director_search is not None:
            directors = directors.filter(name__contains=director_search)

        if director_id is not None:
            directors = directors.filter(id=director_id)

        if director_age is not None:
            directors = directors.filter(age=director_age)

        if director_sex is not None:
            directors = directors.filter(sex=director_sex)

        serializer = DirectorSerializer(directors, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DirectorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        serializer = DirectorSerializer(data=request.data)
        director_id = request.data['id']
        try:
            instance = Director.objects.filter(id=director_id)[0]
            if serializer.is_valid():
                serializer.update(instance)
            return Response(instance, status=status.HTTP_200_OK)
        except Exception as e:
            # Not found
            print(str(e))
            return Response(None, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        director_id = self.request.query_params.get('id', None)

        if director_id is not None:
            director = Director.objects.filter(id=director_id)[0]
            try:
                director.delete()
                return Response(None, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(None, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(None, status=status.HTTP_404_NOT_FOUND)


class BoardMemberList(APIView):

    def get(self, request):

        boardmember_id = self.request.query_params.get('id', None)
        boardmember_director = self.request.query_params.get('director', None)
        boardmember_company = self.request.query_params.get('company', None)
        boardmember_title = self.request.query_params.get('title', None)
        boardmember_is_independent = self.request.query_params.get('is_independent', None)

        boardmembers = BoardMember.objects.all()

        if boardmember_id is not None:
            boardmembers = boardmembers.filter(id=boardmember_id)

        if boardmember_director is not None:
            boardmembers = boardmembers.filter(director=boardmember_director)

        if boardmember_company is not None:
            boardmembers = boardmembers.filter(company=boardmember_company)

        if boardmember_title is not None:
            boardmembers = boardmembers.filter(title=boardmember_title)

        if boardmember_is_independent is not None:
            boardmembers = boardmembers.filter(is_independent=boardmember_is_independent)

        serializer = BoardMemberSerializer(boardmembers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BoardMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            serializer = BoardMemberSerializer(data=request.data)

            boardmember_id = request.data['id']
            instance = BoardMember.objects.filter(id=boardmember_id)[0]
            if serializer.is_valid():
                serializer.update(instance)
                return Response(None, status=status.HTTP_200_OK)
            else:
                return Response(None, status=status.HTTP_200_OK)
        except Exception as e:
            # Not found
            print(str(e))
            print(serializer.error_messages)
            print(serializer.errors)
            return Response(None, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        boardmember_id = self.request.query_params.get('id', None)

        if boardmember_id is not None:
            director = BoardMember.objects.filter(id=boardmember_id)[0]
            try:
                director.delete()
                return Response(None, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(None, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(None, status=status.HTTP_404_NOT_FOUND)


# Company Detail View
class DetailView(generic.DetailView):
    model = Company, BoardMember

    template_name = 'companies/detail.html'

    def get(self, request, pk):

        try:
            percentage_independent = BoardMember.objects.filter(company=pk, is_independent=True).count() / BoardMember.objects.filter(company=pk).count()
        except Exception as e:
            percentage_independent = "N/A"

        return render(request, self.template_name, context={
            'board_members': BoardMember.objects.filter(company=pk),
            'company': Company.objects.filter(id=pk)[0],
            'is_independent': BoardMember.objects.filter(company=pk, is_independent=True).count(),
            'percentage_independent': percentage_independent
        })


# Director Detail View
class DirectorDetailView(generic.DetailView):
    model = Director
    template_name = 'companies/director_detail.html'


# Listing Detail View
class ListingDetailView(generic.DetailView):
    model = Listing
    template_name = 'companies/listing_detail.html'

#
# CRUD Pages
#
class CompanyCreate(CreateView):
    model = Company
    fields = '__all__'


class CompanyUpdate(UpdateView):
    model = Company
    fields = '__all__'


class CompanyDelete(DeleteView):
    model = Company
    success_url = reverse_lazy('companies:index')


class UserFormView(View):
    form_class = UserForm
    template_name = 'companies/registration_form.html'

    # Display a blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form })

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            # Clean (normaised) data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            # Returns user object if credentials are correct
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('companies:index')

        return render(request, self.template_name, {'form': form})


class BokehView(View):
    model = Company
    template_name = 'companies/graphs.html'

    def get(self, request):

        nyse = Company.objects.filter(exchange='NYSE').count() / Company.objects.count()
        nasdaq = Company.objects.filter(exchange='NASDAQ').count() / Company.objects.count()
        amex = Company.objects.filter(exchange='AMEX').count() / Company.objects.count()

        exchanges = ["NYSE", "NASDAQ", "AMEX"]
        values = [nyse, nasdaq, amex]

        # Bar Chart
        plot = figure(plot_width=400,
                      plot_height=400,
                      x_range=exchanges,
                      title="Number of Listed Companies")
        plot.vbar(x=exchanges,
                  width=0.5,
                  bottom=0,
                  top=values,
                  color="navy")

        # Pie Chart
        # percents = [0, nyse, nasdaq, amex, 1]
        # starts = [p * 2 * pi for p in percents[:-1]]
        # ends = [p * 2 * pi for p in percents[1:]]
        # colors = ["red", "green", "blue"]
        # plot = figure(x_range=(-1, 1), y_range=(-1, 1))
        # plot.wedge(x=0, y=0, radius=1, start_angle=starts, end_angle=ends, color=colors)

        # Histogram
        # plot = figure(title="Normal Distribution (μ=0, σ=0.5)", tools="save",
        #             background_fill_color="#E8DDCB")
        # mu, sigma = 0, 0.5
        # measured = numpy.random.normal(mu, sigma, 1000)
        # hist, edges = numpy.histogram(measured, density=True, bins=50)
        # x = numpy.linspace(-2, 2, 1000)
        # pdf = 1 / (sigma * numpy.sqrt(2 * numpy.pi)) * numpy.exp(-(x - mu) ** 2 / (2 * sigma ** 2))
        # cdf = (1 + scipy.special.erf((x - mu) / numpy.sqrt(2 * sigma ** 2))) / 2
        # plot.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
        #         fill_color="#036564", line_color="#033649")
        # plot.line(x, pdf, line_color="#D95B43", line_width=8, alpha=0.7, legend="PDF")
        # plot.line(x, cdf, line_color="white", line_width=2, alpha=0.7, legend="CDF")
        # plot.legend.location = "center_right"
        # plot.legend.background_fill_color = "darkgrey"
        # plot.xaxis.axis_label = 'x'
        # plot.yaxis.axis_label = 'Pr(x)'


        # Store components
        script, div = components(plot)

        # Feed them to the Django template.
        return render(request, self.template_name, {'bokeh_script': script, 'bokeh_div': div})


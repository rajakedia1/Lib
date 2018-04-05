from django.db.models import Q
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book, Author, BookInstance, Genre, Review
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from .forms import ReviewBookForm

# Create your views here.

def index(request):
    """
    View function for home page of site.
    """
    # Generate counts of some of the main objects
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()  # The 'all()' is implied by default.
    num_visits=request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits+1


    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={'num_books':num_books,'num_instances':num_instances,'num_instances_available':num_instances_available,'num_authors':num_authors,'num_visits':num_visits},
    )

class BookListView(generic.ListView):
    model = Book

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Generic class-based view listing books on loan to current user. 
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


def review_book(request, pk):

    if request.method == 'POST':
        form = ReviewBookForm(request.POST)

        if form.is_valid():
            review_inst = Review()
            book_inst = get_object_or_404(Book, pk=pk)
            review_inst.review = form.cleaned_data['new_review']
            review_inst.book = book_inst
            
            review_inst.save()

            return HttpResponseRedirect(reverse('books'))

    else:
        form = ReviewBookForm()

    return render(request, 'catalog/book_review.html', {'form': form,})


def SearchBook(request):
    template = 'catalog/search_booklist.html'
    query = request.GET.get('q','')
    results = Book.objects.filter(title__icontains=query)
    context = {
    'items' : results
    }
    return render( request, template, context)

def SearchAuthor(request):
    template = 'catalog/search_author.html'
    query = request.GET.get('q','')
    results = Author.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query))
    context = {
    'items' : results
    }
    return render(request, template, context)







# def like_book(request, pk):
#     if request.method == 'POST':
#         book_inst = get_object_or_404(Book, pk=pk)
#         book.like = book.like+1
#         return HttpResponseRedirect(reverse('books'))

# def dislike_book(request,pk):
#     if request.method == 'POST':
#         book_inst = get_object_or_404(Book, pk=pk)
#         book.dislike = book.dislike+1
#         return HttpResponseRedirect(reverse('books'))
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.urls import reverse
from django.db.models import F
from django.http import HttpResponseRedirect
from django.views import generic
from .models import Choice, Question
from django.db.models import Count     # to discard question without choices
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import ChoiceForm


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return (
            Question.objects
            .filter(pub_date__lte=timezone.now())
            # .annotate(num_choices=Count('choice'))            ## if we want to exclude questions without choices
            # .filter(num_choices__gt=0)
            .order_by("-pub_date")[:5]
        )


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ChoiceForm()
        return context

    def post(self, request, **kwargs):
        self.object = self.get_object()
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.question = self.object
            choice.save()
            return redirect('polls:detail', pk=self.object.pk)
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


class QuestionCreateView(CreateView):
    model = Question
    template_name = 'polls/question_form.html'
    fields = ['question_text']
    extra_context = {'title': 'Add Question'}

    def get_success_url(self):
        return reverse('polls:detail', args=[self.object.id])


class QuestionUpdateView(UpdateView):
    model = Question
    template_name = 'polls/question_form.html'
    fields = ['question_text']
    extra_context = {'title': 'Edit Question'}

    def get_success_url(self):
        return reverse('polls:detail', args=[self.object.id])


class QuestionDeleteView(DeleteView):
    model = Question
    template_name = 'polls/question_confirm_delete.html'
    success_url = reverse_lazy('polls:index')

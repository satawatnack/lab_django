from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Count
from django.forms import formset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect


# Create your views here.
from .forms import PollForm, PollModelForm, QuestionForm
from .models import Poll, Answer, Question

def my_login(request):
    context = {}

    if request.method=="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.POST.get('next_url')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('index')
        else:
            context['username'] = username
            context['password'] = password
            context['error'] = 'Wrong username or password!'
            print(context)
    next_url = request.GET.get('next')
    if next_url:
        context['next_url'] = next_url
    return render(request, template_name='polls/login.html', context=context)

def my_logout(request):
    logout(request)
    return redirect('login')

def index(request):
    poll_list = Poll.objects.annotate(question_count=Count('question'))

    # poll_list = Poll.objects.filter(del_flag=False, id__gt=2)
    # poll_list = Poll.objects.all()

    print(poll_list.query)
    # for poll in poll_list:
    #     question_count = Question.objects.filter(poll_id=poll.id).count()
    #     poll.question_count = question_count

    context = {
        'page_title': 'My Polls',
        'poll_list': poll_list
    }

    return render(request, template_name='polls/index.html', context=context)
@login_required
@permission_required('poll.view_poll')
def detail(request, poll_id):

    poll = Poll.objects.get(pk=poll_id)

    if request.method == 'POST':
        for question in poll.question_set.all():
            name = 'choice' + str(question.id)
            choice_id = request.POST.get(name)

            if choice_id:
                try:
                    ans = Answer.objects.get(question_id=question.id)
                    ans.choice_id = choice_id
                    ans.save()
                except Answer.DoesNotExist:
                    Answer.objects.create(
                        choice_id=choice_id,
                        question_id=question.id
                    )
            print(choice_id)
    print(request.GET)
    return render(request, 'polls/detail.html', {'poll': poll})

@login_required
@permission_required('polls.add_poll')
def create(request):
    context = {}
    QuestionFormSet = formset_factory(QuestionForm, extra=2, max_num=10)
    if request.method == 'POST':
        form = PollModelForm(request.POST)
        formset = QuestionFormSet(request.POST)
        if form.is_valid():
            poll = form.save()
            if formset.is_valid():
                for question_form in formset:
                    Question.objects.create(
                        text=question_form.cleaned_data.get('text'),
                        type=question_form.cleaned_data.get('type'),
                        poll=poll
                    )
                context['success'] = "poll %s is successfully!" %poll.title
        # form = PollForm(request.POST)
        #
        # if form.is_valid():
        #     poll = Poll.objects.create(
        #         title=form.cleaned_data.get('title'),
        #         start_date=form.cleaned_data.get('start_date'),
        #         end_date=form.cleaned_data.get('end_date'),
        #
        #     )
        #     for i in range(1, form.cleaned_data.get('no_questions')+1):
        #         Question.objects.create(
        #             text='QQQQ'+str(i),
        #             type='01',
        #             poll=poll
        #         )
    else:
        # form = PollForm()
        form = PollModelForm()
        formset = QuestionFormSet()


    context['form'] = form
    context['formset'] = formset

    return render(request, 'polls/create.html', context=context)

@login_required
@permission_required('polls.change_poll')
def update(request, poll_id):
    poll = Poll.objects.get(id=poll_id)

    if request.method == 'POST':
        form = PollModelForm(request.POST, instance=poll)
        if form.is_valid():
            form.save()
    else:
        # form = PollForm()
        form = PollModelForm(instance=poll)
        #instance คือการดึงข้อมูลมาโชวใน inputfield รีเฟรชแล้วข้อมูลไม่หาย


    context = {
        'form': form,
        'poll_obj': poll
    }

    return render(request, 'polls/update.html', context=context)
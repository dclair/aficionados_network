from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView
from django.urls import reverse_lazy
from .models import Posts
from .forms import PostCreateForm


class PostCreateView(CreateView):
    model = Posts
    form_class = PostCreateForm
    template_name = "posts/post_form.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PostDetailView(DetailView):
    model = Posts
    template_name = "posts/post_detail.html"
    context_object_name = "post"


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Posts, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect("home")


@login_required
def like_post_ajax(request, pk):
    if request.method == "POST":
        post = get_object_or_404(Posts, pk=pk)

        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
            message = "Me gusta eliminado."
        else:
            post.likes.add(request.user)
            liked = True
            message = "Me gusta agregado."

        return JsonResponse(
            {"liked": liked, "count": post.likes.count(), "message": message}
        )

    return JsonResponse({"error": "Método no permitido"}, status=405)

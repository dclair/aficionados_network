from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView
from django.urls import reverse_lazy
from .models import Posts
from .forms import PostCreateForm, CommentForm


class PostCreateView(CreateView):
    model = Posts
    form_class = PostCreateForm
    template_name = "posts/post_create.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PostDetailView(DetailView):
    model = Posts
    template_name = "posts/post_detail.html"
    context_object_name = "post"

    # context_object_name = "post"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = CommentForm()
        return context


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


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Posts, pk=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                # Usa el perfil del usuario que ya existe
                profile = request.user.userprofile
                return JsonResponse(
                    {
                        "success": True,
                        "comment": comment.comment,
                        "username": comment.user.username,
                        "user_id": comment.user.id,
                        "avatar_url": (
                            profile.image.url
                            if hasattr(request.user, "userprofile")
                            else "/static/images/default-avatar.png"
                        ),
                        "comment_id": comment.id,
                        "created_at": "Ahora mismo",
                    }
                )

            return redirect("posts:post_detail", pk=post_id)
    return redirect("posts:post_detail", pk=post_id)

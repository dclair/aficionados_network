from django.shortcuts import get_object_or_404, redirect
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView
from django.urls import reverse_lazy
from .models import Posts
from .forms import PostCreateForm, CommentForm
from notifications.models import Notification


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
def toggle_like(request):
    if request.method == "POST":
        data = json.loads(request.body)
        post_id = data.get("post_id")
        post = Posts.objects.get(pk=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        return JsonResponse({"liked": liked, "count": post.likes.count()})
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

            # --- INICIO LÓGICA DE NOTIFICACIÓN ---
            # Solo enviamos notificación si el que comenta es otra persona
            if post.user != request.user:
                Notification.objects.create(
                    recipient=post.user,  # El dueño del post
                    sender=request.user,  # El que escribe el comentario
                    notification_type="comment",
                    post=post,
                    comment=comment,  # ¡Aquí vinculamos el comentario exacto!
                )
            # --- FIN LÓGICA DE NOTIFICACIÓN ---

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                # Intentamos obtener el perfil para el avatar
                # Nota: revisa si el modelo se llama 'userprofile' o 'profile'
                profile = getattr(request.user, "userprofile", None) or getattr(
                    request.user, "profile", None
                )

                avatar_url = "/static/images/default-avatar.png"
                if profile and hasattr(profile, "image") and profile.image:
                    avatar_url = profile.image.url
                elif (
                    profile
                    and hasattr(profile, "profile_picture")
                    and profile.profile_picture
                ):
                    avatar_url = profile.profile_picture.url

                return JsonResponse(
                    {
                        "success": True,
                        "comment": comment.comment,
                        "username": comment.user.username,
                        "user_id": comment.user.id,
                        "avatar_url": avatar_url,
                        "comment_id": comment.id,
                        "created_at": "Ahora mismo",
                    }
                )

            return redirect("posts:post_detail", pk=post_id)

    return redirect("posts:post_detail", pk=post_id)

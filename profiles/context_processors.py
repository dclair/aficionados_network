def user_hobbies_processor(request):
    """
    Hace que las aficiones del usuario estén disponibles
    en todos los templates del sitio.
    """
    if request.user.is_authenticated and hasattr(request.user, "profile"):
        # Traemos los hobbies directamente de la relación ManyToMany que ya tienes
        return {"my_hobbies": request.user.profile.hobbies.all()}
    return {"my_hobbies": []}

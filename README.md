# views.py
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        mobile   = request.POST['mobile']
        password = request.POST['password']

        try:
            user = UserDetail.objects.get(mobile=mobile)   # your custom model
        except UserDetail.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('login')

        if check_password(password, user.password):
            # Tell Django “this user is now authenticated”
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user)
            return redirect('upload')                      # success!
        else:
            messages.error(request, "Incorrect password.")
            return redirect('login')

    return render(request, 'login.html')
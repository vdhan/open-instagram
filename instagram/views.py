import hashlib
import json
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from .models import *
from open_instagram.settings import *
from django.utils import timezone
from uuid import uuid4


@csrf_exempt
@require_POST
def signup(request):
    data = json.loads(request.body.decode())
    email = data.get('email')
    pwd = data.get('password')
    if not (email and pwd):
        res = json.dumps({
            'message': 'Enter both email and password'
        })
        return HttpResponse(res, 'application/json', 400)

    try:
        validate_email(email)
    except ValidationError:
        res = json.dumps({
            'message': 'Invalid email'
        })
        return HttpResponse(res, 'application/json', 400)

    if not pwd.strip():
        res = json.dumps({
            'message': 'Password is null'
        })
        return HttpResponse(res, 'application/json', 400)

    try:
        User.objects.get(email=email)
    except User.DoesNotExist:
        p = hashlib.sha256(pwd.encode()).hexdigest()
        User.objects.create(email=email, password=p)
    else:
        res = json.dumps({
            'message': 'Email registered'
        })
        return HttpResponse(res, 'application/json', 400)

    salt = str(uuid4())
    code = hashlib.sha256((email + salt).encode()).hexdigest()
    WaitVerify.objects.create(email=email, code=code)

    sbj = 'Registration'
    html = '<a href="' + URL + '/verify/' + code + '">Verify link</a>'
    frm = 'info@localhost'
    to = [email]
    send_mail(sbj, '', frm, to, html_message=html)

    res = json.dumps({
        'message': 'Register success'
    })
    return HttpResponse(res, 'application/json')


@require_GET
def verify(request, code):
    try:
        w = WaitVerify.objects.get(code=code)
    except WaitVerify.DoesNotExist:
        res = json.dumps({
            'message': 'Invalid code'
        })
        return HttpResponse(res, 'application/json', 400)

    user = User.objects.get(email=w.email)
    user.verified = 1
    user.save()
    res = json.dumps({
        'message': 'Verify success'
    })
    return HttpResponse(res, 'application/json')


@csrf_exempt
@require_POST
def login(request):
    data = json.loads(request.body.decode())
    email = data.get('email')
    pwd = data.get('password')
    if not (email and pwd):
        res = json.dumps({
            'message': 'Enter both email and password'
        })
        return HttpResponse(res, 'application/json', 400)

    try:
        validate_email(email)
    except ValidationError:
        res = json.dumps({
            'message': 'Invalid email'
        })
        return HttpResponse(res, 'application/json', 400)

    if not pwd.strip():
        res = json.dumps({
            'message': 'Password is null'
        })
        return HttpResponse(res, 'application/json', 400)

    try:
        user = User.objects.get(email=email, verified=1)
    except User.DoesNotExist:
        res = json.dumps({
            'message': 'Account did not create or validate'
        })
        return HttpResponse(res, 'application/json', 400)

    date = str(timezone.now())
    token = hashlib.sha256((email + date).encode()).hexdigest()
    user.access_token = token
    user.save()

    res = json.dumps({
        'access_token': token
    })
    return HttpResponse(res, 'application/json')


@require_GET
def explorer(request):
    token = request.GET.get('access_token')
    if not token:
        res = json.dumps({
            'message': 'You do not have permission to access'
        })
        return HttpResponse(res, 'application/json', 403)

    try:
        User.objects.get(access_token=token)
    except User.DoesNotExist:
        res = json.dumps({
            'message': 'You do not have permission to access'
        })
        return HttpResponse(res, 'application/json', 403)

    images = Image.objects.all()
    img = []
    for item in images:
        data = {
            'id': item.id,
            'image': URL + item.image.url,
            'title': item.title,
            'comments': item.count
        }
        img.append(data)

    res = json.dumps({
        'images': img
    })
    return HttpResponse(res, 'application/json')


@require_GET
def detail(request, _id):
    token = request.GET.get('access_token')
    if not token:
        res = json.dumps({
            'message': 'You do not have permission to access'
        })
        return HttpResponse(res, 'application/json', 403)

    try:
        User.objects.get(access_token=token)
    except User.DoesNotExist:
        res = json.dumps({
            'message': 'You do not have permission to access'
        })
        return HttpResponse(res, 'application/json', 403)

    img = Image.objects.get(id=_id)
    comments = Comment.objects.filter(img_id=_id)
    cmt = []
    for item in comments:
        data = {
            'email': item.email,
            'content': item.content,
            'time': item.created
        }
        cmt.append(data)

    res = json.dumps({
        'image': URL + img.image.url,
        'title': img.title,
        'comments': cmt
    })
    return HttpResponse(res, 'application/json')


@csrf_exempt
@require_POST
def upload(request):
    token = request.POST.get('access_token')
    if not token:
        res = json.dumps({
            'message': 'You do not have permission to access'
        })
        return HttpResponse(res, 'application/json', 403)

    try:
        user = User.objects.get(access_token=token)
    except User.DoesNotExist:
        res = json.dumps({
            'message': 'You do not have permission to access'
        })
        return HttpResponse(res, 'application/json', 403)

    title = request.POST.get('title', 'title')
    img = request.FILES.get('image')
    if not img:
        res = json.dumps({
            'message': 'No image upload'
        })
        return HttpResponse(res, 'application/json', 400)

    Image.objects.create(email=user.email, image=img, title=title)
    res = json.dumps({
        'message': 'Upload success'
    })
    return HttpResponse(res, 'application/json')


@csrf_exempt
@require_POST
def comment(request):
    data = json.loads(request.body.decode())
    token = data.get('access_token')
    if not token:
        res = json.dumps({
            'message': 'You do not have permission to access'
        })
        return HttpResponse(res, 'application/json', 403)

    try:
        user = User.objects.get(access_token=token)
    except User.DoesNotExist:
        res = json.dumps({
            'message': 'You do not have permission to access'
        })
        return HttpResponse(res, 'application/json', 403)

    _id = data.get('id')
    content = data.get('content')
    if not content.strip():
        res = json.dumps({
            'message': 'You have no comment'
        })
        return HttpResponse(res, 'application/json', 400)

    Comment.objects.create(img_id=_id, email=user.email, content=content)
    img = Image.objects.get(id=_id)
    img.count += 1
    img.save()

    res = json.dumps({
        'message': 'Comment success'
    })
    return HttpResponse(res, 'application/json')

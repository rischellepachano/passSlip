from rest_framework import viewsets
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import json
import random
import string
from datetime import datetime
from django.utils import timezone

from .models import User
from .models import Slip
from .models import Code
from .models import Admin


from .serializers import UserSerializer
from .serializers import SlipSerializer
from .serializers import CodeSerializer
from .serializers import AdminSerializer

from django.core.exceptions import ObjectDoesNotExist


def get_latest_item(request):
    try:
        # Fetch the latest slip based on the id field (which is auto-incremented)
        latest_item = Code.objects.all().order_by('-id').first()  # Order by descending id
        
        if latest_item:
            return JsonResponse({
                'id': latest_item.id,
                'qr': latest_item.qr,
                'user': latest_item.user,
                'date': latest_item.date,
            })
        else:
            return JsonResponse({'error': 'No items found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def get_user_by_id(request, user_id):
    try:
        # Fetch the user by ID
        user = User.objects.get(id=user_id)
        
        # Return user data as JSON
        user_data = {
            'id': user.id,
            'firstName': user.firstName,
            'middleName': user.middleName,
            'lastName': user.lastName,
            'position': user.position,
            'department': user.department,
            'companyId': user.companyId,
            'username': user.username,
            'date': user.date,
        }
        
        return JsonResponse({'user': user_data})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

def qr(request):
    try:
        latest_code = Code.objects.latest('date')
        return render(request, 'index.html', {'qr': latest_code})
    except ObjectDoesNotExist:
        return render(request, 'error.html', {'message': 'No QR code available'})

@csrf_exempt
def make_qr(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('userId')
            qr = data.get('qr_code')
            id = data.get('id')
            action = data.get('action')

            # Now proceed with existing code logic
            existing_code = Code.objects.filter(qr=qr).first()
            get_checkInQR = Slip.objects.get(id=id)

            if existing_code and get_checkInQR:
                random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
                date_part = datetime.now().strftime('%Y%m%d%H%M%S')
                make_new_qr = f'{random_part}_{date_part}' 
                existing_code.user = user_id
                
                if action == "checkInQR":
                    get_checkInQR.checkIn = timezone.now()
                    get_checkInQR.checkInQR = qr
                elif action == "checkOutQR":
                    get_checkInQR.checkOut = timezone.now()
                    get_checkInQR.checkOutQR = qr
                get_checkInQR.save()
                existing_code.save()
                new_code = Code(user=None, qr=make_new_qr)
                new_code.save()

                return JsonResponse({'message': 'QR code created successfully.', 'new_qr': make_new_qr}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def make_request(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            timeOut = data.get('timeOut')
            timeIn = data.get('timeIn')
            reason = data.get('reason')
            department = data.get('department')
            # Retrieve the User instance
            try:
                user = User.objects.get(id=user_id)  # Fetch the user instance
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)

            # Create a new slip instance
            new_slip = Slip(
                user=user,  # Assign the User instance here
                department=department,
                confHR=None,
                confhead=None,
                status=False,
                timeIn=timeIn,
                timeOut=timeOut,
                checkIn=None,
                checkInQR=None,
                checkOut=None,
                checkOutQR=None,
                reason=reason,
                date=timezone.now()
            )
            new_slip.save()  # Save the instance

            return JsonResponse({'message': 'Slip created successfully'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def get_data(request):
    items = Code.objects.latest('date')
    return render(request, 'qr.html', {'item': items.qr})

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class SlipViewSet(viewsets.ModelViewSet):
    queryset = Slip.objects.all()
    serializer_class = SlipSerializer

class CodeViewSet(viewsets.ModelViewSet):
    queryset = Code.objects.all()
    serializer_class = CodeSerializer

class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer

def register_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Basic validation
        if 'username' not in data or 'password' not in data:
            return JsonResponse({'error': 'Please provide username and password'}, status=400)
        # Check if the username already exists
        if User.objects.filter(username=data['username']).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        # Create and save the user
        user = User(
            username=data['username'],
            password=data['password'],
            firstName=data.get('firstName', ''),
            middleName=data.get('middleName', ''),
            lastName=data.get('lastName', ''),
            position=data.get('position', ''),
            companyId=data.get('companyId', '')
        )
        user.save()
        return JsonResponse({'success': 'User registered successfully'})
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'success', 'position': user.profile.position})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


class UserLogin(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user is not None:
            return Response({'id': user.id, 'username': user.username}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            # User is authenticated
            return Response({'id': user.id, 'username': user.username}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)


def get_notifications(request):
    notifications = [
        {"message": "New user registered."},
        {"message": "Server backup completed."},
    ]
    return JsonResponse(notifications, safe=False)

def login(request):
    return render(request, 'Login.html')

from django.contrib.auth.hashers import check_password

@csrf_exempt
def admin_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        try:
            admin_user = Admin.objects.get(username=username)

            if password == admin_user.password:
                request.session['user_id'] = admin_user.id
                request.session['username'] = admin_user.username
                request.session['first_name'] = admin_user.firstName
                request.session['last_name'] = admin_user.lastName
                request.session['position'] = admin_user.position
                request.session['department'] = admin_user.department

                user_data = {
                    'id': admin_user.id,
                    'firstName': admin_user.firstName,
                    'middleName': admin_user.middleName,
                    'lastName': admin_user.lastName,
                    'position': admin_user.position,
                    'department': admin_user.department,
                }

                return JsonResponse({'message': 'Login successful', 'user': user_data}, status=200)
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)
        except Admin.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)
    else:
        # If session exists, redirect to home
        if 'user_id' in request.session:
            return redirect('home')
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def home(request):
    # Check if the user is authenticated by verifying the session
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect to login page if session is invalid

    # Get user info from the session
    user_info = {
        'id': request.session['user_id'],
        'username': request.session['username'],
        'first_name': request.session['first_name'],
        'last_name': request.session['last_name'],
        'position': request.session['position'],
        'department': request.session['department'],
    }

    # Render the home page with the user's session data
    return render(request, 'home.html', {'user': user_info})

@ensure_csrf_cookie
def admin_login_view(request):
    return render(request, 'login.html')

@login_required
def home(request):
    return render(request, 'home.html')
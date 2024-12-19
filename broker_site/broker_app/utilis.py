from .decorators import *
from .forms import *
from .models import *

# utils.py
def validate_mid_code(input_mid_code, user_profile):
    # Compare the input OTP with the OTP stored in the user profile
    return input_mid_code == user_profile.MID_CODE

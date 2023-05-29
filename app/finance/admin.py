from django.contrib import admin
from .models import *

# SuperUser
# name: admin, password: admin

admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(Budget)
admin.site.register(Category)
admin.site.register(RegularPayment)
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class SignupForm(UserCreationForm):
    email=forms.EmailField(required=False)
    class Meta:
        model=User
        fields=('username','email','password1','password2')
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():field.widget.attrs['class']='field-input'

class SigninForm(AuthenticationForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():field.widget.attrs['class']='field-input'

class JournalForm(forms.Form):
    text=forms.CharField(max_length=3000,widget=forms.Textarea(attrs={'class':'journal-input','rows':5,'maxlength':3000,'placeholder':'Write what is on your mind...'}))

class CheckinForm(forms.Form):
    def __init__(self,questions,*args,**kwargs):
        super().__init__(*args,**kwargs)
        choices=[(0,'Not at all'),(1,'Several days'),(2,'More than half the days'),(3,'Nearly every day')]
        for i in range(1,len(questions)+1):
            self.fields[f'q{i}']=forms.TypedChoiceField(choices=choices,coerce=int,widget=forms.RadioSelect,required=True)

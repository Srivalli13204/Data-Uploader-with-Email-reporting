import pandas as pd
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from .forms import UploadFileForm
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Create your views here.
def home(request):
    return render(request, 'app/home.html')

def handle_file(f):
    df = pd.read_excel(f, engine ='openpyxl') if f.name.endswith('.xlsx') else pd.read_csv(f)
    return df

def generate_summary(df):
    summary = {
        "rows" : df.shape[0],
        "columns" : df.shape[1],
    }
    return summary

def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            df = handle_file(file)
            summary = generate_summary(df)

            html = df.to_html(classes='table table-striped', index=False, header=True)

            content = render_to_string('app/email.html', {'summary' : summary, 'html' : html})
            text = strip_tags(content)

            email = EmailMultiAlternatives(
                subject='Python Assignment - Your Name',
                body=text,
                from_email='Sender Email',
                to=['Receiver Email'],
            )
            email.attach_alternative(content, "text/html")
            email.send()

            context = {
                'table' : html,
                'summary' : summary
            }
            return render(request, 'app/success.html', context)
    else:
        form = UploadFileForm()
    return render(request, 'app/upload.html', {'form' : form})

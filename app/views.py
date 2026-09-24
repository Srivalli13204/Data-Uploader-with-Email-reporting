import pandas as pd

from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from .forms import UploadFileForm

from django.template.loader import render_to_string
from django.utils.html import strip_tags


# ==================================================
# HOME PAGE
# ==================================================

def home(request):
    return render(request, 'app/home.html')


# ==================================================
# HANDLE UPLOADED FILE
# ==================================================

def handle_file(f):

    if f.name.endswith('.xlsx'):
        df = pd.read_excel(
            f,
            engine='openpyxl'
        )

    elif f.name.endswith('.csv'):
        df = pd.read_csv(f)

    else:
        raise ValueError(
            'Only CSV and XLSX files are supported.'
        )

    return df


# ==================================================
# GENERATE SUMMARY
# ==================================================

def generate_summary(df):

    summary = {
        'rows': df.shape[0],
        'columns': df.shape[1],
    }

    return summary


# ==================================================
# UPLOAD PAGE
# ==================================================

def upload(request):

    if request.method == 'POST':

        form = UploadFileForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            file = request.FILES['file']

            try:

                # Read uploaded file
                df = handle_file(file)

                # Generate summary
                summary = generate_summary(df)

                # Convert dataframe to HTML table
                html = df.to_html(
                    classes='table table-striped',
                    index=False,
                    header=True
                )

                # Prepare email HTML
                content = render_to_string(
                    'app/email.html',
                    {
                        'summary': summary,
                        'html': html
                    }
                )

                # Convert HTML email to plain text
                text = strip_tags(content)

                # Create email
                email = EmailMultiAlternatives(
                    subject='Data Processing & Summary Report',

                    body=text,

                    from_email=settings.EMAIL_HOST_USER,

                    to=[
                        settings.REPORT_RECEIVER_EMAIL
                    ],
                )

                # Add HTML version
                email.attach_alternative(
                    content,
                    'text/html'
                )

                # Send email
                email.send()

                # Display success page
                context = {
                    'table': html,
                    'summary': summary
                }

                return render(
                    request,
                    'app/success.html',
                    context
                )

            except Exception as e:

                return render(
                    request,
                    'app/upload.html',
                    {
                        'form': form,
                        'error': str(e)
                    }
                )

    else:

        form = UploadFileForm()

    return render(
        request,
        'app/upload.html',
        {
            'form': form
        }
    )
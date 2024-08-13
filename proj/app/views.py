# email_app/views.py
from django.shortcuts import render, redirect
from .forms import EmailUploadForm
from django.views.decorators.csrf import csrf_exempt
from email.parser import BytesParser, Parser
from email.policy import default
from bs4 import BeautifulSoup
from django.http import JsonResponse
from pickle import load
import os
from .models import EmailFeedback

@csrf_exempt
def upload_email(request):
    if request.method == 'POST':
        form = EmailUploadForm(request.POST, request.FILES)
        if form.is_valid():
            email_file = request.FILES['email_file']
            email_content = extract_email_info_view(email_file)
            email_body = email_content['body']
            email_prediction = mail_predict(email_body)
            context = {**email_content, **email_prediction}
            return render(request, 'display_email.html', context)
    else:
        form = EmailUploadForm()
    return render(request, 'upload_email.html', {'form': form})

def display_email(request):
    message = ""
    if request.method == 'POST':
        email = request.POST.get('email')
        proof = request.POST.get('proof') 

        # Check if fields are not empty
        if email and proof:
            try:
                feedback = EmailFeedback(email=email, proof=proof)
                feedback.save()
                message = "Feedback submitted successfully!"
            except Exception as e:
                message = f"Error saving feedback: {str(e)}"
        else:
            message = "Please fill in both the email and proof fields."

    return render(request, 'display_email.html', {'message': message})

@csrf_exempt
def extract_email_info_view(email_file):
    try:
        msg = BytesParser(policy=default).parse(email_file)
        subject = msg['subject']
        sender = msg['from']

        body = ""
        if msg.is_multipart():
            for part in msg.iter_parts():
                if part.get_content_type() == 'text/plain':
                    body += part.get_payload(decode=True).decode(part.get_content_charset(), errors='ignore')
                elif part.get_content_type() == 'text/html':
                    html = part.get_payload(decode=True).decode(part.get_content_charset(), errors='ignore')
                    soup = BeautifulSoup(html, 'html.parser')
                    body += soup.get_text()
        else:
            if msg.get_content_type() == 'text/plain':
                body = msg.get_payload(decode=True).decode(msg.get_content_charset(), errors='ignore')
            elif msg.get_content_type() == 'text/html':
                html = msg.get_payload(decode=True).decode(msg.get_content_charset(), errors='ignore')
                soup = BeautifulSoup(html, 'html.parser')
                body = soup.get_text()

        # Function to remove meaningless words
        body = remove_meaningless_words(body)

        links = []
        if msg.is_multipart():
            for part in msg.iter_parts():
                if part.get_content_type() == 'text/html':
                    html = part.get_payload(decode=True).decode(part.get_content_charset(), errors='ignore')
                    soup = BeautifulSoup(html, 'html.parser')
                    links.extend(a['href'] for a in soup.find_all('a', href=True))
        else:
            if msg.get_content_type() == 'text/html':
                soup = BeautifulSoup(body, 'html.parser')
                links.extend(a['href'] for a in soup.find_all('a', href=True))

        attachments = []
        if msg.is_multipart():
            for part in msg.iter_parts():
                if part.get_content_disposition() and 'attachment' in part.get_content_disposition():
                    filename = part.get_filename()
                    attachments.append(filename)

        return {
            'subject': subject,
            'body': body,
            'links': links,
            'attachments': attachments
        }

    except Exception as e:
        return {'error': str(e)}

def remove_meaningless_words(text):
    # Placeholder for a real implementation
    return text

@csrf_exempt
def mail_predict(body):
    try:
        # Define the path to the model files
        model_files = {
            "vector": "app/predmodels/vector.pkl",
            "nb": "app/predmodels/nb.pkl",
            "lg": "app/predmodels/lg.pkl",
            "sgd": "app/predmodels/sgd.pkl",
            "xgb": "app/predmodels/xgb.pkl",
            "mlp": "app/predmodels/mlp.pkl"
        }

        models = {}

        # Load each model file
        for name, path in model_files.items():
            if not os.path.exists(path):
                return {'error': f"File not found: {path}"}
            with open(path, "rb") as f:
                models[name] = load(f)

        tf, nb, lg, sgd, xgb, mlp = models["vector"], models["nb"], models["lg"], models["sgd"], models["xgb"], models["mlp"]

        # Get input text from the request body
        text = body

        # Check if text is provided
        if not text:
            return {'error': 'No text provided'}

        # Use the original vectorizer to transform the new text
        text_vectorized = tf.transform([text])

        # Predict using models
        results = [
            ("NB", nb.predict(text_vectorized)),
            ("Logistic", lg.predict(text_vectorized)),
            ("SGD", sgd.predict(text_vectorized)),
            ("XG", xgb.predict(text_vectorized)),
            ("MLP", mlp.predict(text_vectorized)),
        ]

        # Determine majority vote (0 = phishing, 1 = safe)
        predictions = [result[1][0] for result in results]
        malicious_count = predictions.count(0)
        total_predictions = len(predictions)
        maliciousness_percentage = (malicious_count / total_predictions) * 100

        # Return the prediction result and maliciousness percentage as JSON
        return {
            "result": results,
            'msg': "Safe" if sum(predictions) > len(predictions) / 2 else "Not Safe",
            'maliciousness_percentage': maliciousness_percentage
        }
    except Exception as e:
        return {'error': str(e)}


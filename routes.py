from flask import request, render_template, url_for, redirect
from app import app
from formurlvalidator import FormValidator, ValidationFailureReason
from gform import GoogleForm
from switch import switch
import logging

# TO DO:
#   Given a public URL, give a Twilio URL
#   SentFromIP:     IP address that sent the request to this script

@app.route("/", methods=['GET'])
def index():
    
    return render_template('base.html', state="nothing-submitted")

@app.route("/", methods=['POST'])
def submit():
    print "I'm on submit"
    logging.info('something in submit')

    try:

        form = FormValidator(request.form['url'])
        print "I'm on submit - form"
        if form.Validate():
            message = "Looks good! Here is the data that will be sent to your spreadsheet:"
            print "I'm on submit - v1 "
            sms_request_url = url_for('form', formkey=form.formkey, _external=True)
            print "I'm on submit - v2"

            return render_template('base.html',
                        message=message,
                        state="valid-submission",
                        url=form.url,
                        parameters_found=form.parameters,
                        sms_request_url=sms_request_url)

        else:
            message = ''

            for case in switch(form.failureReason):
                if case(ValidationFailureReason.NoUrl) :
                    message = "No URL entered. " \
                                'Maybe you just pressed the "Submit" button ' \
                                "without pasting a URL in the input field above?"
                    break
                if case (ValidationFailureReason.NoGoogleInUrl) :
                    message = "There was a problem with the URL, " \
                                "are you sure that you entered the URL " \
                                "for a Google Form?"
                    break
                if case (ValidationFailureReason.UrlNotForGoogleForm) :
                    message = "There was a problem with the URL, " \
                                "are you sure that you entered the URL " \
                                " for a \"live\" Google Form?"
                    break
                if case (ValidationFailureReason.UrlForGoogleSpreadsheetNotForm) :
                    message = "That URL appears to be for a Google Spreadsheet, " \
                        "it needs to be for a Google Form."
                    break
                if case (ValidationFailureReason.GoogleFormDoesntExist) :
                    message = "The URL you entered " \
                                "looks like a valid URL for a Google Form, " \
                                "I'm just having trouble validating it. " \
                                "Perhaps you entered the URL for an example form?"
                    break
                if case (ValidationFailureReason.NoTwilioParametersInForm) :
                    message = "The URL you entered looks like a valid Google Form, " \
                                "but it doesn't have any inputs for Twilio data. " \
                                "Update your form to accept at least one Twilio parameter " \
                                "and try again."
                    break                
                # /// end switch

            return render_template('base.html',
                        message=message,
                        state="error",
                        url=request.form['url'])

            # /// end if

    except Exception as inst:

        return render_template('base.html',
            message=inst,
            state="error",
            url=request.form['url'])

# https://docs.google.com
# /spreadsheet/viewform?formkey=aBCdEfG0hIJkLM1NoPQRStuvwxYZAbc2DE#git=0
@app.route("/form/<formkey>", methods=['GET', 'POST'])
def form(formkey):

    gform = GoogleForm(formkey)

    print 'in routers.pyt form method'
    # I could probably re-implement this with fewer lines using sets
    for key in request.values:
        print key
        if key in gform.labels:
            name = gform.labels[key]
            gform.parameters[name] = request.values[key]
   
    gform.show_state()

    

    return gform.submit()


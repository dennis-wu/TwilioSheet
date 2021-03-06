from pyquery import PyQuery as pq
import urllib
import urllib2
import re
import logging
from twilio.rest import TwilioRestClient

# Find these values at https://twilio.com/user/account
account_sid = "AC4eaf871649e343703db8d1dead644f5b"
auth_token  = "85a92cee1e3c131cd9d5348114e287f1"
twilio_client = TwilioRestClient(account_sid, auth_token)

class GoogleFormException(Exception):
    pass

class GoogleForm:

    formkey = ''
    """String containing the value
       of the formkey GET paramater from a Google Form URL"""
    action_url = ''
    """String containing the URL value
       from the 'action' attribute of the <form> tag in a Google Form"""
    parameters = {}
    """Dictionary where the 'key' is the input name
       and the 'value' is the default value, if any"""
    labels = {}
    """Dictionary where the 'key' is the label
       for a Google Form input and the 'value' is the input name"""

    def __init__(self, formkey):

        """Given a Google Form 'formkey',
           will parse interesting information from said form."""
        form_url = "https://docs.google.com/a/letslinc.com/forms/d/e/{0}/viewform".format(formkey)

        self.formkey = ''
        self.action_url = ''
        self.parameters = {}
        self.labels = {}   
        # label example: SmsSid, From, To

        try:
            print 'in gform 1 ' + str(form_url)
            
            html = pq(url=form_url)
            print 'in gform 2'
            #print html

        except Exception as inst:
            print 'exception ' + str(inst)
            logging.warn(inst)
            raise GoogleFormException("Error parsing URL '%s', did you pass the correct formkey?" % inst)

        form = html.find('form')
        self.action_url = form.attr['action']

        # Map out the label to form-input-name relationships
        for item in html.find('.freebirdFormviewerViewItemsItemItem.freebirdFormviewerViewItemsTextTextItem'):
            text_item = pq(item)
            print text_item

            input_label = text_item.find('.freebirdFormviewerViewItemsItemItemTitle').text()
            print input_label

            input_html = text_item.find('input')
            
            print input_html

#            input_id = item.find('.freebirdFormviewerViewItemsItemItemHelpText').attr('id')
#            print input_id
            input_id = input_html.attr('name') 
            input_name = input_html.attr('aria-label')
            input_value = input_html.attr('value')

#        for item in html.find('.ss-item.ss-text'):
#            text_item = pq(item)
#            input_label = text_item.find('.ss-q-title').text()
#            input_id = text_item.find('input[type=\'text\']').attr('id')
#            input_name = text_item.find('input[type=\'text\']').attr('name')
#            input_value = text_item.find('input[type=\'text\']').val()

            if (input_id != ""):
                self.parameters[input_id] = input_value
                
            self.labels[input_label] = input_id
        
        print 'end of. show state follows'
        self.show_state()


    def show_state(self):
        """Print the contents of the 'paramaters' and 'labels' properties"""

        print "Parameters:",
        print self.parameters
        print "Labels:",
        print self.labels

    def submit(self):
        """Submit the contents of the 'parameters' property
           to the Google Form"""

        url = self.action_url + urllib.urlencode(self.parameters)
        print self.action_url
        print self.parameters
        print url


        logging.warn(url)

        f = urllib2.urlopen(self.action_url, urllib.urlencode(self.parameters))
        result = pq(f.read())
        message = result.find('.ss-resp-message').text()
        
        # send thank you sms message back
        entry_id = None
        for label in self.labels:
            if label == 'From':
                entry_id = self.labels[label]

        if entry_id != None:
            to_number = self.parameters[entry_id]
            sms_message = twilio_client.messages.create(to= to_number, from_="+18552325462", body="Thanks for Linc-ing! You've officially been entered into a chance to win an Amazon Echo. Winner will be emailed October 4th")
        else:
            print 'can not find proper entry_id for From field'

        # http://bit.ly/12ySdJQ
        response = "<Response><!-- %s --></Response>" % message
        return response

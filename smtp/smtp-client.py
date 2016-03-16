#!/usr/bin/python

import smtplib
import sys, os
import argparse
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

class SmtpClient:
  def __init__(self):
    # debug mode
    self.debug = 0

    # global variables
    self.smtp = {
      'host': None, 
      'port': 25,
      'user': None, 
      'pass': None, 
      'usetls': True }
    self.smtpsession = None
    self.MsgBody = []
    self.MsgSubject = "Mail default subject"
    self.MsgHeaders = []
    self.MsgFromName = 'Mail SMTP Script'
    self.MsgFromAddress = None
    self.MsgTo = []
    self.MsgFromFile = None
    self.MsgAttachments = []
    #self.Args = None

    self.GetArgs()
    self.SmtpSend()

  def GetArgs(self):
    parser = argparse.ArgumentParser()
    parser.add_argument("--smtp-host", action="store", type=str, help="SMTP Port (default 25)")
    parser.add_argument("--smtp-port", action="store", type=int, help="SMTP Port (default 25)")
    parser.add_argument("--smtp-user", action="store", type=str, help="User for smtp authentication")
    parser.add_argument("--smtp-pass", action="store", type=str, help="Password for smtp authentication")
    parser.add_argument("--smtp-usetls", action="store_true", help="Use TLS")
    parser.add_argument("--msg-mailfrom", action="store", type=str, help="Mail From, (johndoe@example.com)")
    parser.add_argument("--msg-namefrom", action="store", type=str, help="Name From, John Doe")
    parser.add_argument("--msg-subject", action="store", type=str, help="Subject")
    parser.add_argument("--msg-to", action="store", type=str, help="Mail addresses list separated by comma")
    parser.add_argument("--msg-fromfile", action="store", type=str, help="Path to filename that will be send as body")
    parser.add_argument("--msg-body", action="store", type=str,help="Mail Body")
    parser.add_argument("--msg-attachments", action="store", type=str, help="Path to attachment file comma separated. --msg-attachments='file1,file2'")

    # parse arguments
    args = parser.parse_args()

    # smtp args
    self.smtp['host']   = args.smtp_host if args.smtp_host!=None else None 
    self.smtp['port']   = args.smtp_port if args.smtp_port!=None else None 
    self.smtp['user']   = args.smtp_user if args.smtp_user!=None else None 
    self.smtp['pass']   = args.smtp_pass if args.smtp_pass!=None else None 
    self.smtp['usetls'] = True if args.smtp_usetls!=None else False 
    
    # message args
    self.MsgBody        = args.msg_body if args.msg_body!=None else None
    self.MsgSubject     = args.msg_subject if args.msg_subject!=None else 'Mail default subject'
    self.MsgFromName    = args.msg_namefrom if args.msg_namefrom!=None else 'Smtp Client'
    self.MsgFromAddress = args.msg_mailfrom if args.msg_mailfrom!=None else 'noreply@example.com'
    self.MsgTo          = args.msg_to.split(',') if args.msg_to!=None else None
    self.MsgFromFile    = args.msg_fromfile if args.msg_fromfile!=None else None 
    self.MsgAttachments = args.msg_attachments.split(',') if args.msg_attachments!=None else None

    if self.debug > 0:
      print self.MsgBody       
      print self.MsgSubject    
      print self.MsgFromName   
      print self.MsgFromAddress
      print self.MsgTo         
      print self.MsgFromFile   
      print self.smtp

    try:
      if self.smtp['host']==None: raise Exception('--smtp-host is needed by smtp server')
      if self.smtp['user']==None: raise Exception('--smtp-user is needed by smtp server')
      if self.smtp['pass']==None: raise Exception('--smtp-pass is needed by smtp server')
      if self.MsgTo==None: raise Exception('--msg-to is a required param')
    except Exception as e:
      print e
      sys.exit(0)

  def SmtpConnect(self):
    try:
      self.smtpsession = smtplib.SMTP(self.smtp['host'], self.smtp['port'])
      self.smtpsession.ehlo()
      if self.smtp['usetls']: self.smtpsession.starttls()
      if self.smtp['user']!=None and self.smtp['pass']!=None: self.smtpsession.login(self.smtp['user'], self.smtp['pass'])
    except smtplib.SMTPDataError as e:
      with open('/tmp/AvtSMTP.log', 'w') as text_file:
        text_file.write("Error: %s" % e)
        sys.exit(1)

  def SmtpCreateHeaders(self):
    self.MsgHeaders.append("from: %s <%s>" %(self.MsgFromName,self.MsgFromAddress))
    self.MsgHeaders.append("to: %s" %( ','.join(self.MsgTo) ))
    self.MsgHeaders.append("subject: %s " %(self.MsgSubject))
    self.MsgHeaders.append("mime-version: 1.0")
    self.MsgHeaders.append("content-type: text/html")
  
  def SmtpCreateMessage(self):
    self.SmtpConnect()
    self.SmtpCreateHeaders()

    Headers = '\r\n'.join(self.MsgHeaders)
    Body = self.MsgBody if self.MsgFromFile==None else self.ReadMessageFromFile(self.MsgFromFile)
    Body = Body.replace('\n','<br>') # replace new lines by <br> for the text/html message
    Content = Headers + '\r\n\r\n' + Body

    try:
      # send mail
      self.smtpsession.sendmail(self.MsgFromAddress, self.MsgTo, Content)
      print "mail sent"
    except (smtplib.SMTPDataError, Exception) as e:
      print e
      sys.exit(1)

  def SmtpSend(self):
    if self.MsgAttachments==None:
      self.SmtpCreateMessage()
    else:
      self.SmtpSendAttach()

  def ReadMessageFromFile(self, filename=None):
    try:
      if os.path.isfile('%s' %(filename)):
        with open(filename, 'r') as text_file:
          content = text_file.read()
          return content
    except (OSError, ValueError) as e:
        print e
        sys.exit(1)

  def SmtpSendAttach(self):
    assert isinstance(self.MsgTo, list)
  
    msg = MIMEMultipart()
    msg['From']     = "%s <%s>" %(self.MsgFromName, self.MsgFromAddress)
    msg['To']       = COMMASPACE.join(self.MsgTo)
    msg['Date']     = formatdate(localtime=True)
    msg['Subject']  = self.MsgSubject

    msg.attach(MIMEText(self.MsgBody))

    for attachment in self.MsgAttachments or []:
      attach_file=MIMEApplication(open(attachment,"rb").read())
      attach_file.add_header('Content-Disposition','attachment', filename="%s" % os.path.basename(attachment))
      msg.attach(attach_file)

    try:
      self.SmtpConnect() # connect to smtp server
      self.smtpsession.sendmail(self.MsgFromAddress, self.MsgTo, msg.as_string())
      self.smtpsession.close()
      print "mail sent"
    except Exception as e:
      print e

if __name__ == '__main__': 
  Client = SmtpClient()
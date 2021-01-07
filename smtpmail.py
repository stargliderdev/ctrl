#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import Encoders
from email.MIMEBase import MIMEBase
import os
from datetime import datetime

import parameters as gl

def send_saft_smtp(senders, filename, msg_headers):
    flag = False
    smtpserver = gl.mail_server
    AUTHREQUIRED = 0
    smtpuser = gl.mail_user
    smtppass = gl.mail_pass
    SUBJECT = msg_headers['sub']

    msg = MIMEMultipart()
    msg['Subject'] = SUBJECT
    msg['From'] = gl.mail_user
    to = senders.split(';')
    to.append(gl.mail_user)
    msg['To'] = ','.join(to)
    text = msg_headers['body']

    part1 = MIMEText(text, 'html','UTF-8')

    # permite varios ficheiros
    msg.attach(part1)
    for n in filename:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(n, "rb").read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(n))
        msg.attach(part)

    session = smtplib.SMTP(smtpserver,25)
    session.ehlo()
    session.starttls()
    session.ehlo()
    #if AUTHREQUIRED:
    session.login(smtpuser, smtppass)
    smtpresult = session.sendmail(gl.mail_user, to, msg.as_string())
    if smtpresult:
        errstr = ""
        for recip in list(smtpresult.keys()):
            errstr = """Could not delivery mail to: %s
                Server said: %s
                %s
                %s""" % (recip, smtpresult[recip][0], smtpresult[recip][1], errstr)
        raise smtplib.SMTPException(errstr)
        return False
    else:
        return True


def make_saft_headers():
    meses = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
             9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro', 13: 'Todo o Ano'}
    subject = 'SAF-T do NIF: ' + gl.saft_config_dict['saftnif'] + ' ' + gl.saft_config_dict['commercial_name'] + ' de ' + \
              meses[gl.saft_config_dict['saft_month']] + '/' + str(gl.saft_config_dict['saft_year'])
    
    body_text = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8"></head> '''
    body_text += '''<pre>'''
    body_text += '''D. COMERCIAL:''' + gl.saft_config_dict['commercial_name'] + '''<br>'''
    body_text += '''    D.SOCIAL:''' + gl.saft_config_dict['saftname'] + '''<br>'''
    body_text += '''       N.I.F:''' + gl.saft_config_dict['saftnif'] + '''<br>'''
    body_text += '''   MES e ANO:''' + meses[gl.saft_config_dict['saft_month']] + '/' + str(gl.saft_config_dict['saft_year']) + '''<br>'''
    body_text += '''        DATA:''' + datetime.now().strftime('%d.%b.%Y %H:%M') + '''<br>'''
    body_text += '''    PORTARIA:''' + gl.PORTARIA + '''<br>'''
    body_text += '''</pre>
               Exmos. Senhores,<br>segue em anexo o ficheiro SAF-T do contribuinte supra mencionado.''' + '''<br>'''\
                + '''O presente ficheiro cumpre as regras estabelecidas na '''\
                + '''<a href="http://info.portaldasfinancas.gov.pt/pt/apoio_contribuinte/SAFT_PT/Paginas/news-saf-t-pt.aspx">'''\
                + '''Portaria 302/2016 e consequentes Declarações de Retificação</a>.'''\
                +  gl.msg_to_sender  \
                + '''Erros de validação transmitidos pelo site da AT têm de ser comunicados respondendo a este e-mail<br>ou enviando uma mensagem para
               <a href="mailto:saft@jheg.pt">saft@jheg.pt</a> com os seguintes elementos:
               <ul>
              <li>Identificação do NIF no <b>assunto</b>.</li>
              <li>Ficheiro SAF-T original(não resumido) gerado pela <b>nossa aplicação</b>.</li></ul>'''\
                + '''Duvidas geradas ao utilizar/analisar com: <ul>'''\
                + '''<li>programas de contablidade </li>  ''' \
                + '''<li>analisadores de SAF-t. </li>  ''' \
                + '''<li>listagens/relatorios de programas de contablidade. </li>  '''\
                + '''<li>ficheiros em Excel. </li>  '''\
                + '''<li>integradores de SAF-t na contablidade. </li> </ul> '''\
                + '''Devem ser comunicadas aos fabricantes dos respectivos programas.
                <br><br><strong>Atenção</strong>: o ficheiro encontra-se compactado,
               para descompactar deve ser utilizada uma aplicação própria como: winzip, winrar,7zip,gzip. <br>'''
    body_text += '''<small>v. ''' + gl.VERSION + '''</small><br>'''

    body_text += '''<hr><h6>Este e-mail pode conter informação privilegiada e/ou confidencial . Se não for o destinatário
    (ou tiver erradamente  recebido este e-mail), por favor notifique o remetente imediatamente ou destrua este e-mail.
     Qualquer cópia não autorizada, divulgação ou distribuição do material neste e-mail está estritamente proibida.<br></h6></html>'''
    msg_dic = {'sub': subject, 'body': body_text}
    return msg_dic


def make_email_headers(sub,files_names, body_mesage):
    subject = sub
    body_text = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8"></head>
               Exmos. Senhores,<br>seguem em anexo(s) ficheiros/documentos solicitados.<br>''' + unicode(body_mesage.replace('\n','<br>')).encode('utf-8')
                
    body_text += '''<br><hr><pre>Ficheiros anexos a esta mensagem:<strong>''' + files_names.replace(';','<br>') + '''<br>'''
    body_text += '''</strong><br>Data:''' + datetime.now().strftime('%d.%m.%Y %H:%M:%S') + '''<br>'''
    body_text += '''UUID:''' + str(uuid.uuid4()) + '''<br>'''
    body_text += '''UNIT:''' + gl.saft_config_dict['commercial_name']  + '''<br>'''
    body_text += '''</pre><hr><h6>Este e-mail pode conter informação privilegiada e/ou confidencial . Se não for o destinatário
    (ou tiver erradamente  recebido este e-mail), por favor notifique o remetente imediatamente ou destrua este e-mail.
     Qualquer cópia não autorizada, divulgação ou distribuição do material neste e-mail está estritamente proibida.<br><br>
This email may contain confidential and/or privileged information. If you are not the intended recipient
   (or have mistakenly received this email) please notify the sender immediately and destroy this email.
    Any unauthorised copying, disclosure or distribution of the material in this email is strictly forbidden.</h6></html>'''
    msg_dic = {'sub': subject, 'body': body_text}
    return msg_dic



if __name__ == '__main__':
    pass


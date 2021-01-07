#!/usr/bin/python
# -*- coding: utf-8 -*-

import parameters as gl
import psql_check


def update_to_html():
    # gera html
    html = '''<!DOCTYPE html><html lang="pt_pt"><head><meta charset="utf-8">
              <style> ''' + get_lib(1) + '</style></head>'
    div_title = '''<div style="margin-bottom: 10px; margin-left: 10px;"><h3 class='round_title'>'''
    div_end = '''</h3></div>\n'''
    td_caixa='<tr><td id="label">'
    td_data = '<td style="color: #000080 ; font-family:Verdana; font-size:14px">'
    td_end = '''</td></tr>\n'''
    html += ''' <table> '''
    html += div_title +'Dados do Cliente<td> ' + div_end
    html += td_caixa + 'Designação social:</td>' + td_data + gl.saftname + td_end
    html += td_caixa + 'Numero de Contribuinte</td>' + td_data + gl.saftnif + td_end
    html += td_caixa + 'Designação Comercial:</td>' + td_data + gl.commercial_name + td_end
    html += td_caixa + 'Morada:</td>' + td_data + gl.saftaddress + td_end
    html += td_caixa + 'Codio Postal</td>' + td_data + gl.saftpostalcode + td_end
    html += td_caixa + 'Localidade</td>' + td_data + gl.saftcity + td_end
    html += td_caixa + 'Posto</td>' + td_data + gl.pos_ini['posid'] + td_end
    if gl.update_settings['unlock']:
        html += td_caixa + 'Data de Bloqueio</td>' + td_data + ' SEM BLOQUEIO.' + td_end
    else:
        html += td_caixa + 'Data de Bloqueio:</td>' + td_data + '<font color="red"> ' + gl.lock_date + '</font">' + td_end
    html += '</table>\n'
    html += ''' <table> '''
    html += '''<div style="margin-bottom: 10px; margin-left: 10px;"><h3 class='round_title2'>Meta Dados </h3></div>\n'''
    try:
        html += td_caixa + 'Software</td>' + td_data + gl.server_data['software'] + td_end
    except KeyError:
        html += td_caixa + 'Software</td> KEY ERROR' + td_end
    html += td_caixa + 'Versão Actual</td>' + td_data + gl.version + td_end
    html += td_caixa + 'S.O.</td>' + td_data + gl.system_info['os'] + ' ' + gl.system_info['os_version'] + ' / ' + \
            gl.system_info['arch'] + td_end
    if gl.server_data['server']:
        html += td_caixa + 'Versão PostgreSQL</td>' + td_data + gl.pg_version + td_end
        html += td_caixa + 'Postos</td>' + td_data + str(gl.server_data['terminals']) + td_end
        if gl.server_data['printers'] >0:
            html += td_caixa + 'Numero de impressoras</td>' + td_data + str(gl.server_data['printers']) + td_end
            html += td_caixa + 'Nomes das impressoras</td>' + td_data + gl.server_data['printers_names'] + td_end
        if gl.server_data['monitors'] >0:
            html += td_caixa + 'Monitores</td>' + td_data + str(gl.server_data['monitors']) + td_end
            html += td_caixa + 'Nomes dos monitores</td>' + td_data + gl.server_data['monitors_names'] + td_end
        html += td_caixa + 'IWS</td>' + td_data + str(gl.server_data['iws']) + td_end
        html += td_caixa + 'Envia SAF-t</td>' + td_data + str(gl.server_data['saft']) + td_end
        serie_data = psql_check.get_series_info()
    
        html += td_caixa + 'Serie</td>' + td_data + '<pre>' + serie_data + '</pre>' + td_end
        # html += td_caixa + 'Serie</td>' + td_data + gl.server_data['serie'] + td_end
        try:
            html += td_caixa + 'Premium</td>' + td_data + str(gl.server_data['agd'])  + td_end
        except KeyError:
            pass
        try:
            html += td_caixa + 'Data do Contrato</td>' + td_data + gl.server_data['contract']  + td_end
        except KeyError:
            html += td_caixa + 'Data do Contrato</td>' + td_data + 'N/D' + td_end
        try:
            html += td_caixa + 'Valido até</td>' + td_data + gl.server_data['valid_until']  + td_end
        except KeyError:
            html += td_caixa + 'Valido até</td>' + td_data + 'N/D' + td_end
        try:
            html += td_caixa + 'Data do Servidor</td>' + td_data + gl.pg_date[:16] + td_end
        except KeyError:
            html += td_caixa + 'Data do Servidor</td>' + 'Error'+ td_end
        try:
            html += td_caixa + 'Versão Anterior</td>' + td_data + gl.init_version + td_end
        except KeyError:
            html += td_caixa + 'Versão Anterior</td>' + td_data + 'Error' + td_end
    html += '</table>\n'
    html += '</html>'
    return html

def get_lib(id):
    if id == 1:
        toto ='''.round_conner {color:#000000;
                    font:14px verdana,sans-serif;
                    display: inline;
                    background:#56C5EA;
                    height: 25px;
                    border-radius: 7px;
                    padding-left:10px;
                    padding-right:10px;
                    padding-bottom:3px;
                    padding-top:2px;
                    text-align:right;
                    }
                    .round_title {color:#000000;
                    font:19px verdana,sans-serif;
                    background:#56C5EA;
                    height: 25px;
                    border-radius: 7px;
                    padding-left:10px;
                    padding-right:10px;
                    padding-bottom:3px;
                    padding-top:2px;
                    text-align:center;
                    }
                    .round_title2 {color:#000000;
                    font:16px verdana,sans-serif;
                    background:#567AEA;
                    height: 23px;
                    border-radius: 7px;
                    padding-left:8px;
                    padding-right:8px;
                    padding-bottom:3px;
                    padding-top:2px;
                    text-align:center;
                    }
                    .round_small {color:#FFDF00;
                    font:14px verdana,sans-serif;
                    display: inline;
                    background:#6F4E37;6F4E37
                    height: 25px;
                    border-radius: 4px;
                    padding-left:10px;
                    padding-right:10px;
                    padding-bottom:3px;
                    padding-top:2px;
                    text-align:right;

                    }
                    .round_tags {color:#ffffff;
                    font:10px verdana,sans-serif;
                    display: inline;
                    background:#6FD000;
                    height: 25px;
                    border-radius: 4px;
                    padding-left:10px;
                    padding-right:10px;
                    padding-bottom:3px;
                    padding-top:2px;
                    text-align:right;
                    }
                    .terminal {color:#00DD00;
                    font:14px verdana,sans-serif;
                    background-color:#000000;
                    border-radius: 6px;
                    padding-left:10px;
                    padding-right:10px;
                    padding-bottom:4px;
                    padding-top:2px;
                    text-align:left;
                    }
                    #label
                    {
                    border: solid #CCC 1.0pt;
                    text-align: center;
                    font-family: Verdana;
                    font-size: 10px;
                    color: #333;
                    font-weight: bold;
                    vertical-align: middle;
                    height: 20px;
                    }
                '''
    return toto

if __name__ == '__main__':
    pass


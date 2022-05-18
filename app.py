import os
import json
import uuid
from urllib import request, parse
from urllib.error import URLError, HTTPError
from flask import Flask, jsonify

#LINK PARA ENTENDER O ENVIO DE NOTIFICAÇÃO POR API: https://help.blip.ai/hc/pt-br/articles/4474382664855-Como-enviar-notificações-WhatsApp-via-API-do-Blip

#URLBLIP lista de endpoints da take
URLBLIP = ["https://msging.net/commands","https://http.msging.net/messages","https://http.msging.net/notifications"]

#KEYBLIP é chave do bot ou roteador que tenha o whatsapp conectado
KEYBLIP = ""

#namespace é estático sempre será o mesmo
namespace = ''

#tempalte_name será dinâmico aqui api que busca na waba()
template_name = ''

#flow_id é o identificador do bot para qual vamos amndar o cliente
flow_id = ""

#state_id é o id do bloco para qual vamos enviar o cliente
state_id = ""

#id_bot será o id do bot
id_bot = ""

#Nome do cliente dentro da aplicação de vocês
name = "Nome Do Cliente"

#variavael em que vai enviar o email do agente que efetuou o disparo 
agent_email = ""

data_response = {}

#requisição que registra o evento com dados do envio
#Link: https://docs.blip.ai/#create-an-event
def create_event (URLBLIP, KEYBLIP):

    print("Evento Criado")
    id = str(uuid.uuid4())
    id = "send-notification-api-" + id
    print("Monta Body")
    payBlip =  json.dumps({
    "id": id,
    "to": "postmaster@analytics.msging.net",
    "method": "set",
    "type": "application/vnd.iris.eventTrack+json",
    "uri": "/event-track",
    "resource": {
        "category": "notifications",
        "action": "send"
  }
}).encode('utf-8')
    print("Monta Requisição")
    BlipReq = request.Request(URLBLIP[0],data = payBlip, headers={'content-type': 'application/json', 'Authorization': KEYBLIP})
    print("Faz Requisição")
    BlipResp = request.urlopen(BlipReq).read().decode()
   
    return BlipResp

#requisição que verifica o número com o grupo meta
#Link: https://docs.blip.ai/#sending-a-notification-active-message a primeira req dessa sessão
def verification_phone (phone, URLBLIP, KEYBLIP):

    name = "Erro"
    
    id = str(uuid.uuid4())
    id = "send-notification-api-" + id
    payBlip =  json.dumps({
        
  "id": id,
  "to": "postmaster@wa.gw.msging.net",
  "method": "get",
  "uri": "lime://wa.gw.msging.net/accounts/"+phone
  
}).encode('utf-8')
    BlipReq = request.Request(URLBLIP[0],data = payBlip, headers={'content-type': 'application/json', 'Authorization': KEYBLIP})
    BlipResp = request.urlopen(BlipReq).read().decode()
    data = json.loads(BlipResp)
    status = data['status']

    if ("fullName" in BlipResp):

        name = data ['resource']['fullName']
        


    return BlipResp

#requsição que definifinitavemente envia a notificação para o cliente
#Mudar para modelo com váriavel
#Link: https://docs.blip.ai/#sending-a-notification-active-message a segunda req dessa sessão
def send_notification(URLBLIP ,KEYBLIP, namespace, template_name, identity):

    id = str(uuid.uuid4())
    id = "send-notification-api-" + id
    print("Monta Body")
    payBlip =  json.dumps({
            
    "id":id,
    "to":identity,
    "type":"application/json",
    "content":{
    "type":"template",
    "template":{
        "namespace":namespace,
        "name":template_name,
        "language":{
        "code":"pt_BR",
        "policy":"deterministic"

    }}}
  
    }).encode('utf-8')
    print("Monta Requisição")
    BlipReq = request.Request(URLBLIP[1],data = payBlip, headers={'content-type': 'application/json', 'Authorization': KEYBLIP})
    print("Faz Requisição")
    BlipResp = request.urlopen(BlipReq).read().decode()
   
    return BlipResp

#Requisição que altera o bloco do cliente
#Link da Doc:https://docs.blip.ai/#change-user-state
def change_state(URLBLIP, KEYBLIP, identity, flow_id, state_id):

    uri = "/contexts/"+identity+"/stateid@"+flow_id 
    id = str(uuid.uuid4())
    id = "send-notification-api-" + id
    payBlip =  json.dumps({
        
  "id": id,
  "to": "postmaster@msging.net",
  "method": "set",
  "uri": uri,
  "type": "text/plain",
  "resource": state_id
  
}).encode('utf-8')
    BlipReq = request.Request(URLBLIP[0],data = payBlip, headers={'content-type': 'application/json', 'Authorization': KEYBLIP})
    BlipResp = request.urlopen(BlipReq).read().decode()
    data = json.loads(BlipResp)
    status = data['status']

    return BlipResp

#Requisição que altera o bot que o cliente se encontra
#Atualmente não tem documentação atualizada
def change_bot(URLBLIP, KEYBLIP, identity, id_bot):

    uri = "/contexts/"+identity+"/master-state"
    id = str(uuid.uuid4())
    id = "send-notification-api-" + id
    id_bot = id_bot + "@msging.net"
    payBlip =  json.dumps({
        
"id": id,
"to": "postmaster@msging.net",
"method": "set",
"uri": uri,
"type": "text/plain",
"resource": id_bot
  
}).encode('utf-8')
    BlipReq = request.Request(URLBLIP[0],data = payBlip, headers={'content-type': 'application/json', 'Authorization': KEYBLIP})
    BlipResp = request.urlopen(BlipReq).read().decode()
    data = json.loads(BlipResp)
    status = data['status']

    return BlipResp

#requisição que cria ou atualiza o contato do cliente dentro do blip
#Link Doc: https://docs.blip.ai/#update-a-contact
def cria_att_ctt (URLBLIP, KEYBLIP, identity, name, jsonExtras):

    id = str(uuid.uuid4())
    id = "send-notification-api-" + id
    payBlip =  json.dumps({
                "id": id,
                "method": "merge",
                "type": "application/vnd.lime.contact+json",
                "uri": "/contacts",
                "resource": {
                "identity":identity,
                "name": name,
                "extras": jsonExtras
                
          } 
        }).encode('utf-8')
    BlipReq = request.Request(URLBLIP[0],data = payBlip, headers={'content-type': 'application/json', 'Authorization': KEYBLIP})
    BlipResp = request.urlopen(BlipReq).read().decode()
    try:
            BlipResp = request.urlopen(BlipReq).read().decode()

            print('Lead no Blip aceito')

            return BlipResp

    except HTTPError as e:
            
        print('Notificação no Blip rejeitada - StatusCode: ', e.code, ' Resposta: ', e.read(), ' Payload: ', payBlip)  

#ajusta telefone para padrão de auteticação BR da API
def regex_num (phone):

    phone=phone.replace(' ','',)
    phone=phone.replace('(','')
    phone=phone.replace(')','')
    phone=phone.replace('-','')
    phone=phone.replace('.','')

    tam_phone= len (phone)

    if (tam_phone > 2):

        ddd=phone[0]+phone[1]

    if (ddd == "+5") :

        phone = phone

    elif (ddd == "55"):

        phone =  "+"+phone

    else:

        phone = "+55" + phone
     

    return phone

       




#endpoint hello world teste

app = Flask(__name__)

@app.route('/')
def nao_entre_em_panico():

    from flask import request

    if request.headers.get('Authorization') == '42':
        return jsonify({"42": "a resposta para a vida, o universo e tudo mais"})
    return jsonify({"message": "Não entre em pânico!"})

@app.route('/send_notification', methods=['POST'])

def send():

    from flask import request

    data = request.get_json()
    

    #ler JSON
    state_id=data['state_id']
    flow_id=data['flow_id']
    template_name=data['template']
    phone=data['phone']
    name=data['name']
    id_bot=data['id_bot']
    jsonExtras = data['extras']

    KEYBLIP = request.headers.get('Authorization')
    namespace = request.headers.get('namespace')


    #identifica caso authorization não exista
    if(KEYBLIP == ""):

        return jsonify ({"erro":"Authorization não encontrado"})

    #identifica caso name sapce não exista
    if(namespace == ""):

        return jsonify ({"erro":"namespace não encontrado"})

    #Ajustar Telefone Para Verificação do Número
    adjustment_phone = regex_num(phone=phone)
    print("Ajustar Telefone Para Verificação do Número")

    #Verifica o Número na API do WhatsApp
    response_verification = verification_phone(phone = adjustment_phone, URLBLIP = URLBLIP, KEYBLIP = KEYBLIP)
    print("Verifica o Número na API do WhatsApp")

    #Carrega Informações retornadas no formato de JSON
    data_verification = json.loads(response_verification)
    print("Carrega Informações retornadas no formato de JSON")

    #Verifica Se Existe Nome vinculado a conta
    if ("fullName" in response_verification):

            name = data_verification ['resource']['fullName']

    #Identifica o Identity do número no whatsapp       
    identity = data_verification ['resource']['alternativeAccount']

    #Enviar Notificação
    response_notification = send_notification(URLBLIP = URLBLIP,KEYBLIP = KEYBLIP,namespace = namespace, template_name = template_name, identity = identity)

    #Levar o Cliente para o bloco correto
    response_state = change_state(URLBLIP = URLBLIP, KEYBLIP = KEYBLIP,identity = identity, state_id = state_id, flow_id = flow_id)
    
    #Coloca o usuário dentro do bot desejado, e no bloco selecionado anteriomente
    response_bot_change = change_bot(URLBLIP = URLBLIP, KEYBLIP = KEYBLIP, identity = identity, id_bot = id_bot)
    print("Coloca o usuário dentro do bot desejado, e no bloco selecionado anteriomente")

    #atuaiza dados do cliente de acordo com as informações passadas
    response_ctt = cria_att_ctt (URLBLIP = URLBLIP, KEYBLIP = KEYBLIP,identity = identity, name = name, jsonExtras = jsonExtras)

    #cria evento guardando a informação que a notificação foi enviada
    response_event = create_event (URLBLIP, KEYBLIP)

    #envia informações como retorno
    data_response = {

        "response_verification":data_verification,
        "response_change_bot":response_bot_change,
        "response_change_state":response_state,
        "response_send_notification":response_notification,
        "phone_number":adjustment_phone,
        "response_event":response_event,
        "response_ctt":response_ctt


    }

    return jsonify (data_response)

#Modelo de Body Esperado
#{
#    "phone": "11 956927573",
#    "name": "Pedro Mourão",
#    "template": "nps_2022v1",
#    "state_id": "47402715-0cd2-4c7c-ae79-4d347d93a9f9", 
#    "flow_id": "3da8fb90-7a04-42c2-b83e-b0b6a15e2774",
#    "id_bot": "apogeuprincipal",
#    "extras": {"Teste":"o pai ta on"}
#}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
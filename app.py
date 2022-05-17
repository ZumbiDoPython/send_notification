import os
from flask import Flask, jsonify, request

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

#requisição que verifica o número com o grupo meta
#Link: https://docs.blip.ai/#sending-a-notification-active-message a primeira req dessa sessão
def verification_phone (phone, URLBLIP, KEYBLIP):

    name = "Erro"
    
    id = str(uuid.uuid4())
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
def send_notification (URLBLIP, KEYBLIP, namespace, template_name, identity):

    id = str(uuid.uuid4())
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
    BlipReq = request.Request(URLBLIP[1],data = payBlip, headers={'content-type': 'application/json', 'Authorization': KEYBLIP})
    BlipResp = request.urlopen(BlipReq).read().decode()
   
    return BlipResp

#Requisição que altera o bloco do cliente
#Link da Doc:https://docs.blip.ai/#change-user-state
def change_state(URLBLIP, KEYBLIP, identity, flow_id, state_id):

    uri = "/contexts/"+identity+"/stateid@"+flow_id 
    id = str(uuid.uuid4())
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
def cria_att_ctt (URLBLIP, KEYBLIP, identity, name):

    uri = "/contacts/" + identity

    id = str(uuid.uuid4())
    payBlip =  json.dumps({
        
  "id": id,
  "method": "get",
  "uri": uri
  
}).encode('utf-8')
    BlipReq = request.Request(URLBLIP[0],data = payBlip, headers={'content-type': 'application/json', 'Authorization': KEYBLIP})
    BlipResp = request.urlopen(BlipReq).read().decode()
    try:
        BlipResp = request.urlopen(BlipReq).read().decode()
        print('Lead no Blip aceito')
        data = json.loads(BlipResp)
        status = data['status']

        
    except HTTPError as e:
        
        print('Notificação no Blip rejeitada - StatusCode: ', e.code, ' Resposta: ', e.read(), ' Payload: ', payBlip) 
    
    if(status == "Failure"):
    
        id = str(uuid.uuid4())
        payBlip =  json.dumps({
                "id": id,
                "method": "merge",
                "type": "application/vnd.lime.contact+json",
                "uri": "/contacts",
                "resource": {
                "identity":identity,
                "name": name,
                "extras":{
                    "email_agente":agent_email
                    
                }
                
          } 
        }).encode('utf-8')
        BlipReq = request.Request(URLBLIP[0],data = payBlip, headers={'content-type': 'application/json', 'Authorization': KEYBLIP})
        BlipResp = request.urlopen(BlipReq).read().decode()
        try:
            BlipResp = request.urlopen(BlipReq).read().decode()
            print('Lead no Blip aceito') 
        except HTTPError as e:
            
            print('Notificação no Blip rejeitada - StatusCode: ', e.code, ' Resposta: ', e.read(), ' Payload: ', payBlip)

    else:

        status = data['status']

        print("Lead Já Existente")

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
    if request.headers.get('Authorization') == '42':
        return jsonify({"42": "a resposta para a vida, o universo e tudo mais"})
    return jsonify({"message": "Não entre em pânico!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
from pyexpat.errors import messages
from bottle import get, post, run, request, response, route, static_file, template
import json
from db import *
import xmltodict
import yaml

@get('/read/topic/<topic>/from/<last_message_id>/limit/<limit:int>/token/<token>/format/<format>')
def _(topic, last_message_id, limit, token, format):
    try:
        #token to use: 843561
        output = {"messages": []}

        #validate of limit is correct
        if limit == 0: raise Exception("Limit must be greater than 0")

        #validate of token exists in users
        if validate_token(token):
    
            #get messages from topic
            messages = get_messages(topic, last_message_id, limit)
            for message in messages:
                output["messages"].append(message)
        else:
            raise Exception("Token is not valid")

        #format output to give form 
        if format == "json":
            response.content_type = 'application/json'
            print(output)
            return json.dumps(output, default=str)
        elif format == "yaml":
            print("YAML")
            return yaml.dump(output)
        elif format == "xml":
            response.content_type = 'text/xml'
            return xmltodict.unparse(output, pretty=True, full_document=False)
        elif format == "csv":
            response.content_type = 'text/csv'
            return to_csv(output)
        elif format == "tsv":
            return to_tsv(output)  
        else:
            raise Exception("Format is not valid")

    except Exception as e:
        response.status = 400
        return "Error: " + str(e)

@post('/create/topic/<topic>/token/<token>/format/<format>')
def _(topic,token, format):
    try:
        if validate_token(token) == False:
            raise Exception("Token is not valid")

        message = request.body.read()
        print("Message: ")
        print(message)

        if format == "json":
            message = json.loads(message)
            message = message["message"]
        elif format == "xml":
            message = json.dumps(xmltodict.parse(message)["message"])
            message = message.strip('"')
            print(message)

        if create_message(topic, message):
            return "Message created"
        else:
            raise Exception("Message could not be created")


    except Exception as e:
        response.status = 400
        return "Error: " + str(e)

@post('/update/topic/<topic>/message_id/<message_id>/token/<token>/format/<format>')
def _(topic, message_id, token, format):
    try:
        if validate_token(token) == False:
            raise Exception("Token is not valid")

        message = request.body.read()
        print("Message: ")
        print(message)

        if format == "json":
            message = json.loads(message)
            message = message["message"]
        elif format == "xml":
            message = json.dumps(xmltodict.parse(message)["message"])
            message = message.strip('"')
            print(message)

        if update_message(topic, message, message_id):
            return "Message updated"
        else:
            raise Exception("Message could not be updated")

    except Exception as e:
        response.status = 400
        return "Error: " + str(e)

@post ('/delete/topic/<topic>/message_id/<message_id>/token/<token>')
def _(topic, message_id, token):
    try:
        if validate_token(token) == False:
            raise Exception("Token is not valid")

        if delete_message(topic, message_id):
            return "Message deleted"
        else:
            raise Exception("Message could not be deleted")

    except Exception as e:
        response.status = 400
        return "Error: " + str(e)



def to_csv(output):
    print("CSV", output)
    csv_data = "id,message,exp\r\n"
    line = ""

    for message in output["messages"]:
        for key, value in message.items():
            #data += "{},{},{}\r\n".format(key, value["message"], value["exp"])
            line += str(value) + ","
        csv_data += line + "\r\n"
        line = ""
    return csv_data

def to_tsv(output):
    print("CSV", output)
    tsv_data = "id\tmessage\texp\r\n"
    line = ""

    for message in output["messages"]:
        for key, value in message.items():
            #data += "{},{},{}\r\n".format(key, value["message"], value["exp"])
            line += str(value) + "\t"
        tsv_data += line + "\r\n"
        line = ""
    return tsv_data

run (host='127.0.0.1', port=4440, debug=True, reloader=True)





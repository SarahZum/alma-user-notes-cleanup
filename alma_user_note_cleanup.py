#! /usr/bin/env python3

from urllib.request import urlopen
import xml.etree.ElementTree as ET
import requests

# Insert API key for Alma User API (https://developers.exlibrisgroup.com/alma/apis/users)
apiKey = ""
baseURL = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/users"

# Returns User Records
def getUserRecords():
    # Create a text file of primary IDs to retrieve records
    with open("C:/alma-users/user_primary_ids.txt", 'r') as f:
        fileUsers1 = open('C:/alma-users/users.xml', 'a')
        fileUsers1.write('<users>')
        for line in f:
            url = baseURL + "/" + line.rstrip() + "?apikey=" + apiKey
            try:
                newXML = urlopen(url)
                tree = ET.parse(newXML)
                tree.write(fileUsers1, encoding="unicode")
            except urllib.error.HTTPError as e:
                print(e.code)
    fileUsers1.write('</users>')
    fileUsers1.close()
    f.close()

# Looks for text in a note and deletes entire note if found
def deleteNotes():
    fileUsers2 = open('C:/alma-users/users.xml', 'r')
    tree = ET.parse(fileUsers2)
    root = tree.getroot()
    i = 1
    allusers = len(root.getchildren())
    # update to total users in file + 1
    while (i <= allusers):
        notes = root.findall("./user[" + str(i) + "]/user_notes")
        for user_notes in notes:
            children = user_notes.getchildren()
            for note in children: 
                note_text = note.find('note_text').text
                # specify text to look for
                if ('CL RTRND:' in note_text or 'CUR CHKOUT:' in note_text):
                    user_notes.remove(note)
        i += 1
    tree.write('C:/alma-users/users_notes_removed.xml', encoding="unicode")
    fileUsers2.close()

# Loads updated user file 
def loadUpdatedUsers():
    xmlfile = open('C:/alma-users/users_notes_removed.xml', 'r')
    logfile = open('C:/alma-users/loading_log.txt', 'a')
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    headers = {'content-type': 'application/xml'}

    for user in tree.findall('user'):
        xml_string = ET.tostring(user)
        epuid = user.find('primary_id').text

        r = requests.put(baseURL + "/" + epuid +"?apikey=" + apiKey, data=xml_string, headers=headers)

        logfile.write(str(r.status_code))
        logfile.write('\n')
        logfile.write(str(r.content))
        logfile.write('\n\n')

    xmlfile.close()
    logfile.close()

getUserRecords()
deleteNotes()
loadUpdatedUsers()
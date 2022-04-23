#!/usr/bin/env python3

import csv
from re import sub

# load database
database=[]
with open('data-test.csv', mode ='r') as file:
    csvFile = csv.reader(file,delimiter='\t')
    counter = 0
    for line in csvFile:
        counter += 1
        is_comment = False
        if len(line) == 3: # line contains a comment
            name      = str(line[0])
            hname     = str(line[1])
            comment   = str(line[2])
            is_comment = True
        elif len(line) == 5: # line contains an invariant
            name      = str(line[0])
            hname     = str(line[1])
            invariant = str(line[2])
            value     = str(line[3])
            metadata  = str(line[4])
        elif len(line) != 0:
            print("Warning: I could not read line "\
                    + str(counter)\
                    + ". I will ignore it and proceed.")
        is_new = True
        for entry in database:
            if (entry["name"] == name and name != "" )\
                    or ( entry["hname"] == hname and hname != "" ):
                is_new = False
                # try to fill in entries that might be missing
                if ( entry["name"] == ""):
                    entry["name"] = name
                if ( entry["hname"] == ""):
                    entry["hname"] = hname
                # check for inconsistent names and hnames    
                if ( name != "" and entry["name"] != name ):
                    print("Warning: The hname in line "\
                            + str(counter)\
                            + " already exists in the database,"\
                            + " but the corresponding name is different."\
                            + " I will ignore the new name and proceed.")
                if ( hname != "" and entry["hname"] != hname ):
                    print("Warning: The name in line "\
                            + str(counter)\
                            + " already exists in the database,"\
                            + " but the corresponding hname is different."\
                            + "I will ignore the new hname and proceed.")
                if ( is_comment ):
                    if entry["comment"] == "":
                        entry["comment"] = (comment)
                    elif comment != "":
                        entry["comment"] += (", " + comment)
                else:
                    if entry.get(invariant) == None:
                        entry[invariant] = [value, metadata]
                    else:
                        print("Warning: The invariant " + invariant\
                                + " for the knot " + name +"/"+ hname\
                                + " already exists in the database."\
                                + " I will ignore the new value and proceed.")
        if ( is_new ):
            if ( is_comment ):
                database.append(dict({
                    "name": name, 
                    "hname": hname, 
                    "comment": comment}))
            else:
                database.append(dict({
                    "name": name, 
                    "hname": hname, 
                    invariant: [value,metadata],
                    "comment": ""}))



# process database
columns = []
for entry in database:
    columns.extend(entry.keys())
columns = list(dict.fromkeys(columns))
columns.sort()

## make sure comments column is last and hname and name columns are first
for header in ["comment","name","hname"]:
    if header in columns:
        columns.remove(header)

columns.insert(0,"hname")
columns.insert(1,"name")
columns.append("comment")

## compile html file
html = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.1 Transitional//EN">

<head>
<link rel='stylesheet' href='style.css'>

<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<meta content="utf-8" http-equiv="encoding">

<script type='text/javascript'>
function toggleDisplay(cl,id) {
	if (document.getElementById(id).style.display == '') {
		document.getElementById(id).style.display = 'none';
	}
	else {
		document.getElementById(id).style.display = '';
	}
	update_button(cl);
}
</script>
<script type='text/javascript'>
function update_button(cl) {
	var subtabs = document.getElementsByClassName(cl);
	var expanded = true;
	for (itD = 0; itD < subtabs.length; itD++) {
		if (subtabs[itD].style.display=="none"){
			expanded = false;
		}
	}
	if (expanded){
		document.getElementById(cl+"-all").innerHTML = "hide all " + cl;
	}
	else {
		document.getElementById(cl+"-all").innerHTML = "show all " + cl;
	}
}
</script>
<script type='text/javascript'>
        function toggleDisplayClass(cl) {
            	var subtabs = document.getElementsByClassName(cl);
            	var expanded = true;
          	for (itD = 0; itD < subtabs.length; itD++) {
          		if (subtabs[itD].style.display=="none"){
          			expanded = false;
          		}
          	}
          	if (expanded){
          		for (itD = 0; itD < subtabs.length; itD++) {
          			subtabs[itD].style.display="none";
          		}
          	}
          	else {
          		for (itD = 0; itD < subtabs.length; itD++) {
          			subtabs[itD].style.display="";
          		}
          	}
          	update_button(cl);
        }
</script>

<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<script src="sorttable.js"></script>
<!--- https://www.kryogenix.org/code/browser/sorttable/ --->

</head>

<body>
"""

html += "<h1>Computations of \(\\boldsymbol{\\vartheta_c}\)</h1>"
html += "<p class='button-wrapper'><span class='metadata-button' id='metadata-all' onclick=\"toggleDisplayClass('metadata');\">show all metadata</span></p>"

html +="<table class=\"sortable\">"

def str2mathjax( string ):
    string = sub(r"theta_([0-9]*)",r"\\(\\boldsymbol{\\vartheta_{\1}}\\)", string)
    string = sub(r"hname","", string )
    string = sub(r"name","Name", string )
    string = sub(r"comment","Comment", string )
    string = sub(r"rational","rat", string )
    return string

html += "<thead><tr>"
for col in columns:
    if col in ["hname","name","comment"]:
        html += "<th>" + str2mathjax(col) + "</th>\n" 
    else:
        html += "<th class=\"sorttable_numeric\">" + str2mathjax(col) + "</th>\n" 
html += "</tr></thead>\n"

def etype(entry):
    if isinstance( entry, str ):
        return 0    # not an invariant
    if entry == None:
        return 1    # not computed
    if entry[0] == "":
        return 2    # failed to compute invariant
    return 3        # numerical invariant

def sortkey(entry, et):
    if et == 0:
        return entry
    if et == 1:
        return str(-10000)
    if et == 2:
        return str(-1000)
    return entry[0]

def colclass(col):
    if col in ["name","hname","comment"]:
        return col
    return "invariant"

def html_td( identifier, colclass, entry, et ):
    html = "<td sorttable_customkey=\"" + sortkey(entry,et)\
            + "\" class=\"" + colclass + "\">"
    if et == 0:
        html += entry
    elif et == 1:
        html += "—"
    else:
        html += "\n<span\nonclick=\"toggleDisplay('metadata','meta-" + identifier + "');\" \n"
        if et == 2:
            html += "class=\"invariant-missing\">\nX\n"
        else:
            html += "title='click to show metadata'>\n" + entry[0] + "\n"
        html += "</span>\n"
        html += "<div class='metadata' id='meta-" + identifier 
        html += "' style='display:none'>\n"
        html += entry[1]
        html += "\n</div>\n"
        html += "<div class='invariants' id='" + identifier
        html += "' style='display:none'>\n"            
    html += "</td>\n\n"
    return html

html += "<tbody>\n"
for knot in database:
    html += "<tr>\n"
    for col in columns:
        identifier = knot.get("hname") + "_-_" + knot.get("name") + col
        entry = knot.get( col )
        et = etype(entry)
        html += html_td(identifier, colclass(col), entry, et)
    html += "</tr>\n\n\n\n"
html += "</tbody>\n"
html += "</table>\n"
html += "</body>\n"

print(html)

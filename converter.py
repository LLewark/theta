#!/usr/bin/env python3

import csv
from re import sub
import warnings
import csv

import sys
import os

if (len(sys.argv) != 2):
    print("Error: please provide as single parameter the name of the csv file that shall be converted.")
    sys.exit(0)

filename = sys.argv[1]

if not os.path.isfile(filename):
   print("File does not exist.")
   sys.exit(0)



# load database
database=[]
warning_count = 0
with open(filename, mode ='r') as file:
    csvFile = csv.reader(file,delimiter='\t')
    counter = 0
    for line in csvFile:
        counter += 1
        is_comment = False
        if len(line) == 2: # line contains a comment
            name      = str(line[0])
            comment   = str(line[1])
            is_comment = True
        elif len(line) == 4: # line contains an invariant
            name      = str(line[0])
            invariant = str(line[1])
            value     = str(line[2])
            metadata  = str(line[3])
            if (metadata) == "":
               warnings.warn("Please add metadata (e.g. 'program', 'source', 'author', etc.) to the invariant " + invariant\
                  + " for the knot " + name + ".",SyntaxWarning,2)
               warning_count += 1
        elif len(line) != 0:
            warnings.warn("I could not read line "\
                    + str(counter)\
                    + ". I will ignore it and proceed.",SyntaxWarning,2)
            warning_count += 1
            continue
        is_new = True
        for entry in database:
            if entry["name"] == name:
                is_new = False
                if ( is_comment ):
                    if entry["comment"] == "":
                        entry["comment"] = (comment)
                    elif comment != "":
                        entry["comment"] += (", " + comment)
                else:
                    if entry.get(invariant) == None:
                        entry[invariant] = [value, [metadata]]
                    elif entry.get(invariant)[0] == value:
                        entry[invariant][1].append(metadata)
                    else:
                        warnings.warn("The invariant " + invariant\
                                + " for the knot " + name\
                                + " already exists in the database."\
                                + " I will ignore the new value and proceed.",SyntaxWarning,2)
                        warning_count += 1
        if ( is_new ):
            if ( is_comment ):
                database.append(dict({
                    "name": name, 
                    "comment": comment}))
            else:
                database.append(dict({
                    "name": name, 
                    invariant: [value,[metadata]],
                    "comment": ""}))

# sort database
database = sorted(database, key=lambda d: d['name']) 

# process database
columns = []
for entry in database:
    columns.extend(entry.keys())
columns = list(dict.fromkeys(columns))
columns.sort()

predefined_cols = [
        "name",
        "pretzel",
        "torus",
        "theta_0",
        "theta_2",
        "theta_3",
        "theta_5",
        "theta_7",
        "s_2",
        "sigma",
        "tau",
        "epsilon",
        "Genus-4D"]

## make sure comments do not appear as a separate column and name column is first
for header in ["comment"]:
    if header in columns:
        columns.remove(header)
for header in columns:
    if header not in predefined_cols:
        predefined_cols.append(header)
        warnings.warn("Dataset contains the unknown invariant '" + header + "'. Adding it as the last column in the table.",UserWarning,2)

columns = predefined_cols

## compile html file
html = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.1 Transitional//EN">

<head>
<link rel='stylesheet' href='style.css'>

<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<meta content="utf-8" http-equiv="encoding">
<script type='text/javascript'>
	function on(file) {
	    document.getElementById("overlay").style.display = "block";
	    document.getElementById("overlay_container").style.display = "block";
            toggleDisplay(file);
	}

	function off() {
	    document.getElementById("overlay").style.display = "none";
	    document.getElementById("overlay_container").style.display = "none";
	} 
        var list = document.getElementsByClassName("details");
	function toggleDisplay(details) {
		for (itD = 0; itD < list.length; itD++) {
			list[itD].style.display="none";
		}
		document.getElementById(details).style.display = "";
	}
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<script src="sorttable.js"></script>
<!--- https://www.kryogenix.org/code/browser/sorttable/ --->

</head>"""

def str2mathjax( string ):
    string = sub(r"theta_([0-9]*)",r"\\(\\boldsymbol{\\vartheta_{\1}}\\)", string)
    string = sub(r"epsilon",r"\\(\\boldsymbol{\\varepsilon}\\)", string)
    string = sub(r"sigma",r"\\(\\boldsymbol{\\sigma}\\)", string)
    string = sub(r"tau",r"\\(\\boldsymbol{\\tau}\\)", string)
    string = sub(r"s_([0-9]*)",r"\\(\\boldsymbol{s_{\1}}\\)", string)
    string = sub(r"name","Name", string )
    string = sub(r"comment","Comment", string )
    string = sub(r"rational","rat", string )
    return string

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
    if col in ["name","comment"]:
        return col
    return "invariant"

def html_td( identifier, colclass, entry, et, commenttrue):
    html = "<td title='click to view metadata and comments' sorttable_customkey=\"" + sortkey(entry,et)\
            + "\" class=\"" + colclass + "\">"
    if et == 0:
        html += entry
        if commenttrue:
            html += "ᶜ"
    elif et == 1:
        html += ""
    else:
        html += "\n<span\n"
        if et == 2:
            html += "class=\"invariant-missing\">\nX\n"
        else:
            html += ">" + entry[0] + "\n"
        html += "</span>\n"
    html += "</td>\n\n"
    return html

def format_metadata( string ):
    l = [ e.split(":") for e in string.split(";")]
    html = "<table class='table-metadata'>\n"
    for e in l:
        html += "<tr>\n"
        if len(e) == 1:
            html += "<td>comment</td><td>"
            html += e[0]
            html += "</td>"
        elif len(e) == 2:
            html += "<td>"
            html += e[0]
            html += "</td><td>"
            html += e[1]
            html += "</td>"
        else:
            warnings.warn("Some metadata is not formatted correctly. Please correct this!",SyntaxWarning,2)
            warning_count += 1
        html += "</tr>"
    html += "</table>\n"
    return html

def invariant_only( entry ):
    if etype( entry ) == 3:
        return entry[0]
    else: 
        return ""

html += "<body>\n"
html += "<div id=\"overlay\" onclick=\"off()\" style=\"display: none;\"></div>"
html += "<div id=\"overlay_container\" style=\"display: none;\">"
# details as overlay
for knot in database:
    html += "<div class=\"details\" id=\"details-" + knot.get("name") + "\" style='display:none'>\n"
    html += "<h2>" + knot.get("name") + "</h2>\n"
    if knot.get("comment") != "":
        html += "<h3>comments</h3>\n"
        html += "<p>"+ knot.get("comment") + "</p>"
#    else:
#        html += "<div>—no comments—</div>"
    html += "<h3>metadata</h3>\n"
    for col in columns:
        entry = knot.get( col )
        if etype(entry) == 2:
            html += "<h4>" + str2mathjax(col) + "= <span class='invariant-missing'>X</span></h4>\n"
            for e in entry[1]:
                html += format_metadata(e) + "\n"
        if etype(entry) == 3:
            html += "<h4>" + str2mathjax(col) + "=" + entry[0] + "</h4>\n"
            for e in entry[1]:
                html += format_metadata(e) + "\n"
    html += "</div>\n"
html += "</div>\n\n"

# page title
html += "<h1>Table of \(\\boldsymbol{\\vartheta_c}\)-invariants</h1>"
if warning_count != 0:
    html += "<span style=\"color:red\">Warning! There were warnings when this file was generated! Please fix and compile again.</span>"

# table head
html += "<div class='fixHead'>\n\n"
html +="<table class=\"sortable\">"
html += "<thead><tr>"
for col in columns:
    if col in ["name","comment"]:
        html += "<th>" + str2mathjax(col) + "</th>\n" 
    else:
        html += "<th class=\"sorttable_numeric\">" + str2mathjax(col) + "</th>\n" 
html += "</tr></thead>\n"

# some info text
html += """
<p>
The raw data from which this table was compiled can be found on <a href="https://github.com/LLewark/theta">github</a> (<a href='https://github.com/LLewark/theta/blob/master/""" + filename + "'>" + filename + """</a>).
</p>
<p>
You can download a csv-file of this table <a href='https://github.com/LLewark/theta/blob/master/""" + filename.split(".")[0] + """-invariants-only.csv'>here</a>.
</p>
"""

csv_output = open(filename.split(".")[0] + '-invariants-only.csv', 'w')
writer = csv.writer(csv_output)
writer.writerow( ["name"] + [col for col in columns] )

# table content
html += "<tbody>\n"
for knot in database:
    html += "<tr onClick=\"on('details-" + knot.get("name") + "')\">\n"
    writer.writerow( [knot.get("name")] + [invariant_only( knot.get( col ) ) for col in columns] )
    for col in columns:
        identifier = knot.get("name") + col
        entry = knot.get( col )
        commenttrue = (knot.get( "comment" ) != "")
        et = etype(entry)
        html += html_td(identifier, colclass(col), entry, et, commenttrue)
    html += "</tr>\n\n\n\n"
html += "</tbody>\n"
html += "</table>\n"
html += "</div>\n"
html += "</body>\n"

print(html)

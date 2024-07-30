import re
import subprocess
from tkinter import *


with open("input.txt", "w"):
    pass

subprocess.run(["notepad.exe", "input.txt"])

file_text = ""
with open("input.txt", "r") as file:
    for line in file:
        file_text += line
    
    # Look-ahead insertions are used (?<=) but do not appear as part of the resulting match
    customer = list(set(re.findall(r"(?<=Customer: )(.+)", file_text)))
    if len(customer) > 1:
        print("Error: More than 1 customer was included in the input")
    else:
        customer = customer[0]
        
    contact_person = re.search(r"(?<=Primary Contact - )(.+)", file_text) # what about secondary and tertiary?
    contact_number = re.search(r"(?<=  )(.+ )(?=\.+ Secondary Number:)", file_text) # same as above
    
    location_list = re.findall(r"(?<=Group: )(.+)", file_text)
    location_list = sorted(list(set(map(lambda x: x.strip(), location_list))))
    
    device_list = re.findall(r"(?<=\=\=\=\=\=\= Device \=\=\=\=\=\=\n\n)(.+\))(?= \()", file_text)
    device_list = sorted(list(set(device_list)))
    
    
    alert_received_time_list = re.findall(r"(?<=Date\/Time: ).+(?= \()", file_text)
    alert_received_time_list = sorted(list(set(alert_received_time_list)), reverse=True)
    
    device_down_time = re.search(r"(?<=last up as of )(.+)(?=\[)", file_text)


with open("output.txt", "w") as file:
    file.write("Support has received the following alerts.\n\nEdnetics Case: CAS_\n\n")
    file.write("Customer: " + customer)
    file.write("\nPoC: " + contact_person.group()) # currently only takes the primary
    file.write("\nContact Number: " + contact_number.group()) 
    
    file.write("\n\nLocation(s):")
    for location in location_list:
        file.write("\n\t" + location)
            
    file.write("\nDevice Name (IP/MAC): ")
    for device in device_list:
        file.write("\n\t" + device)
        
    file.write("\n\nAlert Date/Time: ")
    for alert_received_time in alert_received_time_list:
        file.write("\n\t" + alert_received_time)
    
    file.write("\nUp Date/Time: TBD")
    file.write("\n\nNext Steps/RFO: Investigating")
    file.write("\n-----------------------------------------------------------------------------------------")
    file.write("\nTime Line (Pacific):")

    file.write("\n" + alert_received_time + " - Alert received")
    file.write("\n" + device_down_time.group() + "- Device down")

subprocess.run(["notepad.exe", "output.txt"])

# window = Tk()
# window.title("Alert Formatter")
# window.geometry('300x300')

# customer_label = Label(window, text="Customer:").grid(row=0, column=0, padx=10, pady=10)
# customer_entry = Entry(window).grid(row=0, column=1)

# window.mainloop()
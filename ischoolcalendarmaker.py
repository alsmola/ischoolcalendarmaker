import sys
import urllib2
import icalendar
from BeautifulSoup import BeautifulSoup
from icalendar import Calendar, Event, vRecur
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil.rrule import MO, TU, WE, TH, FR


class Course:
    def __str__( self ) :
        return self.number + ". " + self.name + "\n" + self.units + " units" + "\n" + "Teacher(s): " + self.teachers + "\n" + self.days + " " + self.time + "\n" + self.location + "\n" + "CCN: " + self.ccn + "\n"


scheduleUrl = raw_input("Enter URL of course schedule:")
year = int(raw_input("What is the 4-digit year:"))
startmonth = int(raw_input("What is the semester start month (1=Jan, 2=Feb, etc):"))
startday =  int(raw_input("What is the semester start day (Instruction begins):"))
endmonth = int(raw_input("What is the semester end month (1=Jan, 2=Feb, etc):"))
endday =  int(raw_input("What is the semester end day (Instruction ends):"))

page = urllib2.urlopen(scheduleUrl)

# Parse schedule page
soup = BeautifulSoup(page)
for incident in soup.findAll("span", {"class" : "views-field-field-courseinst-course-nid"}):
    course = Course()
    courseNameAndNumber = incident.findNext("a").contents[0].split('.')
    course.number = courseNameAndNumber[0].strip()
    course.name = courseNameAndNumber[1].strip()
    course.units = incident.findNext("span", {"class": "views-field-field-course-units-value"}).contents[0].split("&nbsp")[0].replace("(", "")
    teachers = incident.findNext("div", {"class": "views-field-field-courseinst-instructors-nid"})
    course.teachers = ""
    for teacher in teachers.findAll("a"):
        course.teachers += teacher.contents[0] + " "
    daysAndTime = incident.findNext("div", {"class" : "views-field-field-courseinst-days-times-value"}).contents[0].split("Time: ")[1].split(' ')
    course.days = daysAndTime[0].strip()
    if course.days == 'TBA':
        continue
    course.time = daysAndTime[1].strip()
    course.location = incident.findNext("div", {"class": "views-field-field-courseinst-location-value"}).contents[0].split("Location: ")[1]
    course.ccn = incident.findNext("div", {"class":"views-field-field-courseinst-control-number-value"}).contents[0].split("CCN: ")[1]
    course.description = incident.findNext("div", {"class":"views-field-field-course-long-description-value"}).findNext("p").contents[0]
    
    coursetitle = 'Info ' + course.number + ' - ' + course.name
    starttime = course.time.split('-')[0]
    endtime = course.time.split('-')[1]
    startminute = 0
    endminute = 0
    newstartday = startday
    coursedays = [MO]
    if ':' in starttime:
        starthour = int(starttime.split(':')[0])
        startminute = 30    
    else:
        starthour = int(starttime)
    if starthour < 8:
        starthour += 12 
    if ':' in endtime:
        endhour = int(endtime.split(':')[0])
        endminute = 30  
    else:
        endhour = int(endtime)
    if endhour < 8:
        endhour += 12
    
    
    
    if course.days == 'M':
        coursedays = [MO]
        courseStartWeekdays = [0]
    if course.days == 'W':
        coursedays = [WE]
        courseStartWeekdays = [2]
    if course.days == 'F':
        coursedays = [FR]
        courseStartWeekdays = [4]
    if course.days == 'MW':
        coursedays = [MO,WE]
        courseStartWeekdays = [0, 2]
    if course.days == 'WF':
        coursedays = [WE, FR]
        courseStartWeekdays = [2, 4]
    if course.days == 'MWF':
        coursedays = [MO,WE,FR]
        courseStartWeekdays = [0, 2, 4]
    if course.days == 'Tu':
        coursedays = [TU]
        courseStartWeekdays = [1]
    if course.days == 'Th':
        coursedays = [TH]
        courseStartWeekdays = [3]
    if course.days == 'TuTh':
        coursedays = [TU,TH]
        courseStartWeekdays = [1, 3]

    startdate = date(year, startmonth, startday)
    startWeekday = startdate.weekday()
    delta = 0
    while (startWeekday not in courseStartWeekdays):
        delta += 1
        startWeekday += 1
        if (startWeekday > 6):
            startWeekday = 0

    startdate += timedelta(days=delta)
    
    
    # Make .ics file
    cal = Calendar()
    cal.add('prodid', 'I School Course Calendar')
    cal.add('version', '2.0')
    event = Event()
    event.add('summary', coursetitle)
    event.add('location', course.location)
    event.add('dtstart', datetime(year,startdate.month, startdate.day,starthour,startminute,0))
    event.add('dtend', datetime(year,startdate.month,startdate.day,endhour,endminute,0))
    event.add('tzid', 'California-Los_Angeles')
    finishedt = datetime(year,endmonth,endday,0,0,0)
    event.add('rrule', vRecur(freq='weekly', byday=coursedays, until=finishedt))        
    cal.add_component(event)
    f = open(coursetitle + '.ics', 'wb')
    f.write(cal.as_string())
    print 'Wrote: ' + coursetitle + '.ics'
    f.close()

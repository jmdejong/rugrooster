#!/usr/bin/env python3

from urllib.request import urlopen
from datetime import datetime
from datetime import date as ddate
import json

apiurl = "https://rooster.rug.nl/api/{year}/activity/by/course/{code}"

langPrefs = ["en", "nl"]

def _ml(jsonlang):
	for lang in langPrefs:
		val = jsonlang.get(lang, "").strip()
		if val != "":
			return val
	return ""

class Activity:
	
	def __init__(self, jsondata):
		
		self.id = jsondata.get("id")
		self.name = _ml(jsondata.get("name"))
		self.activityName = _ml(jsondata.get("activityName"))
		self.start = datetime(*jsondata.get("start", []))
		self.end = datetime(*jsondata.get("end", []))
		activityType = jsondata.get("activityType", {})
		#print(activityType, type(activityType))
		self.activityTypeName = _ml(activityType.get("name"))
		self.activityTypeSyllabusName = activityType.get("syllabusName").strip()
		self.groups = [_ml(group.get("name")) for group in jsondata.get("groups", [])]
		self.locations = [_ml(location.get("name")) for location in jsondata.get("locationUnits", [])]
		self.courses = [_ml(course.get("name")) for course in jsondata.get("courses", [])]
		self.staff = [_ml(teacher.get("name")) for teacher in jsondata.get("staff", [])]
		remarks = jsondata.get("remarks")
		if remarks:
			self.remarks = json.dumps(remarks)
		else:
			self.remarks = ""
	
	def __lt__(self, other):
		return self.start < other.start
	
	def __gt__(self, other):
		return self.start > other.start
	
	def inlist(self, timeformat=None):
		return "{start} - {end}   {name} {activityName}  {activityTypeName}  {locations}  {groups} {remarks}".format(
			start = self.start if timeformat is None else self.start.strftime(timeformat),
			end = self.end if timeformat is None  else self.end.strftime(timeformat),
			name = self.name,
			activityName = self.activityName,
			activityTypeName = self.activityTypeName,
			locations = " ".join("[{}]".format(location) for location in self.locations),
			groups = ", ".join(self.groups),
			remarks = self.remarks
		)


def make_list(activities, show_id=False, hide_old=False, filters=set()):
	
	last_date = datetime(1,1,1)
	
	text = ""
	for activity in activities:
		date = activity.start.date()
		if activity.id in filters or hide_old and date < ddate.today():
			continue
		if date != last_date:
			text += date.strftime("\n    %A, %d/%m/%y\n")
			last_date = date
		text += activity.inlist("%H:%M")
		if show_id:
			text += activity.id
		text += "\n"
	
	text += "\n\nLast Updated: " + str(datetime.now())
	return text

def load_course(code, year):
	url = apiurl.format(year=year, code=code)
	with urlopen(url) as response:
		data = response.read()
	return json.loads(data)
	

def main():

	with open("profile.json") as f:
		profile = json.load(f)

	schedule = []
	for course, year in profile["courses"]:
		schedule.extend(load_course(course, year))
	
	activities = [Activity(act) for act in schedule]
	activities.sort()
	
	filters = set(profile["filter"])
	
	full_text = make_list(activities)
	edit_text = make_list(activities, True)
	filtered_text = make_list(activities, False, True, filters)
	
	print(edit_text)
	
	with open("templates/index.html") as f:
		template = f.read()

	with open("html/full.html", "w") as of:
		of.write(template.format(full_text))
	with open("html/edit.html", "w") as of:
		of.write(template.format(edit_text))
	with open("html/index.html", "w") as of:
		of.write(template.format(filtered_text))
	

if __name__ == "__main__":
	main()

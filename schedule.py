#!/usr/bin/env python3

from urllib.request import urlopen
from datetime import datetime
from datetime import date as ddate
from os.path import join
import os
import json
import glob

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
			if date.isocalendar()[1] != last_date.isocalendar()[1]:
				text += "\n---------------- Week " + str(date.isocalendar()[1])
			text += date.strftime("\n  %a, %d/%m/%y\n")
			last_date = date
		text += activity.inlist("%H:%M")
		if show_id:
			text += "  " + activity.id
		text += "\n"
	
	text += "\n\nLast Updated: " + str(datetime.now()) + " UTC"
	return text

def load_course(code, year):
	url = apiurl.format(year=year, code=code)
	with urlopen(url) as response:
		data = response.read()
	return json.loads(data)
	

def update_profile(profile_path):

	with open(profile_path) as f:
		profile = json.load(f)
	
	if "source" in profile:
		with urlopen(profile["source"]) as response:
			extern = response.read()
		if "delimiters" in profile:
			start, end = profile["delimiters"]
			extern = extern.partition(start)[2].partition(end)[0]
		profile = json.loads(extern)

	schedule = []
	for course, year in profile["courses"]:
		schedule.extend(load_course(course, year))
	
	activities = [Activity(act) for act in schedule]
	activities.sort()
	
	filters = set(profile["filter"])
	
	full_text = make_list(activities)
	edit_text = make_list(activities, True)
	filtered_text = make_list(activities, False, True, filters)
	
	with open(join("templates", "index.html")) as f:
		template = f.read()
		
	outdir = join("html", os.path.basename(profile_path)[:-5])
	
	os.makedirs(outdir, exist_ok=True)

	with open(join(outdir, "full.html"), "w") as of:
		of.write(template.format(full_text))
	with open(join(outdir, "edit.html"), "w") as of:
		of.write(template.format(edit_text))
	with open(join(outdir, "index.html"), "w") as of:
		of.write(template.format(filtered_text))

def main():
	
	for profile in glob.glob(join("profiles", "*.json")):
		try:
			update_profile(profile)
		except Exception as e:
			print("failed to load", profile)
			print(type(e), e)
	

if __name__ == "__main__":
	main()

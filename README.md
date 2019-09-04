# RUG Rooster 🐓

This is supposed to help with creating a better schedule

This adds the options to choose individual (weekly) items to remove from the schedule.
Also, the result is pure static lightweight html, and can be viewed on any crappy browser on a shitty internet connection (for example in the train or in a very busy lecture).

# How to run

There are several options for running this.
If possible, you could get a server and run this dayly with a cron entry.
You could also run it manually, and host the resulting pages on some static page host (for example github pages).

# Profiles

You can create a profile json file in the profiles directory.
The profile will hold the courses you choose and the filtered activities.

For courses you need the course code.
For filtering activities you need the id of that activity.
You can get that id by looking it up in the produced edit.html file.

Profiles can also link to an external page to be used.

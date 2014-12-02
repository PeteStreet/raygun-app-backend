I built this backend (rather hastily) to power the social networking features of bespoken, an Android app designed for spoken word poets to collaborate and share their work.  Originally I built the database using Google Cloud SQL, but about halfway through switched over to the Datastore.  

This backend covers the very basics of what is necessary for a social networking app.  User accounts (through Google's account system, not a 'bespoke' one), posting (both written poems and audio recordings from the user's phone), commenting, and following are all available here.  The models set up at the top of the python file are rather simple, though they still leave a little room to grow.

The two of the backend that were more hastily done than I would have liked are profile pictures and search.  Currently, search only tests the query against the list of poem titles, and the profile pictures are hardcoded tv characters.  

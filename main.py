import os
import logging
import webapp2
import time
import datetime
from random import randrange
import json

import models

from google.appengine.api import app_identity
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images

import jinja2

template_path = os.path.join(os.path.dirname(__file__))

jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path),
    autoescape=True
)

#Global values
likePoints = 3
dislikePoints = 1
commentPoints = 5
postPoints = 10


#a helper class
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja2_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


#Dynamic loading for the listing pages is a critical next feature.
class HomeListingNewHandler(Handler):
    def get(self):
        # get the latest 30 slogans globally.
        sloganRows = models.slogan.gql('ORDER BY createdAt DESC limit 30').fetch()

        #Attach profile pictures to each slogan in the listing.
        userRows = []
        for sRow in sloganRows:
            userRows.append(models.user.get_by_id(sRow.uniqueAuthorID))

        template_values = {"sloganRows": sloganRows, "userRows": userRows}
        template = jinja2_env.get_template('html/listing.html')
        self.response.out.write(template.render(template_values))

class HomeListingTrendingHandler(Handler):
    def get(self):
        # get the 30 top trending slogans globally.
        sloganRows = models.slogan.gql('ORDER BY globalRank DESC limit 30').fetch()

        currentTime = datetime.datetime.now()
        for sRow in sloganRows:
            #put the timediff into some exponential decay function - this needs tweaking!
            timeDiff = 100000 * 10**(-1 * ((currentTime - sRow.createdAt).total_seconds()) / 100000)
            sRow.temporalRank = int(timeDiff * sRow.globalRank)
        sortedSlogans = sorted(sloganRows, key=tempRank, reverse=True)

        #Attach profile pictures to each slogan in the listing.
        userRows = []
        for sRow in sortedSlogans:
            userRows.append(models.user.get_by_id(sRow.uniqueAuthorID))

        template_values = {"sloganRows": sortedSlogans, "userRows": userRows}
        template = jinja2_env.get_template('html/listing.html')
        self.response.out.write(template.render(template_values))

class HomeListingTopHandler(Handler):
    def get(self):
        # get the 30 all-time top slogans globally.
        sloganRows = models.slogan.gql('ORDER BY globalRank DESC LIMIT 30').fetch()

        #Attach profile pictures to each slogan in the listing.
        userRows = []
        for sRow in sloganRows:
            userRows.append(models.user.get_by_id(sRow.uniqueAuthorID))

        template_values = {"sloganRows": sloganRows, "userRows": userRows}
        template = jinja2_env.get_template('html/listing.html')
        self.response.out.write(template.render(template_values))

class SubpageListingNewHandler(Handler):
    def get(self, subpage):
        # get the 30 newest slogans for a specific subpage
        sloganRows = models.slogan.gql('WHERE subpageTag1 = :1 ORDER BY createdAt LIMIT 20', subpage).fetch()
        sloganRows2 = models.slogan.gql('WHERE subpageTag2 = :1 ORDER BY createdAt LIMIT 20', subpage).fetch()

        #prior attepts to get the first 30 results matching either tag from GQL failed spectacularly, so instead I'm joining the lists manually.
        sloganRows = sloganRows + sloganRows2
        sortedSlogans = sorted(sloganRows, key=lambda sRow: sRow.createdAt, reverse=True)

        #Attach profile pictures to each slogan in the listing.
        userRows = []
        for sRow in sortedSlogans:
            userRows.append(models.user.get_by_id(sRow.uniqueAuthorID))

        template_values = {"sloganRows": sortedSlogans, "userRows": userRows}
        template = jinja2_env.get_template('html/listing.html')
        self.response.out.write(template.render(template_values))

class SubpageListingTrendingHandler(Handler):
    def get(self, subpage):
        # get the top trending slogans for a specific subpage
        sloganRows = models.slogan.gql('WHERE subpageTag1 = :1 ORDER BY globalRank LIMIT 20', subpage).fetch()
        sloganRows2 = models.slogan.gql('WHERE subpageTag2 = :1 ORDER BY globalRank LIMIT 20', subpage).fetch()

        #prior attepts to get the first 30 results matching either tag from GQL failed spectacularly, so instead I'm joining the lists manually.
        sloganRows = sloganRows + sloganRows2
        currentTime = datetime.datetime.now()
        for sRow in sloganRows:
            #put the timediff into some exponential decay function - this needs tweaking!
            timeDiff = 100000 * 10**(-1 * ((currentTime - sRow.createdAt).total_seconds()) / 100000)
            sRow.temporalRank = int(timeDiff * sRow.globalRank)
        sortedSlogans = sorted(sloganRows, key=tempRank, reverse=True)

        #Attach profile pictures to each slogan in the listing.
        userRows = []
        for sRow in sortedSlogans:
            userRows.append(models.user.get_by_id(sRow.uniqueAuthorID))

        template_values = {"sloganRows": sortedSlogans, "userRows": userRows}
        template = jinja2_env.get_template('html/listing.html')
        self.response.out.write(template.render(template_values))

class SubpageListingTopHandler(Handler):
    def get(self, subpage):
        # get the 30 all-time top slogans for a specific subpage
        sloganRows = models.slogan.gql('WHERE subpageTag1 = :1 ORDER BY globalRank LIMIT 20', subpage).fetch()
        sloganRows2 = models.slogan.gql('WHERE subpageTag2 = :1 ORDER BY globalRank LIMIT 20', subpage).fetch()

        #prior attepts to get the first 30 results matching either tag from GQL failed spectacularly, so instead I'm joining the lists manually.
        sloganRows = sloganRows + sloganRows2
        sortedSlogans = sorted(sloganRows, key=lambda sRow: sRow.globalRank, reverse=True) #for that descending order

        #Attach profile pictures to each slogan in the listing.
        userRows = []
        for sRow in sortedSlogans:
            userRows.append(models.user.get_by_id(sRow.uniqueAuthorID))

        template_values = {"sloganRows": sortedSlogans, "userRows": userRows}
        template = jinja2_env.get_template('html/listing.html')
        self.response.out.write(template.render(template_values))

def tempRank(sortItem): #The lambda function was being prissy, so I'm using this external function to sort temporal ranks instead
    return sortItem.temporalRank


class SearchHandler(Handler):
    def get(self):
        asdf = 0


class ProfileHandler(Handler):
    def get(self, profile_id):
        #general method for displaying a user profile
        userSloganRows = []
        userExists = False
        isCurrentUser = False

        uRow = models.user.get_by_id(int(profile_id))

        if uRow:
            userExists = True
            if uRow.uniqueGivenID == users.get_current_user().user_id():
                isCurrentUser = True

            sloganRows = models.slogan.gql('WHERE uniqueAuthorID = :1 ORDER BY createdAt DESC', int(profile_id))
            for sRow in sloganRows:
                if sRow.uniqueAuthorID == uRow.key.id(): # If the user wrote this slogan
                    userSloganRows.append(sRow)

            template = jinja2_env.get_template('html/profile.html')
            template_values = {"uRow": uRow, "sloganRows": userSloganRows, "isCurrentUser": isCurrentUser}
            self.response.out.write(template.render(template_values))

        if not userExists:
            #self.response.out.write("Create yourself a profile")
            self.redirect("/app/create-profile")

class ProfileEditHandler(Handler, blobstore_handlers.BlobstoreUploadHandler):
    def get(self, profile_id, error=0):
        #general method for displaying the profile editing form
        uRow = models.user.get_by_id(int(profile_id))

        upload_url = blobstore.create_upload_url('/app/user/' + profile_id + '/edit')

        errorText = ""
        if error == "0":
            errorText = "No Error"
        elif error == "1":
            errorText = "That username is already taken!  Pick a different one."

        if uRow:
            userExists = True
            if uRow.uniqueGivenID == users.get_current_user().user_id(): #only display the form if it is the current user.
                template = jinja2_env.get_template('html/edit-profile.html')
                template_values = {"uRow": uRow, "upload_url": upload_url, "error": errorText}
                self.response.out.write(template.render(template_values))
            else:
                template = jinja2_env.get_template('html/edit-profile-error.html')
                template_values = {"uRow": uRow}
                self.response.out.write(template.render(template_values))


    def post(self, profile_id):
        userNickname = self.request.get('username')
        userBio = self.request.get('user_bio')
        upload = False
        if len(self.get_uploads('pic')) > 0:
            upload = self.get_uploads('pic')[0]

        theUser = models.user.get_by_id(int(profile_id))
        currentUser = users.get_current_user().user_id()

        #check to see if the userNickname provided is unique
        userRows = models.user.gql('')
        isUniqueUsername = True
        if len(userNickname) > 0:
            for uRow in userRows:
                if uRow.nickname == userNickname:
                    isUniqueUsername = False
                    break

        if theUser.uniqueGivenID == str(currentUser):
            for i in range(0,1): #this for loop is sucky, and only exists so I can break out of it on a username clash error.
                if len(userNickname) > 0:
                    logging.debug(isUniqueUsername)
                    if isUniqueUsername:
                        theUser.nickname = userNickname
                    else:
                        self.redirect("/app/user/" + str(profile_id) + "/edit/1")
                        break #save us from the redirect that happens below
                if userBio:
                    theUser.bio = userBio
                if upload:
                    theUser.picture = upload.key()
                    theUser.pictureURL = images.get_serving_url(upload.key())
                theUser.put()
                time.sleep(.15) #This helps keep the eventual consistency at bay
                self.redirect("/app/user/" + str(profile_id))

        else:
            template = jinja2_env.get_template('html/edit-profile-error.html')
            template_values = {"uRow": theUser}
            self.response.out.write(template.render(template_values))



class MyProfileHandler(Handler):
    def get(self):
        #specific method for redirecting to the current user's profile
        userRows = models.user.gql('')
        currentUser = users.get_current_user().user_id()

        userExists = False
        for uRow in userRows:
            if uRow.uniqueGivenID == currentUser:
                userExists = True
                redirString = "/app/user/" + str(uRow.key.id())
                self.redirect(redirString)
                break

        if not userExists:
            self.redirect("/app/create-profile")

class MyProfileEditHandler(Handler):
    def get(self):
        #specific method for redirecting to the current user's profile
        userRows = models.user.gql('')
        currentUser = users.get_current_user().user_id()

        userExists = False
        for uRow in userRows:
            if uRow.uniqueGivenID == currentUser:
                userExists = True
                redirString = "/app/user/" + str(uRow.key.id()) + "/edit"
                self.redirect(redirString)
                break

        if not userExists:
            self.redirect("/app/create-profile")

class MyProfileSlogaramaHandler(Handler):
    def get(self):
        #specific method for redirecting to the current user's slogarama page
        userRows = models.user.gql('')
        currentUser = users.get_current_user().user_id()

        userExists = False
        for uRow in userRows:
            if uRow.uniqueGivenID == currentUser:
                userExists = True
                redirString = "/app/user/" + str(uRow.key.id()) + "/slogarama"
                self.redirect(redirString)
                break

        if not userExists:
            self.redirect("/app/create-profile")


class ProfileSlogansHandler(Handler):
    def get(self):
        asdf = 0

class ProfileTopSlogansHandler(Handler):
    def get(self):
        asdf = 0

class ProfileCommentsHandler(Handler):
    def get(self):
        asdf = 0


class SloganHandler(Handler):
    def get(self, slogan_id):
        #general method for displaying a slogan on its own page.
        sloganExists = False
        sRow = models.slogan.get_by_id(int(slogan_id))
        if sRow:
            sloganExists = True
            commentRows = models.comment.gql('WHERE uniqueSloganID = :1 LIMIT 2', int(slogan_id))
            comments = []
            commentCounter = 0 #this limits how many comments are shown on the slogan page.
            for cRow in commentRows:
                comments.append(cRow)

            template_values = {"sRow": sRow, "comments": comments}
            template = jinja2_env.get_template('html/slogan.html')
            self.response.out.write(template.render(template_values))

        if not sloganExists:
            self.response.out.write("This slogan doesn't exist!")



class SloganCommentsHandler(Handler):
    def get(self, slogan_id):
        commentRows = models.comment.gql('WHERE uniqueSloganID = :1 ORDER BY createdAt DESC', int(slogan_id))
        comments = []
        for cRow in commentRows:
            if cRow.uniqueSloganID == int(slogan_id): # If the comments belong to this particular slogan
                comments.append(cRow)

        sloganRows = models.slogan.gql('')
        for sRow in sloganRows:
            if sRow.key.id() == int(slogan_id):
                template_values = {"comments": comments, "sRow": sRow}
                template = jinja2_env.get_template('html/comments.html')
                self.response.out.write(template.render(template_values))
                break

    def post(self):
        #first, collect data to be placed into the comment entity
        commentText = self.request.get("comment_text")
        uniqueSloganID = self.request.get("slogan_id")

        userRows = models.user.gql('')
        currentUser = users.get_current_user().user_id()
        userNickname = ""
        commentAuthorID = 0
        for uRow in userRows:
            if uRow.uniqueGivenID == currentUser:
                userNickname = uRow.nickname
                commentAuthorID = uRow.key.id()
                uRow.slogarma += commentPoints #add slogarama points for the commenter
                uRow.put()

        #increment "numComments" for the slogan.
        sloganRows = models.slogan.gql('')
        for sRow in sloganRows:
            if sRow.key.id() == int(uniqueSloganID):
                sRow.numComments += 1
                sRow.globalRank += commentPoints
                sRow.put()

        #create a new comment entity.
        c = models.comment(uniqueAuthorID = commentAuthorID, uniqueSloganID = int(uniqueSloganID),
                           userNickname = userNickname, text = commentText)
        c.put()

        #add slogarama points for the commentee
        theSlogan = models.slogan.get_by_id(int(uniqueSloganID))
        sloganAuthor = models.user.get_by_id(theSlogan.uniqueAuthorID)
        if sloganAuthor.key.id() != commentAuthorID:
            sloganAuthor.slogarma += commentPoints
            sloganAuthor.put()

        time.sleep(.15) #This helps keep the eventual consistency at bay

        self.redirect("/app/slogan/" + uniqueSloganID + "/comments")


class AddSloganHandler(Handler):
    def get(self):
        if users.get_current_user():
            currentUser = users.get_current_user().user_id()
            profileExists = False

            userRows = models.user.gql('')
            for uRow in userRows:
                if uRow.uniqueGivenID == currentUser:
                    profileExists = True

                    template_values = {}
                    template = jinja2_env.get_template('html/add-slogan.html')
                    self.response.out.write(template.render(template_values))
                    break
            if not profileExists:
                self.redirect('/app/create-profile')

    def post(self):
        if True:
            #posting a new slogan
            sloganText = self.request.get('slogan_text')
            manualID = self.request.get('unique_id')
            checkedBoxes = self.request.get_all('single-check')

            currentUser = False
            if users.get_current_user():
                currentUser = users.get_current_user().user_id()
            userRows = models.user.gql('')

            #if the user is logged in (posting from a web browser), use their id:
            if currentUser:
                for uRow in userRows:
                    if uRow.uniqueGivenID == currentUser:
                        if sloganText:
                            if len(sloganText) > 65:
                                sloganText = sloganText[0:65] #truncate the end of the slogan if it's too long.

                            #get the number of words in the string and choose one of them at random to highlight.
                            numWords = len(sloganText.split())
                            highlightWord = int(randrange(numWords))

                            tag1 = "null"
                            tag2 = "null"
                            if len(checkedBoxes) == 2:
                                tag1 = checkedBoxes[0]
                                tag2 = checkedBoxes[1]
                            elif len(checkedBoxes) == 1:
                                tag1 = checkedBoxes[0]

                            s = models.slogan(uniqueAuthorID = uRow.key.id(), authorNickname = uRow.nickname,
                                              subpageTag1 = tag1, subpageTag2 = tag2,
                                              globalRank = 0, highlightedWord = highlightWord,
                                              numComments = 0, numLikes = 0, numDislikes = 0, text = sloganText.upper())
                            sloganID = s.put().id() #put the slogan in the datastore

                            u = models.user.get_by_id(uRow.key.id())
                            u.slogarma += postPoints
                            u.put()

                            #this is a janky way to get around the common eventual consistency issue...
                            time.sleep(.11)
                            sloganExists = False
                            for x in range(0, 3):
                                sloganRows = models.slogan.gql('')
                                for sRow in sloganRows:
                                    if sRow.key.id() == sloganID:
                                        sloganExists = True
                                        self.redirect('/app/slogan/%s' % int(sloganID))
                                        break
                                    else:
                                        time.sleep(.15)
                                if sloganExists:
                                    break #break out of the containing loop
                            if not sloganExists:  #if it's too slow, don't keep on querying the datastore.
                                self.redirect('/app/listing/new')
            else:
                for uRow in userRows:
                    if uRow.uniqueGivenID == manualID:
                        userExists = True
                        if sloganText:
                            #get the number of words in the string and choose one of them at random to highlight.
                            numWords = len(sloganText.split())
                            highlightWord = int(randrange(numWords))
                            s = models.slogan(uniqueAuthorID = manualID, authorNickname = uRow.nickname,
                                                          globalRank = 0, highlightedWord = highlightWord,
                                                          numComments = 0, numLikes = 0, numDislikes = 0, text = sloganText.upper())
                            s.put() #put the slogan in the datastore
                            sloganID = s.put().id() #put the slogan in the datastore

                            #this is a janky way to get around the common eventual consistency issue...
                            time.sleep(.2)
                            sloganExists = False
                            for x in range(0, 3):
                                sloganRows = models.slogan.gql('')
                                for sRow in sloganRows:
                                    if sRow.key.id() == sloganID:
                                        sloganExists = True
                                        self.redirect('/app/slogan/%s' % int(sloganID))
                                        break
                                    else:
                                        time.sleep(.2)
                            if not sloganExists:  #if it's too slow, don't keep on querying the datastore.
                                self.redirect('/app/listing/new')


class CreateProfileHandler(Handler, blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/app/create-profile')

        template_values = {"upload_url": upload_url}
        template = jinja2_env.get_template('html/create-profile.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        newUserNickname = self.request.get('username')
        userEmail = self.request.get('email')
        userBio = self.request.get('user_bio')
        upload = False
        if len(self.get_uploads('pic')) > 0:
            upload = self.get_uploads('pic')[0]

        #check to see if the userNickname provided is unique
        userRows = models.user.gql('')
        isUniqueUsername = True
        for uRow in userRows:
            if uRow.nickname == newUserNickname:
                isUniqueUsername = False

        if isUniqueUsername:
            currentUser = users.get_current_user().user_id()

            if upload:
                u = models.user(uniqueGivenID = currentUser, nickname = newUserNickname, slogarma = 0, email = userEmail,
                                bio = userBio, numSlogans = 0, picture = upload.key(), pictureURL = images.get_serving_url(upload.key()))
            else:
                u = models.user(uniqueGivenID = currentUser, nickname = newUserNickname, slogarma = 0,
                                email = userEmail, bio = userBio, numSlogans = 0)
            u.put()

            self.redirect("/app/listing/new")

        else:
            error = "That username already exists!  Please pick a different one."
            template = jinja2_env.get_template('html/create-profile.html')
            template_values = {"error": error}
            self.response.out.write(template.render(template_values))


class SlogaramaHandler(Handler):
    def get(self, profile_id):
        uRow = models.user.get_by_id(int(profile_id))
        if uRow:
            template_values = {"slogaramaPoints": uRow.slogarma}
            template = jinja2_env.get_template('html/slogarama.html')
            self.response.out.write(template.render(template_values))


class DeleteSloganHandler(Handler):
    def post(self):
        asdf = 99
        '''poemRows = poem.gql('').fetch()
        userRows = user.gql('').fetch()
        poemToDeleteID = self.request.get("poemKeyID")

        for pRow in poemRows:
            if str(pRow.key.id()) == poemToDeleteID:
                pRow.key.delete() #remove the 'poem' entity

        self.redirect("/app/my-profile")'''

class DeleteCommentHandler(Handler):
    def post(self):
        asdf = 8


class UpVoteHandler(Handler):
    def post(self):
        logging.info(self.request.body)
        data = json.loads(self.request.body)
        slogan = models.slogan.get_by_id(int(data['sloganKey']))

        votedSloganIDs = models.vote.gql('WHERE uniqueSloganID = :1', slogan.key.id()).fetch()
        hasUserVoted = False
        currentUser = users.get_current_user().user_id()
        for vs in votedSloganIDs:
            if vs.uniqueVoterID == currentUser:
                hasUserVoted = True

        if not hasUserVoted:
            slogan.numLikes += 1
            slogan.globalRank += likePoints
            slogan.put()
            vote = models.vote(uniqueVoterID = str(currentUser), uniqueSloganID = slogan.key.id())
            vote.put()

class DownVoteHandler(Handler):
    def post(self):
        logging.info(self.request.body)
        data = json.loads(self.request.body)
        slogan = models.slogan.get_by_id(int(data['sloganKey']))

        votedSloganIDs = models.vote.gql('WHERE uniqueSloganID = :1', slogan.key.id()).fetch()
        hasUserVoted = False
        currentUser = users.get_current_user().user_id()
        for vs in votedSloganIDs:
            if vs.uniqueVoterID == currentUser:
                hasUserVoted = True

        if not hasUserVoted:
            slogan.numDislikes += 1
            slogan.globalRank += dislikePoints
            slogan.put()
            vote = models.vote(uniqueVoterID = str(currentUser), uniqueSloganID = slogan.key.id())
            vote.put()


class CheckProfileHandler(Handler):
    def get(self):
        hasProfile = False
        if users.get_current_user():
            currentUser = users.get_current_user().user_id()
            userRows = models.user.gql('')
            for uRow in userRows:
                if uRow.uniqueGivenID == currentUser:
                    hasProfile = True

        template_values = {"hasProfile": hasProfile}
        template = jinja2_env.get_template('html/check-profile.html')
        self.response.out.write(template.render(template_values))


def handle_404(request, response, exception):
    logging.exception(exception)
    template = jinja2_env.get_template('html/404.html')
    response.write(template.render())
    response.set_status(404)


def handle_500(request, response, exception):
    logging.exception(exception)
    template = jinja2_env.get_template('html/500.html')
    response.write(template.render())
    response.set_status(500)


application = webapp2.WSGIApplication([
    ("/app/upvote/", UpVoteHandler),
    ("/app/downvote/", DownVoteHandler),
    ("/app/listing/new", HomeListingNewHandler),
    ("/app/listing/trending", HomeListingTrendingHandler),
    ("/app/listing/top", HomeListingTopHandler),
    ("/app/listing/([\w\-]+)/new", SubpageListingNewHandler),
    ("/app/listing/([\w\-]+)/trending", SubpageListingTrendingHandler),
    ("/app/listing/([\w\-]+)/top", SubpageListingTopHandler),
    ("/app/search", SearchHandler),
    ("/app/user/(\d+)", ProfileHandler),
    ("/app/user/(\d+)/edit", ProfileEditHandler),
    ("/app/user/(\d+)/edit/(\d+)", ProfileEditHandler),
    ("/app/user/(\d+)/slogans", ProfileSlogansHandler),
    ("/app/user/(\d+)/top-slogans", ProfileTopSlogansHandler),
    ("/app/user/(\d+)/comments", ProfileCommentsHandler),
    ("/app/user/(\d+)/slogarama", SlogaramaHandler),
    ("/app/my-profile", MyProfileHandler),
    ("/app/my-profile/edit", MyProfileEditHandler),
    ("/app/my-profile/slogarama", MyProfileSlogaramaHandler),
    ("/app/create-profile", CreateProfileHandler),
    ("/app/slogan/(\d+)", SloganHandler),
    ("/app/slogan/(\d+)/share", SloganHandler),
    ("/app/slogan/(\d+)/comments", SloganCommentsHandler),
    ("/app/addComment", SloganCommentsHandler),
    ("/app/addSlogan", AddSloganHandler),
    ("/app/deleteSlogan", DeleteSloganHandler),
    ("/app/checkProfile", CheckProfileHandler),
], debug=True)
application.error_handlers[404] = handle_404
#application.error_handlers[500] = handle_500
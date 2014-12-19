import os
import logging
import webapp2
import time
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


class HomeListingNewHandler(Handler):
    def get(self):
        # get the latest 30 slogans globally.
        sloganRows = models.slogan.gql('ORDER BY createdAt DESC limit 30').fetch()

        template_values = {"sloganRows": sloganRows}
        template = jinja2_env.get_template('html/listing.html')
        self.response.out.write(template.render(template_values))

class HomeListingTrendingHandler(Handler):
    def get(self):
        # get the 30 top trending slogans globally.
        sloganRows = models.slogan.gql('ORDER BY globalRank DESC limit 30').fetch()

        template_values = {"sloganRows": sloganRows}
        template = jinja2_env.get_template('html/listing.html')
        self.response.out.write(template.render(template_values))

class HomeListingTopHandler(Handler):
    def get(self):
        # get the 30 all-time top slogans globally.
        sloganRows = models.slogan.gql('ORDER BY globalRank DESC LIMIT 30').fetch()

        template_values = {"sloganRows": sloganRows}
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


        template_values = {"sloganRows": sortedSlogans}
        template = jinja2_env.get_template('html/listing.html')
        self.response.out.write(template.render(template_values))

class SubpageListingTrendingHandler(Handler):
    def get(self, subpage):
        # get the 30 top trending slogans for a specific subpage
        sloganRows = models.slogan.gql('WHERE subpageTag1 = :1 ORDER BY globalRank LIMIT 20', subpage).fetch()
        sloganRows2 = models.slogan.gql('WHERE subpageTag2 = :1 ORDER BY globalRank LIMIT 20', subpage).fetch()

        #prior attepts to get the first 30 results matching either tag from GQL failed spectacularly, so instead I'm joining the lists manually.
        sloganRows = sloganRows + sloganRows2
        sortedSlogans = sorted(sloganRows, key=lambda sRow: sRow.globalRank, reverse=True)

        template_values = {"sloganRows": sortedSlogans}
        template = jinja2_env.get_template('html/listing.html')
        self.response.out.write(template.render(template_values))

class SubpageListingTopHandler(Handler):
    def get(self, subpage):
        # get the 30 all-time top slogans for a specific subpage
        sloganRows = models.slogan.gql('WHERE subpageTag1 = :1 ORDER BY globalRank LIMIT 20', subpage).fetch()
        sloganRows2 = models.slogan.gql('WHERE subpageTag2 = :1 ORDER BY globalRank LIMIT 20', subpage).fetch()

        #prior attepts to get the first 30 results matching either tag from GQL failed spectacularly, so instead I'm joining the lists manually.
        sloganRows = sloganRows + sloganRows2
        sortedSlogans = sorted(sloganRows, key=lambda sRow: sRow.globalRank, reverse=True)

        template_values = {"sloganRows": sortedSlogans}
        template = jinja2_env.get_template('html/listing.html')
        self.response.out.write(template.render(template_values))


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
            self.redirect("/create-profile")


class MyProfileHandler(Handler):
    def get(self):
        #specific method for redirecting to the current user's profile
        userRows = models.user.gql('')
        currentUser = users.get_current_user().user_id()

        userExists = False
        for uRow in userRows:
            if uRow.uniqueGivenID == currentUser:
                userExists = True
                redirString = "/user/" + str(uRow.key.id())
                self.redirect(redirString)
                break

        if not userExists:
            self.redirect("/create-profile")

class MyProfileSlogaramaHandler(Handler):
    def get(self):
        #specific method for redirecting to the current user's slogarama page
        userRows = models.user.gql('')
        currentUser = users.get_current_user().user_id()

        userExists = False
        for uRow in userRows:
            if uRow.uniqueGivenID == currentUser:
                userExists = True
                redirString = "/user/" + str(uRow.key.id() + "/slogarama")
                self.redirect(redirString)
                break

        if not userExists:
            self.redirect("/create-profile")


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
                uRow.slogarma += commentPoints
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

        self.redirect("/slogan/" + uniqueSloganID + "/comments")


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
                self.redirect('/create-profile')

    def post(self):
        if True:
            #posting a new slogan
            sloganText = self.request.get('slogan_text')
            manualID = self.request.get('unique_id')

            currentUser = False
            if users.get_current_user():
                currentUser = users.get_current_user().user_id()
            userRows = models.user.gql('')

            #if the user is logged in (posting from a web browser), use their id:
            if currentUser:
                for uRow in userRows:
                    if uRow.uniqueGivenID == currentUser:
                        if sloganText:
                            #get the number of words in the string and choose one of them at random to highlight.
                            numWords = len(sloganText.split())
                            highlightWord = int(randrange(numWords))

                            s = models.slogan(uniqueAuthorID = uRow.key.id(), authorNickname = uRow.nickname,
                                              subpageTag1 = "tag1", subpageTag2 = "tag2",
                                              globalRank = 0, highlightedWord = highlightWord,
                                              numComments = 0, numLikes = 0, numDislikes = 0, text = sloganText.upper())
                            sloganID = s.put().id() #put the slogan in the datastore

                            #this is a janky way to get around the common eventual consistency issue...
                            time.sleep(.2)
                            sloganExists = False
                            for x in range(0, 3):
                                sloganRows = models.slogan.gql('')
                                for sRow in sloganRows:
                                    if sRow.key.id() == sloganID:
                                        sloganExists = True
                                        self.redirect('/slogan/%s' % int(sloganID))
                                        break
                                    else:
                                        time.sleep(.2)
                            if not sloganExists:  #if it's too slow, don't keep on querying the datastore.
                                self.redirect('/listing/new')
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
                                        self.redirect('/slogan/%s' % int(sloganID))
                                        break
                                    else:
                                        time.sleep(.2)
                            if not sloganExists:  #if it's too slow, don't keep on querying the datastore.
                                self.redirect('/listing/new')


class CreateProfileHandler(Handler, blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/create-profile')

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

            self.redirect("/listing/new")

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

        self.redirect("/my-profile")'''

class DeleteCommentHandler(Handler):
    def post(self):
        asdf = 8


class UpVoteHandler(Handler):
    def post(self):
        logging.info(self.request.body)
        data = json.loads(self.request.body)
        slogan = models.slogan.get_by_id(int(data['sloganKey']))
        slogan.numLikes += 1
        slogan.globalRank += likePoints
        slogan.put()

class DownVoteHandler(Handler):
    def post(self):
        logging.info(self.request.body)
        data = json.loads(self.request.body)
        slogan = models.slogan.get_by_id(int(data['sloganKey']))
        slogan.numDislikes += 1
        slogan.globalRank += dislikePoints
        slogan.put()


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
    ("/upvote/", UpVoteHandler),
    ("/downvote/", DownVoteHandler),
    ("/listing/new", HomeListingNewHandler),
    ("/listing/trending", HomeListingTrendingHandler),
    ("/listing/top", HomeListingTopHandler),
    ("/listing/(\w+)/new", SubpageListingNewHandler),
    ("/listing/(\w+)/trending", SubpageListingTrendingHandler),
    ("/listing/(\w+)/top", SubpageListingTopHandler),
    ("/search", SearchHandler),
    ("/user/(\d+)", ProfileHandler),
    ("/user/(\d+)/slogans", ProfileSlogansHandler),
    ("/user/(\d+)/top-slogans", ProfileTopSlogansHandler),
    ("/user/(\d+)/comments", ProfileCommentsHandler),
    ("/user/(\d+)/slogarama", SlogaramaHandler),
    ("/my-profile", MyProfileHandler),
    ("/my-profile/slogarama", MyProfileSlogaramaHandler),
    ("/create-profile", CreateProfileHandler),
    ("/slogan/(\d+)", SloganHandler),
    ("/slogan/(\d+)/share", SloganHandler),
    ("/slogan/(\d+)/comments", SloganCommentsHandler),
    ("/addComment", SloganCommentsHandler),
    ("/addSlogan", AddSloganHandler),
    ("/deleteSlogan", DeleteSloganHandler),
], debug=True)
application.error_handlers[404] = handle_404
#application.error_handlers[500] = handle_500
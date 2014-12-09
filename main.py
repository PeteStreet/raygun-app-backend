import os
import logging
import webapp2
import time

import models

from google.appengine.api import app_identity
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

import jinja2

template_path = os.path.join(os.path.dirname(__file__))

jinja2_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_path),
    autoescape=True
)


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

        template_values = {"sloganRows": sloganRows, "whichListing": "HOME NEW"}
        template = jinja2_env.get_template('html/listing.html')
        self.response.out.write(template.render(template_values))

class HomeListingTrendingHandler(Handler):
    def get(self):
        # get the 30 top trending slogans globally.
        sloganRows = models.slogan.gql('ORDER BY temporalRank DESC limit 30').fetch()

        template_values = {"sloganRows": sloganRows, "whichListing": "HOME TRENDING"}
        template = jinja2_env.get_template('html/listing.html')
        self.response.out.write(template.render(template_values))

class HomeListingTopHandler(Handler):
    def get(self):
        # get the 30 all-time top slogans globally.
        sloganRows = models.slogan.gql('ORDER BY globalRank DESC LIMIT 30').fetch()

        template_values = {"sloganRows": sloganRows, "whichListing": "HOME TOP"}
        template = jinja2_env.get_template('html/listing.html')
        self.response.out.write(template.render(template_values))


class SubpageListingNewHandler(Handler):
    def get(self, subpage):
        # get the 30 newest slogans for a specific subpage
        #sloganRows = models.slogan.gql('WHERE :subpage IN (subpageTag1, subpageTag2) ORDER BY createdAt LIMIT 30').fetch()
        sloganRows = models.slogan.gql('ORDER BY createdAt LIMIT 30').fetch()

        template_values = {"sloganRows": sloganRows, "whichListing": "SUBPAGE " + subpage + " NEW"}
        template = jinja2_env.get_template('html/listing.html')
        self.response.out.write(template.render(template_values))

class SubpageListingTrendingHandler(Handler):
    def get(self, subpage):
        # get the 30 top trending slogans for a specific subpage
        #sloganRows = models.slogan.gql('WHERE :subpage IN (subpageTag1, subpageTag2) ORDER BY temporalRank LIMIT 30').fetch()
        sloganRows = models.slogan.gql('ORDER BY temporalRank LIMIT 30').fetch()

        template_values = {"sloganRows": sloganRows, "whichListing": "SUBPAGE " + subpage + " TRENDING"}
        template = jinja2_env.get_template('html/listing.html')
        self.response.out.write(template.render(template_values))

class SubpageListingTopHandler(Handler):
    def get(self, subpage):
        # get the 30 all-time top slogans for a specific subpage
        #sloganRows = models.slogan.gql('WHERE :subpage IN (subpageTag1, subpageTag2) ORDER BY globalRank LIMIT 30').fetch()
        sloganRows = models.slogan.gql('ORDER BY globalRank LIMIT 30').fetch()

        template_values = {"sloganRows": sloganRows, "whichListing": "SUBPAGE " + subpage + " TOP"}
        template = jinja2_env.get_template('html/listing.html')
        self.response.out.write(template.render(template_values))


class SearchHandler(Handler):
    def get(self):
        asdf = 0


class ProfileHandler(Handler):
    def get(self, profile_id):
        #general method for displaying a user profile
        userRows = models.user.gql('')
        userSloganRows = []
        userExists = False
        isCurrentUser = False

        for uRow in userRows:
            if uRow.key.id() == int(profile_id): # The specific user's profile
                userExists = True
                if uRow.uniqueGivenID == users.get_current_user().user_id():
                    isCurrentUser = True

                sloganRows = models.slogan.gql('ORDER BY createdAt DESC')
                for sRow in sloganRows:
                    if sRow.uniqueAuthorID == uRow.key.id(): # If the user wrote this slogan
                        userSloganRows.append(sRow)

                template = jinja2_env.get_template('html/profile.html')
                template_values = {"uRow": uRow, "sloganRows": userSloganRows, "isCurrentUser": isCurrentUser}
                self.response.out.write(template.render(template_values))
                break

        if not userExists:
            #self.response.out.write("Create yourself a profile")
            self.redirect("/create-profile")




        '''userRows = models.user.gql('').fetch()
        poemRows = poem.gql('ORDER BY createdAt DESC').fetch()
        followRows = follow.gql('').fetch()
        currentUser = users.get_current_user().user_id()

        isCurrentUser = False
        numPoems = 0
        numFollowers = 0
        numFollowing = 0
        isFollowing = False #if the current user is following this profile, the "follow" button will be changed on the profile page.

        userExists = False
        for uRow in userRows:
            if uRow.key.id() == int(profile_id): #The specific user's profile

                #send the user to the unique "my profile" page if they are going to their own profile
                if uRow.uniqueUserID == currentUser:
                    isCurrentUser = True
                    #template = jinja2_env.get_template('html/my-profile.html')

                #find all of the poems written by this user
                for pRow in poemRows:
                    if pRow.uniqueUserID == uRow.uniqueUserID: #if the uniqueUserIDs of the poem and current user match
                        numPoems += 1

                #find all the followers/followees of this user
                for fRow in followRows:
                    if fRow.followingID == uRow.uniqueUserID:
                        numFollowers += 1
                    if fRow.followerID == uRow.uniqueUserID:
                        numFollowing += 1
                    if fRow.followerID == currentUser and fRow.followingID == uRow.uniqueUserID:
                        isFollowing = True

                template = jinja2_env.get_template('html/profile.html')
                template_values = {"uRow": uRow, "isCurrentUser": isCurrentUser,
                                   "numPoems": numPoems, "numFollowers": numFollowers, "numFollowing": numFollowing, "isFollowing": isFollowing}
                self.response.out.write(template.render(template_values))
                userExists = True;
                break;

        if not userExists:
            self.redirect("/create-profile")'''

class MyProfileHandler(Handler):
    def get(self):
        asdf = 2
        '''#specific method for redirecting to the current user's profile
        userRows = user.gql('').fetch()
        currentUser = users.get_current_user().user_id()

        userExists = False
        for uRow in userRows:
            if uRow.uniqueUserID == currentUser:
                userExists = True
                redirString = "/user/" + str(uRow.key.id()) + "/me"
                self.redirect(redirString)

        if not userExists:
            self.redirect("/create-profile")'''

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
        sloganRows = models.slogan.gql('')
        sloganExists = False
        for sRow in sloganRows:
            if sRow.key.id() == int(slogan_id):
                commentRows = models.comment.gql('ORDER BY createdAt DESC')
                comments = []
                commentCounter = 0 #this limits how many comments are shown on the slogan page.
                for cRow in commentRows:
                    if cRow.uniqueSloganID == int(slogan_id) and commentCounter < 2:
                        comments.append(cRow)
                        commentCounter += 1
                    elif commentCounter >= 2:
                        break


                template_values = {"sRow": sRow, "comments": comments}
                template = jinja2_env.get_template('html/slogan.html')
                self.response.out.write(template.render(template_values))
                sloganExists = True
                break;

        if not sloganExists:
            self.response.out.write("This slogan doesn't exist!")


class SloganCommentsHandler(Handler):
    def get(self, slogan_id):
        commentRows = models.comment.gql('ORDER BY createdAt DESC')
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

        userRows = models.user.gql('').fetch()
        currentUser = users.get_current_user().user_id()
        userNickname = ""
        commentAuthorID = 0
        for uRow in userRows:
            if uRow.uniqueGivenID == currentUser:
                userNickname = uRow.nickname
                commentAuthorID = uRow.key.id()
                uRow.slogarma += 5 #increment the user's "slogarma" on comments, likes, and posts.

        #increment "numComments" for the slogan.
        sloganRows = models.slogan.gql('')
        for sRow in sloganRows:
            if sRow.key.id() == int(uniqueSloganID):
                sRow.numComments += 1
                sRow.put()

        #create a new comment entity.
        c = models.comment(uniqueAuthorID = commentAuthorID, uniqueSloganID = int(uniqueSloganID),
                           userNickname = userNickname, text = commentText)
        c.put()

        self.redirect("/slogan/" + uniqueSloganID + "/comments")


class AddSloganHandler(Handler, blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        template_values = {}
        template = jinja2_env.get_template('html/add-slogan.html')
        self.response.out.write(template.render(template_values))

    def post(self):
        if True:
            #posting a new slogan
            sloganText = self.request.get('slogan_text')

            #if the user is logged in (posting from a web browser), use their id:
            if users.get_current_user():
                currentUser = users.get_current_user().user_id()

                userRows = models.user.gql('')
                for uRow in userRows:
                    if uRow.uniqueGivenID == currentUser:
                        if sloganText:
                            s = models.slogan(uniqueAuthorID = uRow.key.id(), authorNickname = uRow.nickname,
                                              numComments = 0, numLikes = 0, numDislikes = 0, text = sloganText)
                            sloganID = s.put().id() #put the slogan in the datastore
                            #send us back to the poem page, and from there we can poll for recordings.

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



class CreateProfileHandler(Handler):
    def get(self):
        template = jinja2_env.get_template('html/create-profile.html')
        self.response.out.write(template.render())

    def post(self):
        newUserNickname = self.request.get('username')
        userEmail = self.request.get('email')
        userBio = self.request.get('user_bio')

        #check to see if the userNickname provided is unique
        userRows = models.user.gql('')
        isUniqueUsername = True
        for uRow in userRows:
            if uRow.nickname == newUserNickname:
                isUniqueUsername = False

        if isUniqueUsername:
            currentUser = users.get_current_user().user_id()

            u = models.user(uniqueGivenID = currentUser, nickname = newUserNickname,
                            email = userEmail, bio = userBio, numSlogans = 0)
            u.put()

            self.redirect("/listing/new")

        else:
            error = "That username already exists!  Please pick a different one."
            template = jinja2_env.get_template('html/create-profile.html')
            template_values = {"error": error}
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
    ("/my-profile", MyProfileHandler),
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
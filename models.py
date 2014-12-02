__author__ = 'Alex P'

from google.appengine.ext import ndb

class user(ndb.Model):
    uniqueGivenID = ndb.StringProperty() #good for checking isCurrentUser.
    nickname = ndb.StringProperty()
    picture = ndb.BlobProperty()
    numSlogans = ndb.IntegerProperty()
    bio = ndb.TextProperty()
    createdAt = ndb.DateTimeProperty(auto_now_add=True)

class slogan(ndb.Model):
    uniqueAuthorID = ndb.IntegerProperty(required=True) #key.id()
    authorNickname = ndb.StringProperty()
    authorThumbnail = ndb.BlobProperty()
    text = ndb.StringProperty(required=True)
    highlightedSection = ndb.StringProperty()
    subpageTag1 = ndb.StringProperty()
    subpageTag2 = ndb.StringProperty()
    numComments = ndb.IntegerProperty()
    numLikes = ndb.IntegerProperty()
    numDislikes = ndb.IntegerProperty()
    globalRank = ndb.IntegerProperty()
    temporalRank = ndb.IntegerProperty()
    createdAt = ndb.DateTimeProperty(auto_now_add=True) #argument automatically sets createdAt to the current time.

class comment(ndb.Model):
    uniqueAuthorID = ndb.IntegerProperty(required=True) #key.id()
    uniqueSloganID = ndb.IntegerProperty(required=True) #key.id()
    userNickname = ndb.StringProperty()
    text = ndb.TextProperty()
    parentCommentID = ndb.IntegerProperty() #this will hold a key.id() of another comment if it is a reply
    createdAt = ndb.DateTimeProperty(auto_now_add=True)

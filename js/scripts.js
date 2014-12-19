/**
 * Created by Alex P on 12/17/2014.
 * AJAX example adapted from here: http://stackoverflow.com/questions/22052013/how-to-use-ajax-with-google-app-engine-python
 */
function VoteUp(sloganKey){
    $.ajax({
        type: "POST",
        url: "/upvote/",
        data: JSON.stringify({ "sloganKey": sloganKey})
    });
}
function VoteDown(sloganKey){
    $.ajax({
        type: "POST",
        url: "/downvote/",
        data: JSON.stringify({ "sloganKey": sloganKey})
    });
}

/*Really, this should also remove voting functionality from the complementary button on the slogan listing as well. */
$('.vote-button').on("click",function() {
    //Increment the vote count on the page immediately
    var numVotes = $(this).children("span").text();
    $(this).children("span").text(parseInt(numVotes) + 1);

    //Only allow the user to vote once.
    var content = $(this).contents();
    $(this).replaceWith(content);
});
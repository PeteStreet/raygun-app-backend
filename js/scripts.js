/**
 * Created by Alex P on 12/17/2014.
 * AJAX example adapted from here: http://stackoverflow.com/questions/22052013/how-to-use-ajax-with-google-app-engine-python
 */
function VoteUp(sloganKey){
    $.ajax({
        type: "POST",
        url: "/app/upvote/",
        data: JSON.stringify({ "sloganKey": sloganKey})
    });
}
function VoteDown(sloganKey){
    $.ajax({
        type: "POST",
        url: "/app/downvote/",
        data: JSON.stringify({ "sloganKey": sloganKey})
    });
}
/*Really, this should also remove voting functionality from the complementary button on the slogan listing as well. */
$('.vote-up-button').on("click",function() {
    theSloganID = $(this).find("a").attr("title");

    //Increment the vote count on the page immediately
    var numVotes = $(this).find(".vote-number").text();
    $(this).find(".vote-number").text(parseInt(numVotes) + 1);

    //Only allow the user to vote once.
    var content = $(this).contents();
    $(this).replaceWith(content);

    VoteUp(theSloganID); //can we get a retun value from here, so that the number isn't incremented if the vote is cancelled?
});
$('.vote-down-button').on("click",function() {
    theSloganID = $(this).find("a").attr("title");

    //Increment the vote count on the page immediately
    var numVotes = $(this).find(".vote-number").text();
    $(this).find(".vote-number").text(parseInt(numVotes) + 1);

    //Only allow the user to vote once.
    var content = $(this).contents();
    $(this).replaceWith(content);

    VoteDown(theSloganID); //can we get a retun value from here, so that the number isn't incremented if the vote is cancelled?
});

/* Limit the number of boxes checked when posting a slogan */
$('input.single-check').on('change', function(evt) {
   if($(this).siblings(':checked').length >= 2) {
       this.checked = false;
   }
});

/* Character counters for input text boxes, borrowed from http://stackoverflow.com/questions/5371089/count-characters-in-textarea/5371160#5371160 */
$('#slogan-add-field').keyup(function () {
  var max = 65;
  var len = $(this).val().length;
  if (len >= max) {
    $('#charNum').text("That's all she wrote");
      return false
  } else {
    var char = max - len;
      if (char > 1) {
        $('#charNum').text(char);
      }
      else {
        $('#charNum').text(char);
      }
  }
});

$('#comment-add-field').keyup(function () {
  var max = 100;
  var len = $(this).val().length;
  if (len >= max) {
    $('#charNum').text("That's all she wrote");
      return false;
  } else {
    var char = max - len;
      if (char > 1) {
        $('#charNum').text(char);
      }
      else {
        $('#charNum').text(char);
      }
  }
});
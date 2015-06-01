// PART 1: SHOW Book results

// function getBookResults(evt) {
//   // evt.preventDefault();
//   // $('#book-search-results-div').empty();
//   // $('#book-search-results-div').load('/search');
//   // var query = $.get('/', '#user_book_query').val();
//   // $("user-location-query").append(query);
//   $.get("/", showBookResults);
//   }


// function showBookResults(evt) {
//   $.get("/search", function(results){
//       for (book in results) {
//         console.log(book);
//         $("#book-result-div").append("<div><a href=" + book.previewLink + ">" + "<img src=" + book.thumbnailUrl + "></a>");
//       }
//   }


// $('#book-search-submit-button').on('click', getBookResults).load("/search", showBookResults);



function getBookResults(evt) {
  evt.preventDefault();
  $('#results-div').empty();
  $('#book-result-div').empty();    

  var url = "/search?" + $('#user_book_query').serialize();

  $.get(url, function(json) {
    console.log(json.name);
    $("#results-div").append("<div class='container'><p>Found " + json.name.length + " books associated with " + $("#search-input").val() + ".</p></div>");
    // $("#user-location-query").append($("#user_book_query").val());
    for (var book=0; book <json.name.length; book++) {
    //     console.log(book);
        $("#book-result-div").append("<div class='container'><div class='jumbotron'><img id='bookcover' src='" + json.name[book].thumbnailUrl + "'></div></div>");
        

      }
      $(".jumbotron").click(function() {
    console.log("hello")
   // $('#imagepreview').attr('src', $('#bookcover').attr('src'));
   $('#imagemodal').show();
   
});

  });

}


//       $( ".jumbotron" ).click(function() {
//   alert( "Handler for .click() called." );
// });


// //Modal
// function getBookModal(evt) {

//   var url = "/search?" + $('#user_book_query').serialize();

//   $.get(url, function(json) {
//   for (var book=0; book <json.name.length; book++) {
//   $("#book-result-div").on("click", function() {
//   $('#myModalLabel').append(json.name[book].title);
//   $('#imagepreview').attr('src', $('#bookcover').attr('src'));
//   $('#author').append("Author: " + json.name[book].authors);
//   $('#description').append("Description: " + json.name[book].description);
//   $('#imagemodal').modal('show');
//   });
// }


// $("#book-result-div").on("click", getBookModal);


$(document).ready(function () {
  $('#user_book_query').on('submit', getBookResults);
})

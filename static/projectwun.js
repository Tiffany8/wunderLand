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

  $.get(url, function(json) { // both


    $("#results-div").append("<div class='container'><p>Found " + json.name.length + " books associated with " + $("#search-input").val() + ".</p></div>"); //json result callback

    for (var book=0; book <json.name.length; book++) {
        if (book%3===0) {
          $("#book-result-div").append("<div class='row'><div class='col-md-4'><a data-toggle='modal' data-target='#myModal' href='#'><img id='" + json.name[book].isbn + "' class='book-thumbnail' src='" + json.name[book].thumbnailUrl + "'></a></div>");
        } else if (book%3===2) {
          $("#book-result-div").append("<div class='col-md-4'><a data-toggle='modal' data-target='#myModal' href='#'><img id='" + json.name[book].isbn + "' class='book-thumbnail' src='" + json.name[book].thumbnailUrl + "'></a></div></div>"); 
        } else {
          $("#book-result-div").append("<div class='col-md-4'><a data-toggle='modal' data-target='#myModal' href='#'><img id='" + json.name[book].isbn + "' class='book-thumbnail' src='" + json.name[book].thumbnailUrl + "'></a></div>"); 
        }
        
            // data-toggle="modal" data-target="#exampleModal" data-whatever="@mdo"

      // $('#myModalLabel').append(json.name[book].title);
      // $('#imagepreview').attr('src', $('#bookcover').attr('src'));
      // $('#author').append("Author: " + json.name[book].authors);
      // $('#description').append("Description: " + json.name[book].description);

    }
  });
}
// create a function that is tied to the creation of the thumbnail --- what's going to change is that book's personal info
// clear the div at the beginning of the function 

function getKMeansResults(evt) {
  evt.preventDefault();
  $('#results-div').empty();
  $('#book-result-div').empty();    

  var url = "/search/kmeans?" + $('#user_book_query').serialize();

  $.get(url, function(json) { // both

      
      $("#kmeans_graph").append(json.kmeans); // kmeans result callback
    
  });
}


$(document).ready(function () {
  $('#user_book_query').on('submit', getBookResults);
  $('#user_book_query').on('submit', getKMeansResults)
  $('#books').tab('show')
  // $("#book-thumbnail").on('click', function () { $('#myModal').modal("show")});
  $('#myTab a:first').click(function (e) {
    e.preventDefault()
    $(this).tab('show')
  });

  $('#myTab a:last').click(function (e) {
    e.preventDefault()
    $(this).tab('show')
  });

  // The timer for the loading screen - starts 1000 ms after call
  $(document).ajaxStart(function () {
      timer = setTimeout(function () {
        $("#loaderthingy").show();
      }, 1000);
  });

  $(document).ajaxComplete(function () {
      $("#loaderthingy").hide();
      clearTimeout(timer);
  });

   
  // $("#book-thumbnail").on('click', function() {
  //   $('#myModal').modal('show');
  // });
  // $("#book-thumbnail").modal("show");

})


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


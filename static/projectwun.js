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
    $("#results-div").append("<p>Found " + json.name.length + " books associated with " + $("#search-input").val() + ".</p>");
    // $("#user-location-query").append($("#user_book_query").val());
    for (var book=0; book <json.name.length; book++) {
    //     console.log(book);
        $("#book-result-div").append("<div><a href='" + json.name[book].previewLink + "' target='_blank'>" + "<img src='" + json.name[book].thumbnailUrl + "'></a>");
      }
  });

}

$('#user_book_query').on('submit', getBookResults);
//PAR 2: SHOW number of books and user query

// function showBookNumber(evt) {
//
// }
//
// function showWeather(evt) {
//     evt.preventDefault();
//     $('#weather-info').empty();
//
//     var url = "/weather?zipcode=" + $("#zipcode-field").val();
//     $.get(url, function(data){
//        for (item in data){
//             $('#weather-info').append("<p><b>" + item.toUpperCase() + ":</b> " + data[item] + "</p>");
//         }
//     });
// }
//
// $("#weather-form").on('submit', showWeather);

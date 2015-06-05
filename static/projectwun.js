// PART 1: SHOW Book results


function getBookResults(evt) {
  evt.preventDefault();
  $('#results-div').empty();
  $('#book-result-div').empty();    

  var url = "/search?" + $('#user_book_query').serialize();

  $.get(url, function(json) { 


    $("#results-div").append("<div class='container'><p>Found " + json.name.length + " books associated with " + $("#search-input").val() + ".</p></div>"); 

    for (var book=0; book <json.name.length; book++) {
        if (book%3===0) {
          $("#book-result-div").append("<div class='row'><div class='col-md-4'><a data-toggle='modal' data-target='#myModal' href='#'><img id='" + json.name[book].isbn + "' class='book-thumbnail' data-title='" + json.name[book].title + "' data-keywords='" + json.name[book].keywords + "' src='" + json.name[book].thumbnailUrl + "'></a></div>");
        } else if (book%3===2) {
          $("#book-result-div").append("<div class='col-md-4'><a data-toggle='modal' data-target='#myModal' href='#'><img id='" + json.name[book].isbn + "' class='book-thumbnail' data-title='" + json.name[book].title + "' data-keywords='" + json.name[book].keywords + "' src='" + json.name[book].thumbnailUrl + "'></a></div></div>"); 
        } else {
          $("#book-result-div").append("<div class='col-md-4'><a data-toggle='modal' data-target='#myModal' href='#'><img id='" + json.name[book].isbn + "' class='book-thumbnail' data-title='" + json.name[book].title + "' data-keywords='" + json.name[book].keywords + "' src='" + json.name[book].thumbnailUrl + "'></a></div>"); 
        }
        
      $(".book-thumbnail").click(function() {
        $('.book-title').empty();
        $('.book-keywords').empty();
        $(".book-keywords").append($(this).data("keywords"));
        $(".book-title").append($(this).data("title"));
      });
    }
  });
}




function getModalInfoForEachBook(evt) {
  console.log("something there")
  $('.book-title').empty();
  $('.book-keywords').empty();

  var url='/search?' + $('#user_book_query').serialize();

  $.get(url, function(json) {
    console.log(json)
  })
}


function getKMeansResults(evt) {
  evt.preventDefault();
  $('#results-div').empty();
  $('#book-result-div').empty();
  $('#kmeans_graph').empty();    

  var url = "/search/kmeans?" + $('#user_book_query').serialize();

  $.get(url, function(json) { 
    $("#kmeans_graph").append(json.kmeans); 
  });
}


$(document).ready(function () {
  $('#user_book_query').on('submit', getBookResults);
  $('#user_book_query').on('submit', getKMeansResults)
  $('#books').tab('show')

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
})


